#!/usr/bin/env python3
"""
check_lab.py — pySROS Training Lab Health Check
Connects to both PE nodes and prints a summary of:
  - System name and software version
  - Interface status (1/1/c1/1)
  - BGP neighbor state

Run from your laptop:
    python3 check_lab.py

Requires: pip install pysros
"""

from pysros.management import connect

NODES = [
    {"name": "pe1", "host": "clab-pysros-lab-pe1"},
    {"name": "pe2", "host": "clab-pysros-lab-pe2"},
]
CREDS = {"username": "admin", "password": "admin", "hostkey_verify": False}

SEPARATOR = "=" * 62


def check_node(name, host):
    print(f"\n{SEPARATOR}")
    print(f"  Node: {name}  ({host})")
    print(SEPARATOR)

    try:
        conn = connect(host=host, **CREDS)
    except Exception as e:
        print(f"  ✗ Could not connect: {e}")
        return

    # --- System info ---
    try:
        sys_name = conn.running.get("/nokia-conf:configure/system/name").data
        location = conn.running.get("/nokia-conf:configure/system/location").data
        version  = conn.running.get(
            "/nokia-state:state/system/version/version-number"
        ).data
        print(f"  System name : {sys_name}")
        print(f"  Location    : {location}")
        print(f"  SR OS ver   : {version}")
    except Exception as e:
        print(f"  System info error: {e}")

    # --- Port 1/1/c1/1 state ---
    try:
        ports = conn.running.get("/nokia-state:state/port")
        if "1/1/c1/1" in ports:
            p = ports["1/1/c1/1"]
            admin = p.get("admin-state", None)
            oper  = p.get("oper-state",  None)
            admin_val = admin.data if admin else "n/a"
            oper_val  = oper.data  if oper  else "n/a"
            flag = "  ← DOWN" if oper_val != "up" else ""
            print(f"  Port 1/1/c1/1  : admin={admin_val}  oper={oper_val}{flag}")
        else:
            print("  Port 1/1/c1/1  : not found")
    except Exception as e:
        print(f"  Port state error: {e}")

    # --- BGP neighbors ---
    try:
        neighbors = conn.running.get(
            "/nokia-state:state/router[router-name=Base]/bgp/neighbor"
        )
        print(f"  BGP neighbors ({len(neighbors)} found):")
        for ip, n in neighbors.items():
            stats = n.get("statistics", None)
            if stats:
                state      = stats["session-state"].data if "session-state" in stats else "n/a"
                last_state = stats["last-state"].data    if "last-state"    in stats else "n/a"
            else:
                state, last_state = "n/a", "n/a"
            flag = "  ← CHECK" if state.lower() != "established" else ""
            print(f"    {str(ip):<18} state={state:<14} last={last_state}{flag}")
    except Exception as e:
        print(f"  BGP neighbor error: {e}")

    conn.disconnect()


if __name__ == "__main__":
    print(f"\n{'pySROS Training Lab — Health Check':^62}")
    for node in NODES:
        check_node(node["name"], node["host"])
    print(f"\n{SEPARATOR}\n")
