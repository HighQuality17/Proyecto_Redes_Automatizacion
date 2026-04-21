from config_data import (
    CORE_SWITCHES,
    DMZ_MASK,
    DMZ_NETWORK,
    EDGE_FISICO_NEXT_HOP,
    FW1_OUTSIDE_IF,
    FW1_OUTSIDE_IP,
    FW1_OUTSIDE_MASK,
    FW1_TO_FW2_IF,
    FW1_TO_FW2_IP,
    FW1_TO_SWML1_IF,
    FW1_TO_SWML1_IP,
    FW2_TO_FW1_IF,
    FW2_TO_FW1_IP,
    FW2_TO_SWML2_IF,
    FW2_TO_SWML2_IP,
    MASK_30,
    NAT_INSIDE_NETWORKS,
    OSPF_RIDS,
    SWML1_TO_FW1_IF,
    SWML2_TO_FW2_IF,
)
from common import connect, push_config, save_config


def build_fw1_interfaces():
    return [
        f"interface {FW1_TO_SWML1_IF}",
        "description L3_TO_SWML1",
        f"ip address {FW1_TO_SWML1_IP} {MASK_30}",
        "ip nat inside",
        "no shutdown",
        "exit",
        f"interface {FW1_TO_FW2_IF}",
        "description L3_TO_FW2",
        f"ip address {FW1_TO_FW2_IP} {MASK_30}",
        "ip nat inside",
        "no shutdown",
        "exit",
        f"interface {FW1_OUTSIDE_IF}",
        "description HYBRID_OUTSIDE_TO_EDGE_FISICO",
        f"ip address {FW1_OUTSIDE_IP} {FW1_OUTSIDE_MASK}",
        "ip nat outside",
        "no shutdown",
        "exit",
    ]


def build_fw2_interfaces():
    return [
        f"interface {FW2_TO_SWML2_IF}",
        "description L3_TO_SWML2",
        f"ip address {FW2_TO_SWML2_IP} {MASK_30}",
        "no shutdown",
        "exit",
        f"interface {FW2_TO_FW1_IF}",
        "description L3_TO_FW1",
        f"ip address {FW2_TO_FW1_IP} {MASK_30}",
        "no shutdown",
        "exit",
    ]


def build_fw1_nat():
    cmds = [
        f"no ip nat inside source list NAT_HIBRIDA interface {FW1_OUTSIDE_IF} overload",
        "no ip access-list standard NAT_HIBRIDA",
        "ip access-list standard NAT_HIBRIDA",
    ]
    for network in NAT_INSIDE_NETWORKS:
        cmds.append(f"permit {network}")
    cmds.extend([
        "exit",
        f"ip nat inside source list NAT_HIBRIDA interface {FW1_OUTSIDE_IF} overload",
        f"ip route {DMZ_NETWORK} {DMZ_MASK} {EDGE_FISICO_NEXT_HOP}",
    ])
    return cmds


def build_fw2_static():
    return [
        # Physical DMZ is reached through FW1. VLAN 70 is not configured in GNS3.
        f"ip route {DMZ_NETWORK} {DMZ_MASK} {FW1_TO_FW2_IP}",
    ]


def build_ospf_swml(sw_name: str):
    rid = OSPF_RIDS[sw_name]
    if sw_name == "SWML1":
        uplink_if = SWML1_TO_FW1_IF
        transit_network = "10.10.254.0 0.0.0.3"
    else:
        uplink_if = SWML2_TO_FW2_IF
        transit_network = "10.10.254.16 0.0.0.3"

    return [
        "router ospf 1",
        f"router-id {rid}",
        "passive-interface default",
        f"no passive-interface {uplink_if}",
        f"network {transit_network} area 0",
        "network 10.10.10.0 0.0.0.255 area 0",
        "network 10.10.20.0 0.0.0.255 area 0",
        "network 10.10.30.0 0.0.0.255 area 0",
        "network 10.10.40.0 0.0.0.255 area 0",
        "network 10.10.50.0 0.0.0.255 area 0",
        "network 10.10.60.0 0.0.0.255 area 0",
        "network 10.10.90.0 0.0.0.255 area 0",
        "exit",
    ]


def build_ospf_fw(fw_name: str):
    rid = OSPF_RIDS[fw_name]
    if fw_name == "FW1":
        return [
            "router ospf 1",
            f"router-id {rid}",
            "passive-interface default",
            f"no passive-interface {FW1_TO_SWML1_IF}",
            f"no passive-interface {FW1_TO_FW2_IF}",
            "network 10.10.254.0 0.0.0.3 area 0",
            "network 10.10.254.32 0.0.0.3 area 0",
            "exit",
        ]
    return [
        "router ospf 1",
        f"router-id {rid}",
        "passive-interface default",
        f"no passive-interface {FW2_TO_SWML2_IF}",
        f"no passive-interface {FW2_TO_FW1_IF}",
        "network 10.10.254.16 0.0.0.3 area 0",
        "network 10.10.254.32 0.0.0.3 area 0",
        "exit",
    ]


def build_swml_static_dmz(sw_name: str):
    next_hop = "10.10.254.1" if sw_name == "SWML1" else "10.10.254.17"
    return [
        f"ip route {DMZ_NETWORK} {DMZ_MASK} {next_hop}",
        f"ip route 192.168.100.0 255.255.255.0 {next_hop}",
    ]


def main():
    # OSPF only runs on SWML1/SWML2/FW1/FW2. NAT only runs on FW1.
    conn = connect("FW1")
    try:
        push_config(conn, build_fw1_interfaces(), "FW1 interfaces")
        push_config(conn, build_fw1_nat(), "FW1 NAT")
        push_config(conn, build_ospf_fw("FW1"), "FW1 OSPF")
        save_config(conn)
    finally:
        conn.disconnect()

    conn = connect("FW2")
    try:
        push_config(conn, build_fw2_interfaces(), "FW2 interfaces")
        push_config(conn, build_fw2_static(), "FW2 static route to DMZ")
        push_config(conn, build_ospf_fw("FW2"), "FW2 OSPF")
        save_config(conn)
    finally:
        conn.disconnect()

    for device_name in CORE_SWITCHES:
        conn = connect(device_name)
        try:
            push_config(conn, build_swml_static_dmz(device_name), f"{device_name} routes to DMZ/hybrid")
            push_config(conn, build_ospf_swml(device_name), f"{device_name} OSPF")
            save_config(conn)
        finally:
            conn.disconnect()


if __name__ == "__main__":
    main()
