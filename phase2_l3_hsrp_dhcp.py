from config_data import (
    CORE_SWITCHES,
    DHCP_VLANS,
    MASK_24,
    MASK_30,
    SWML1_ACTIVE_VLANS,
    SWML1_TO_FW1_IF,
    SWML1_TO_FW1_IP,
    SWML2_ACTIVE_VLANS,
    SWML2_TO_FW2_IF,
    SWML2_TO_FW2_IP,
    VLAN_GATEWAYS,
)
from common import connect, push_config, save_config


def build_swml_uplink(sw_name: str):
    if sw_name == "SWML1":
        return [
            f"interface {SWML1_TO_FW1_IF}",
            "description L3_TO_FW1",
            "no switchport",
            f"ip address {SWML1_TO_FW1_IP} {MASK_30}",
            "no shutdown",
            "exit",
        ]
    return [
        f"interface {SWML2_TO_FW2_IF}",
        "description L3_TO_FW2",
        "no switchport",
        f"ip address {SWML2_TO_FW2_IP} {MASK_30}",
        "no shutdown",
        "exit",
    ]


def build_hsrp_svis(sw_name: str):
    cmds = ["ip routing"]
    for vlan_id, (vip, sw1_ip, sw2_ip) in VLAN_GATEWAYS.items():
        local_ip = sw1_ip if sw_name == "SWML1" else sw2_ip
        active_vlans = SWML1_ACTIVE_VLANS if sw_name == "SWML1" else SWML2_ACTIVE_VLANS
        priority = 110 if vlan_id in active_vlans else 90

        cmds.extend([
            f"interface Vlan{vlan_id}",
            f"ip address {local_ip} {MASK_24}",
            f"standby {vlan_id} ip {vip}",
            f"standby {vlan_id} priority {priority}",
            f"standby {vlan_id} preempt",
            "no shutdown",
            "exit",
        ])
    return cmds


def build_dhcp_swml1():
    cmds = ["service dhcp"]
    for vlan_id in DHCP_VLANS:
        vip, _, _ = VLAN_GATEWAYS[vlan_id]
        octets = vip.split(".")
        prefix = ".".join(octets[:3])
        network = f"{prefix}.0"

        cmds.extend([
            f"ip dhcp excluded-address {prefix}.1 {prefix}.49",
            f"ip dhcp excluded-address {prefix}.201 {prefix}.254",
            f"ip dhcp pool VLAN{vlan_id}",
            f"network {network} {MASK_24}",
            f"default-router {vip}",
            "dns-server 8.8.8.8",
            "exit",
        ])
    return cmds


def main():
    # Core only. SWML3/SWML4 are L2 access/distribution switches; configured in phase1.
    for device_name in CORE_SWITCHES:
        print(f"\n==================== {device_name} ====================")
        conn = connect(device_name)
        try:
            push_config(conn, build_swml_uplink(device_name), f"Uplink L3 - {device_name}")
            push_config(conn, build_hsrp_svis(device_name), f"SVI + HSRP - {device_name}")
            if device_name == "SWML1":
                push_config(conn, build_dhcp_swml1(), "DHCP - SWML1")
            save_config(conn)
        finally:
            conn.disconnect()


if __name__ == "__main__":
    main()
