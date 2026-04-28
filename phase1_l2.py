import time

from config_data import (
    ACCESS_PORTS,
    ACCESS_SWITCHES,
    ACCESS_SWITCH_MGMT_IPS,
    ACCESS_TRUNKS,
    CORE_SWITCHES,
    CORE_TRUNKS,
    EC_MEMBERS,
    MANAGEMENT_GATEWAY,
    MANAGEMENT_VLAN,
    MASK_24,
    PORT_CHANNEL_ID,
    TRUNK_ALLOWED,
    VLANS,
)
from common import connect, push_config, run_exec, save_config, check_ssh


def vlan_database_commands():
    cmds = ["vlan database"]

    for vlan_id, name in VLANS.items():
        cmds.append(f"vlan {vlan_id} name {name}")

    cmds.append("exit")
    return cmds


def trunk_allowed_command():
    # Esta imagen IOS requiere "add" para no borrar VLANs permitidas existentes.
    return f"switchport trunk allowed vlan add {TRUNK_ALLOWED}"


def get_etherchannel_members(sw_name: str):
    """
    Devuelve los puertos EtherChannel específicos por switch.
    Solo SWML1 y SWML2 deben tener EtherChannel.
    """
    return EC_MEMBERS.get(sw_name, [])


def trunk_commands(sw_name: str):
    """
    Configura trunks normales.
    No toca los puertos que hacen parte del EtherChannel.
    """
    trunks = CORE_TRUNKS.get(sw_name, []) + ACCESS_TRUNKS.get(sw_name, [])
    ec_members = set(get_etherchannel_members(sw_name))

    cmds = []

    for intf, description in trunks:
        if intf in ec_members:
            print(f"[SKIP] {sw_name} {intf} es miembro de EtherChannel. No se configura como trunk individual.")
            continue

        cmds.extend([
            f"interface {intf}",
            f"description {description}",
            "switchport",
            "switchport mode trunk",
            trunk_allowed_command(),
            "no shutdown",
            "exit",
        ])

    return cmds


def etherchannel_commands(sw_name: str):
    """
    Configura EtherChannel solamente en SWML1 y SWML2.
    """
    members = get_etherchannel_members(sw_name)

    if not members:
        return []

    cmds = []

    cmds.extend([
        f"interface Port-channel{PORT_CHANNEL_ID}",
        "description PO_TO_PEER_SWML",
        "switchport",
        "switchport mode trunk",
        trunk_allowed_command(),
        "no shutdown",
        "exit",
    ])

    for intf in members:
        cmds.extend([
            f"interface {intf}",
            "description EC_MEMBER_TO_PEER_SWML",
            "switchport",
            "switchport mode trunk",
            trunk_allowed_command(),
            f"channel-group {PORT_CHANNEL_ID} mode on",
            "no shutdown",
            "exit",
        ])

    return cmds


def access_port_commands(sw_name: str):
    cmds = []

    for intf, vlan_id, endpoint in ACCESS_PORTS.get(sw_name, []):
        cmds.extend([
            f"interface {intf}",
            f"description ACCESS_TO_{endpoint}",
            "switchport",
            "switchport mode access",
            f"switchport access vlan {vlan_id}",
            "spanning-tree portfast",
            "no shutdown",
            "exit",
        ])

    return cmds


def access_switch_mgmt_commands(sw_name: str):
    """
    SWML3 y SWML4 quedan como L2.
    Solo tienen SVI de gestión en VLAN 90.
    """
    return [
        "no router ospf 1",
        "no service dhcp",
        "no ip routing",
        f"interface Vlan{MANAGEMENT_VLAN}",
        "description MGMT_ONLY",
        f"ip address {ACCESS_SWITCH_MGMT_IPS[sw_name]} {MASK_24}",
        "no shutdown",
        "exit",
        f"ip default-gateway {MANAGEMENT_GATEWAY}",
    ]


def main():
    devices = CORE_SWITCHES + ACCESS_SWITCHES

    print("\n========== PRE-CHECK SSH ==========")

    failed = []

    for device_name in devices:
        if not check_ssh(device_name):
            failed.append(device_name)

    if failed:
        print("\n[STOP] No se puede iniciar fase 1.")
        print(f"Equipos sin SSH: {failed}")
        print("Corrige conectividad antes de modificar la red.")
        return

    print("\n[OK] Todos los switches responden por SSH. Iniciando fase 1...")

    for device_name in devices:
        print(f"\n==================== {device_name} ====================")

        conn = connect(device_name)

        try:
            run_exec(conn, vlan_database_commands(), f"VLAN database - {device_name}")
            time.sleep(2)

            push_config(conn, trunk_commands(device_name), f"Trunks - {device_name}")
            time.sleep(4)

            if device_name in CORE_SWITCHES:
                push_config(conn, etherchannel_commands(device_name), f"EtherChannel - {device_name}")
                time.sleep(8)

            if device_name in ACCESS_SWITCHES:
                push_config(conn, access_port_commands(device_name), f"Access ports - {device_name}")
                time.sleep(4)

                push_config(conn, access_switch_mgmt_commands(device_name), f"Management SVI - {device_name}")
                time.sleep(4)

            save_config(conn)
            time.sleep(5)

        finally:
            conn.disconnect()

    print("\n[OK] Fase 1 finalizada.")

if __name__ == "__main__":
    main()