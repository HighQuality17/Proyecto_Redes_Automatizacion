import time
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
from inventory import INVENTORY


def connect(device_name: str, retries: int = 3, delay: int = 8):
    device = INVENTORY[device_name]

    for attempt in range(1, retries + 1):
        try:
            print(f"[CONNECT] {device_name} intento {attempt}/{retries} -> {device['host']}")
            conn = ConnectHandler(**device)
            conn.enable()
            print(f"[OK] Conectado a {device_name}")
            return conn

        except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
            print(f"[ERROR] No se pudo conectar a {device_name}: {error}")

            if attempt < retries:
                print(f"[WAIT] Esperando {delay}s antes de reintentar...")
                time.sleep(delay)
            else:
                raise


def push_config(conn, commands, title: str = ""):
    if not commands:
        print(f"[SKIP] {title}")
        return

    if title:
        print(f"\n--- {title} ---")

    output = conn.send_config_set(commands, delay_factor=2)
    print(output)


def run_exec(conn, commands, title: str = ""):
    if not commands:
        return

    if title:
        print(f"\n--- {title} ---")

    for cmd in commands:
        print(f"\n$ {cmd}")
        print(conn.send_command_timing(cmd, strip_prompt=False, strip_command=False))


def save_config(conn):
    try:
        print("[SAVE] write memory")
        print(conn.save_config())
    except Exception:
        print(conn.send_command_timing("write memory"))


def check_ssh(device_name: str) -> bool:
    try:
        conn = connect(device_name, retries=2, delay=5)
        conn.disconnect()
        return True
    except Exception:
        return False