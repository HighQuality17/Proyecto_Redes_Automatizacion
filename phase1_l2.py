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
    SWML1_ACTIVE_VLANS,
    SWML2_ACTIVE_VLANS,
    TRUNK_ALLOWED,
    VLANS,
)
from common import connect, push_config, run_exec, save_config


def vlan_database_commands():
    cmds = ["vlan database"]
    for vlan_id, name in VLANS.items():
        cmds.append(f"vlan {vlan_id} name {name}")
    cmds.append("exit")
    return cmds


def trunk_commands(sw_name: str):
    trunks = CORE_TRUNKS.get(sw_name, []) + ACCESS_TRUNKS.get(sw_name, [])
    cmds = []
    for intf, description in trunks:
        cmds.extend([
            f"interface {intf}",
            f"description {description}",
            "switchport",
            "switchport mode trunk",
            f"switchport trunk allowed vlan {TRUNK_ALLOWED}",
            "no shutdown",
            "exit",
        ])
    return cmds


def etherchannel_commands():
    cmds = [
        f"interface Port-channel{PORT_CHANNEL_ID}",
        "description PO_TO_PEER_SWML",
        "switchport",
        "switchport mode trunk",
        f"switchport trunk allowed vlan {TRUNK_ALLOWED}",
        "no shutdown",
        "exit",
    ]
    for intf in EC_MEMBERS:
        cmds.extend([
            f"interface {intf}",
            "description EC_MEMBER_TO_PEER_SWML",
            "switchport",
            "switchport mode trunk",
            f"switchport trunk allowed vlan {TRUNK_ALLOWED}",
            f"channel-group {PORT_CHANNEL_ID} mode on",
            "no shutdown",
            "exit",
        ])
    return cmds


def stp_commands(sw_name: str):
    if sw_name == "SWML1":
        primary = ",".join(map(str, sorted(SWML1_ACTIVE_VLANS)))
        secondary = ",".join(map(str, sorted(SWML2_ACTIVE_VLANS)))
    else:
        primary = ",".join(map(str, sorted(SWML2_ACTIVE_VLANS)))
        secondary = ",".join(map(str, sorted(SWML1_ACTIVE_VLANS)))

    return [
        f"spanning-tree vlan {primary} priority 4096",
        f"spanning-tree vlan {secondary} priority 8192",
    ]


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
            "spanning-tree bpduguard enable",
            "no shutdown",
            "exit",
        ])
    return cmds


def access_switch_mgmt_commands(sw_name: str):
    # SWML3/SWML4 stay L2-only: no HSRP, no OSPF, no DHCP; only Vlan90 SVI.
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
    for device_name in CORE_SWITCHES + ACCESS_SWITCHES:
        print(f"\n==================== {device_name} ====================")
        conn = connect(device_name)
        try:
            run_exec(conn, vlan_database_commands(), f"VLAN database - {device_name}")
            push_config(conn, trunk_commands(device_name), f"Trunks - {device_name}")
            if device_name in CORE_SWITCHES:
                push_config(conn, etherchannel_commands(), f"EtherChannel - {device_name}")
                push_config(conn, stp_commands(device_name), f"STP - {device_name}")
            else:
                push_config(conn, access_port_commands(device_name), f"Access ports - {device_name}")
                push_config(conn, access_switch_mgmt_commands(device_name), f"Management SVI - {device_name}")
            save_config(conn)
        finally:
            conn.disconnect()


if __name__ == "__main__":
    main()
