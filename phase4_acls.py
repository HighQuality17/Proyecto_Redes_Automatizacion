import time

from common import connect, push_config, save_config, check_ssh
from config_data import (
    CORE_SWITCHES,
    ACCESS_SWITCHES,
    FIREWALLS,
    FW1_OUTSIDE_IF,
)


ALL_DEVICES = CORE_SWITCHES + ACCESS_SWITCHES + FIREWALLS

# VLANs autorizadas para salir hacia red física / universidad / internet.
PERMITTED_OUTBOUND_NETWORKS = [
    "10.10.20.0 0.0.0.255",  # QA
    "10.10.40.0 0.0.0.255",  # Ventas
    "10.10.50.0 0.0.0.255",  # TI Operaciones
    "10.10.60.0 0.0.0.255",  # Servidores
]

# VLANs restringidas hacia el perímetro.
RESTRICTED_OUTBOUND_NETWORKS = [
    "10.10.10.0 0.0.0.255",  # Desarrollo
    "10.10.30.0 0.0.0.255",  # Soporte_Admin
    "10.10.90.0 0.0.0.255",  # Gestión
]

# Servidor físico en DMZ.
DMZ_WEB_SERVER = "10.10.70.10"

# SVIs donde aplicamos política interna para evitar acceso administrativo indebido.
USER_SVIS_FOR_INTERNAL_ACL = [
    "Vlan10",
    "Vlan20",
    "Vlan40",
    "Vlan50",
    "Vlan60",
]


def build_fw1_perimeter_acl():
    cmds = [
        f"interface {FW1_OUTSIDE_IF}",
        "no ip access-group PERIMETRAL_OUT out",
        "exit",

        "no ip access-list extended PERIMETRAL_OUT",

        "ip access-list extended PERIMETRAL_OUT",
        "remark === POLITICA PERIMETRAL: salida controlada hacia HP/Universidad/Internet ===",

        # Permitir pruebas desde el propio segmento FW1-HP.
        "permit ip host 192.168.100.3 any",

        "remark === Acceso controlado hacia DMZ fisica ===",
    ]

    for network in PERMITTED_OUTBOUND_NETWORKS:
        cmds.extend([
            f"permit tcp {network} host {DMZ_WEB_SERVER} eq 80",
            f"permit tcp {network} host {DMZ_WEB_SERVER} eq 443",
            f"permit icmp {network} host {DMZ_WEB_SERVER}",
        ])

    cmds.extend([
        # Bloquea accesos no autorizados hacia la DMZ física.
        "deny ip any 10.10.70.0 0.0.0.255 log",

        "remark === Salida general permitida solo para VLANs autorizadas ===",
    ])

    for network in PERMITTED_OUTBOUND_NETWORKS:
        cmds.append(f"permit ip {network} any")

    cmds.extend([
        "remark === Bloqueo de VLANs restringidas hacia el perimetro ===",
    ])

    for network in RESTRICTED_OUTBOUND_NETWORKS:
        cmds.append(f"deny ip {network} any log")

    cmds.extend([
        # Cierre explícito.
        "deny ip any any log",
        "exit",

        f"interface {FW1_OUTSIDE_IF}",
        "ip access-group PERIMETRAL_OUT out",
        "exit",
    ])

    return cmds


def build_vty_mgmt_acl():
    return [
        "no ip access-list standard MGMT_ONLY",
        "ip access-list standard MGMT_ONLY",
        "remark === Solo VLAN90 y VLAN30 pueden administrar por SSH ===",
        "permit 10.10.90.0 0.0.0.255",
        "permit 10.10.30.0 0.0.0.255",
        "deny any log",
        "exit",

        "line vty 0 4",
        "access-class MGMT_ONLY in",
        "login local",
        "transport input ssh",
        "exit",

        "line vty 5 15",
        "access-class MGMT_ONLY in",
        "login local",
        "transport input ssh",
        "exit",
    ]


def build_internal_acl():
    cmds = []

    for svi in USER_SVIS_FOR_INTERNAL_ACL:
        cmds.extend([
            f"interface {svi}",
            "no ip access-group USER_INTERNAL_POLICY in",
            "exit",
        ])

    cmds.extend([
        "no ip access-list extended USER_INTERNAL_POLICY",
        "ip access-list extended USER_INTERNAL_POLICY",
        "remark === Bloqueo de administracion hacia red de gestion desde VLANs de usuarios ===",
        "deny tcp any 10.10.90.0 0.0.0.255 eq 22 log",
        "deny tcp any 10.10.90.0 0.0.0.255 eq 23 log",
        "deny tcp any 10.10.90.0 0.0.0.255 eq 80 log",
        "deny tcp any 10.10.90.0 0.0.0.255 eq 443 log",
        "permit ip any any",
        "exit",
    ])

    for svi in USER_SVIS_FOR_INTERNAL_ACL:
        cmds.extend([
            f"interface {svi}",
            "ip access-group USER_INTERNAL_POLICY in",
            "exit",
        ])

    return cmds


def precheck_devices():
    print("\n========== PRE-CHECK SSH FASE 4 ACLs ==========")

    failed = []

    for device_name in ALL_DEVICES:
        if not check_ssh(device_name):
            failed.append(device_name)

    if failed:
        print("\n[STOP] No se puede iniciar fase 4.")
        print(f"Equipos sin SSH: {failed}")
        return False

    print("\n[OK] Todos los equipos responden por SSH.")
    return True


def main():
    if not precheck_devices():
        return

    print("\n========== ACL PERIMETRAL EN FW1 ==========")
    conn = connect("FW1")
    try:
        push_config(conn, build_fw1_perimeter_acl(), "FW1 PERIMETRAL_OUT")
        time.sleep(3)
        save_config(conn)
    finally:
        conn.disconnect()

    print("\n========== ACL DE GESTION VTY EN TODOS LOS EQUIPOS ==========")
    for device_name in ALL_DEVICES:
        print(f"\n==================== {device_name} ====================")
        conn = connect(device_name)

        try:
            push_config(conn, build_vty_mgmt_acl(), f"{device_name} MGMT_ONLY")
            time.sleep(2)
            save_config(conn)

        finally:
            conn.disconnect()

    print("\n========== ACL INTERNA EN CORE ==========")
    for device_name in CORE_SWITCHES:
        print(f"\n==================== {device_name} ====================")
        conn = connect(device_name)

        try:
            push_config(conn, build_internal_acl(), f"{device_name} USER_INTERNAL_POLICY")
            time.sleep(2)
            save_config(conn)

        finally:
            conn.disconnect()

    print("\n[OK] Fase 4 ACLs finalizada.")


if __name__ == "__main__":
    main()