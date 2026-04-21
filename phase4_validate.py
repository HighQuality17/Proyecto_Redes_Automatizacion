from inventory import DEPLOY_ORDER
from common import connect


VALIDATION = {
    "SWML1": [
        "show ip interface brief",
        "show vlan-switch brief",
        "show spanning-tree",
        "show standby brief",
        "show ip route",
        "show ip ospf neighbor",
        "show ip dhcp pool",
    ],
    "SWML2": [
        "show ip interface brief",
        "show vlan-switch brief",
        "show spanning-tree",
        "show standby brief",
        "show ip route",
        "show ip ospf neighbor",
    ],
    "SWML3": [
        "show ip interface brief",
        "show vlan-switch brief",
        "show interfaces trunk",
        "show spanning-tree",
        "show running-config interface FastEthernet1/6",
        "show running-config interface FastEthernet1/1",
        "show running-config interface Vlan90",
    ],
    "SWML4": [
        "show ip interface brief",
        "show vlan-switch brief",
        "show interfaces trunk",
        "show spanning-tree",
        "show running-config interface FastEthernet1/1",
        "show running-config interface FastEthernet1/5",
        "show running-config interface Vlan90",
    ],
    "FW1": [
        "show ip interface brief",
        "show ip route",
        "show ip ospf neighbor",
        "show ip nat translations",
        "show ip nat statistics",
    ],
    "FW2": [
        "show ip interface brief",
        "show ip route",
        "show ip ospf neighbor",
    ],
}


def main():
    for device_name in DEPLOY_ORDER:
        print(f"\n==================== {device_name} ====================")
        conn = connect(device_name)
        try:
            for cmd in VALIDATION[device_name]:
                print(f"\n$ {cmd}")
                print(conn.send_command(cmd))
        finally:
            conn.disconnect()


if __name__ == "__main__":
    main()
