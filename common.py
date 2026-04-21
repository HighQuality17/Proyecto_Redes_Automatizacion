from netmiko import ConnectHandler
from inventory import INVENTORY


def connect(device_name: str):
    device = INVENTORY[device_name]
    conn = ConnectHandler(**device)
    conn.enable()
    return conn


def push_config(conn, commands, title: str = ""):
    if title:
        print(f"\n--- {title} ---")
    output = conn.send_config_set(commands)
    print(output)


def run_exec(conn, commands, title: str = ""):
    if title:
        print(f"\n--- {title} ---")
    for cmd in commands:
        print(f"\n$ {cmd}")
        print(conn.send_command_timing(cmd, strip_prompt=False, strip_command=False))


def save_config(conn):
    try:
        print(conn.save_config())
    except Exception:
        print(conn.send_command_timing("write memory"))


def generate_rsa_keys(conn):
    try:
        out = conn.send_command_timing("crypto key generate rsa modulus 1024")
        if "How many bits" in out:
            out += conn.send_command_timing("1024")
        elif "Replace existing" in out:
            out += conn.send_command_timing("yes")
        print(out)
    except Exception:
        print("Aviso: no pude generar RSA automaticamente. Si ya existe SSH, ignoralo.")
