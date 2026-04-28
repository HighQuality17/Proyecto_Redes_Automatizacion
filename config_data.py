SSH_USER = "admin"
SSH_PASS = "cisco123"
DOMAIN_NAME = "lab.local"

# VLAN 70 / DMZ is physical-only behind EDGE-FISICO. Do not create it in GNS3.
VLANS = {
    10: "Desarrollo",
    20: "QA",
    30: "Soporte_Admin",
    40: "Ventas",
    50: "TI_Operaciones",
    60: "Servidores",
    90: "Gestion",
}

CORE_SWITCHES = ["SWML1", "SWML2"]
ACCESS_SWITCHES = ["SWML3", "SWML4"]
FIREWALLS = ["FW1", "FW2"]
OSPF_DEVICES = CORE_SWITCHES + FIREWALLS

MANAGEMENT_VLAN = 90
MANAGEMENT_GATEWAY = "10.10.90.2"
ACCESS_SWITCH_MGMT_IPS = {
    "SWML3": "10.10.90.4",
    "SWML4": "10.10.90.5",
}

DHCP_VLANS = [10, 20, 30, 40, 50]

# VIP .1 / SWML1 .2 / SWML2 .3
VLAN_GATEWAYS = {
    10: ("10.10.10.1", "10.10.10.2", "10.10.10.3"),
    20: ("10.10.20.1", "10.10.20.2", "10.10.20.3"),
    30: ("10.10.30.1", "10.10.30.2", "10.10.30.3"),
    40: ("10.10.40.1", "10.10.40.2", "10.10.40.3"),
    50: ("10.10.50.1", "10.10.50.2", "10.10.50.3"),
    60: ("10.10.60.1", "10.10.60.2", "10.10.60.3"),
    90: ("10.10.90.1", "10.10.90.2", "10.10.90.3"),
}

# HSRP / STP alignment
SWML1_ACTIVE_VLANS = {10, 20, 30, 90}
SWML2_ACTIVE_VLANS = {40, 50, 60}

# EtherChannel between SWML1 and SWML2
PORT_CHANNEL_ID = 1

EC_MEMBERS = {
    "SWML1": ["FastEthernet1/4", "FastEthernet1/5"],
    "SWML2": ["FastEthernet1/4", "FastEthernet1/5"],
}

TRUNK_ALLOWED = "10,20,30,40,50,60,90"

CORE_TRUNKS = {
    "SWML1": [
        ("FastEthernet1/3", "TRUNK_TO_SWML3"),
        ("FastEthernet1/1", "TRUNK_TO_SWML4"),
    ],
    "SWML2": [
        ("FastEthernet1/1", "TRUNK_TO_SWML3"),
        ("FastEthernet1/3", "TRUNK_TO_SWML4"),
    ],
}

# SWML3/SWML4 Fa0/0 is not used for L2 trunks because it does not support switchport.
ACCESS_TRUNKS = {
    "SWML3": [
        ("FastEthernet1/6", "TRUNK_TO_SWML1"),
        ("FastEthernet1/1", "TRUNK_TO_SWML2"),
    ],
    "SWML4": [
        ("FastEthernet1/1", "TRUNK_TO_SWML1"),
        ("FastEthernet1/5", "TRUNK_TO_SWML2"),
    ],
}

ACCESS_PORTS = {
    "SWML3": [
        ("FastEthernet1/4", 10, "PC1"),
        ("FastEthernet1/3", 20, "PC2"),
        ("FastEthernet1/2", 30, "PC3"),
        ("FastEthernet1/5", 90, "NetworkAutomation-1_eth0"),
    ],
    "SWML4": [
        ("FastEthernet1/2", 40, "PC4"),
        ("FastEthernet1/3", 50, "PC5"),
        ("FastEthernet1/4", 60, "PC6"),
    ],
}

# L3 links
SWML1_TO_FW1_IF = "FastEthernet1/2"
SWML1_TO_FW1_IP = "10.10.254.2"
FW1_TO_SWML1_IF = "FastEthernet0/0"
FW1_TO_SWML1_IP = "10.10.254.1"

SWML2_TO_FW2_IF = "FastEthernet1/2"
SWML2_TO_FW2_IP = "10.10.254.18"
FW2_TO_SWML2_IF = "FastEthernet0/0"
FW2_TO_SWML2_IP = "10.10.254.17"

FW1_TO_FW2_IF = "FastEthernet1/0"
FW1_TO_FW2_IP = "10.10.254.33"
FW2_TO_FW1_IF = "FastEthernet1/0"
FW2_TO_FW1_IP = "10.10.254.34"

MASK_24 = "255.255.255.0"
MASK_30 = "255.255.255.252"

OSPF_RIDS = {
    "SWML1": "1.1.1.1",
    "SWML2": "2.2.2.2",
    "FW1": "5.5.5.5",
    "FW2": "6.6.6.6",
}

# Hybrid exit
FW1_OUTSIDE_IF = "FastEthernet1/1"
FW1_OUTSIDE_IP = "192.168.100.3"
FW1_OUTSIDE_MASK = "255.255.255.0"
EDGE_FISICO_NEXT_HOP = "192.168.100.1"

# Physical DMZ route. VLAN 70 is not configured inside GNS3.
DMZ_NETWORK = "10.10.70.0"
DMZ_MASK = "255.255.255.0"

# NAT: only non-overlapping hybrid-side networks.
NAT_INSIDE_NETWORKS = [
    "10.10.20.0 0.0.0.255",
    "10.10.40.0 0.0.0.255",
    "10.10.50.0 0.0.0.255",
    "10.10.60.0 0.0.0.255",
]
