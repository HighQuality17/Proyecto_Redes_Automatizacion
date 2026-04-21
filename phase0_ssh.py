from inventory import DEPLOY_ORDER
from config_data import SSH_USER, SSH_PASS, DOMAIN_NAME
from common import connect, push_config, save_config, generate_rsa_keys


def build_ssh_commands(hostname: str):
    return [
        f"hostname {hostname}",
        f"ip domain-name {DOMAIN_NAME}",
        f"username {SSH_USER} privilege 15 secret {SSH_PASS}",
        "ip ssh version 2",
        "line vty 0 4",
        "login local",
        "transport input ssh",
        "exec-timeout 15 0",
        "exit",
    ]


def main():
    # DEPLOY_ORDER contains SWML1/SWML2/SWML3/SWML4/FW1/FW2.
    for device_name in DEPLOY_ORDER:
        print(f"\n==================== {device_name} ====================")
        conn = connect(device_name)
        try:
            push_config(conn, build_ssh_commands(device_name), f"SSH base - {device_name}")
            generate_rsa_keys(conn)
            save_config(conn)
        finally:
            conn.disconnect()


if __name__ == "__main__":
    main()
