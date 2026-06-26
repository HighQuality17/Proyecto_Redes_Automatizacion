# 🌐 Proyecto Redes — Automatización de Red Híbrida Empresarial

Automatización completa de una red híbrida empresarial sobre equipos Cisco IOS simulados en **GNS3**, usando **Python + Netmiko**. El proyecto configura desde cero una infraestructura de red con múltiples capas: switching L2/L3, redundancia, routing dinámico, segmentación por VLANs y control de acceso mediante ACLs.

---

## 🏗️ Arquitectura de la red

La topología implementada incluye:

- **2 Firewalls (FW1 / FW2)** — enrutamiento hacia zona DMZ híbrida e internet, conectados a la nube/edge físico
- **2 Core Switches L3 (SWML1 / SWML2)** — inter-VLAN routing y redundancia HSRP, conectados en malla con los firewalls
- **2 Switches de Acceso L2 (SWML3 / SWML4)** — conectividad hacia end devices (PC1–PC6), con uplinks duales hacia ambos core switches
- **VLANs segmentadas** por departamento/función (datos, voz, gestión, servidores, DMZ)
- **Zona híbrida física** compuesta por un **router HP** y un **switch Cisco físicos**, conectados a GNS3 mediante interfaces de red reales. El router HP proveía la salida a internet y FW1 enrutaba el tráfico hacia él. El switch físico Cisco alojaba una **zona DMZ** con servidores reales, accesible desde la red virtual
- **OSPF área 0** como protocolo de routing dinámico entre los dispositivos L3

![Topología de Red](https://raw.githubusercontent.com/HighQuality17/Proyecto_Redes_Automatizacion/main/TopologiaRedes.jpeg)

---

## ⚙️ Tecnologías utilizadas

| Herramienta | Uso |
|---|---|
| Python 3 | Lenguaje de automatización |
| Netmiko | Conexión SSH a dispositivos Cisco IOS |
| GNS3 | Simulación de la topología de red |
| Cisco IOS | Sistema operativo de switches y firewalls |
| OSPF | Protocolo de routing dinámico |
| HSRP | Redundancia de gateway en capa L3 |

---

## 📁 Estructura del proyecto

```
├── inventory.py              # Inventario de dispositivos (IP, credenciales, tipo)
├── config_data.py            # Variables centralizadas de red (IPs, máscaras, VLANs, IDs OSPF)
├── common.py                 # Funciones reutilizables: connect(), push_config(), save_config()
├── phase0_ssh.py             # Fase 0: verificación de conectividad SSH a todos los dispositivos
├── phase1_l2.py              # Fase 1: configuración L2 — VLANs, troncales, puertos de acceso
├── phase2_l3_hsrp_dhcp.py   # Fase 2: interfaces L3, HSRP, DHCP en core switches
├── phase3_ospf_routes_acl.py # Fase 3: interfaces de firewalls, OSPF, rutas estáticas
└── phase4_acls.py            # Fase 4: listas de control de acceso (ACLs) por zona
    phase4_validate.py        # Validación automática de conectividad y ACLs
```

---

## 🚀 Cómo ejecutar

### Requisitos previos

```bash
pip install netmiko
```

- GNS3 corriendo con la topología cargada
- Dispositivos Cisco IOS con SSH habilitado manualmente (o via `phase0_ssh.py`)
- Ajustar `inventory.py` con las IPs y credenciales de tu laboratorio

### Ejecución por fases

```bash
# Verificar conectividad SSH a todos los dispositivos
python phase0_ssh.py

# Configurar VLANs y switching L2
python phase1_l2.py

# Configurar routing L3, HSRP y DHCP
python phase2_l3_hsrp_dhcp.py

# Configurar firewalls, OSPF y rutas
python phase3_ospf_routes_acl.py

# Aplicar y validar ACLs
python phase4_acls.py
python phase4_validate.py
```

Cada fase incluye **pre-check SSH** automático antes de aplicar cambios, reintentos con backoff y `write memory` al finalizar.

---

## 🔒 Seguridad y control de acceso

- ACLs aplicadas por zona para controlar tráfico entre VLANs
- Separación de tráfico con zonas DMZ aisladas
- Firewalls con rutas estáticas hacia internet y zona híbrida
- `passive-interface default` en OSPF para minimizar superficie de ataque

---

## 📌 Aprendizajes clave

- Automatización de configuración de red con Netmiko sobre Cisco IOS real
- Diseño de topologías empresariales con redundancia (HSRP) y routing dinámico (OSPF)
- Separación de responsabilidades por fases para configuraciones repetibles y controladas
- Centralización de variables de red en `config_data.py` para facilitar mantenimiento

---

## 👤 Autor

**Joni Alexander Cuartas Pineda**  
Estudiante de Administración de Sistemas Informáticos — Universidad Nacional de Colombia  
[LinkedIn](https://www.linkedin.com/in/joni-alexander-cuartas-pineda-a277353ab/) · [GitHub](https://github.com/HighQuality17)
