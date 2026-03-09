"""
01_interface_status.py
======================
OUT-OF-BOX script — runs from your laptop via NETCONF.

What it does:
  Connects to an SR OS node and prints the admin/oper state
  of every port in a clean table format.

Usage:
  python3 01_interface_status.py

Requirements:
  pip install pysros
"""

from pysros.management import connect


# ── Connection details ──────────────────────────────────────────────────────
# Update host to match your Containerlab node name or IP
HOST     = "clab-pysros-lab-pe1"
USERNAME = "admin"
PASSWORD = "NokiaSros1!"

# YANG path for port state
PORT_STATE_PATH = "/nokia-state:state/port"


def get_interface_status(conn):
    """Return a list of (port_id, admin_state, oper_state) tuples."""
    ports = conn.running.get(PORT_STATE_PATH)
    results = []
    for port_id, port_data in ports.items():
        admin = port_data.get("admin-state", None)
        oper  = port_data.get("oper-state",  None)
        admin_val = admin.data if admin else "n/a"
        oper_val  = oper.data  if oper  else "n/a"
        results.append((port_id, admin_val, oper_val))
    return sorted(results)


def print_table(rows):
    """Pretty-print interface status."""
    header = f"{'PORT':<18} {'ADMIN':<10} {'OPER':<10}"
    separator = "-" * len(header)
    print(separator)
    print(header)
    print(separator)
    for port_id, admin, oper in rows:
        # Highlight ports that are admin-up but oper-down
        flag = " ← DOWN" if admin == "up" and oper == "down" else ""
        print(f"{port_id:<18} {admin:<10} {oper:<10}{flag}")
    print(separator)
    print(f"Total ports: {len(rows)}")


def main():
    print(f"Connecting to {HOST}...")
    conn = connect(
        host=HOST,
        username=USERNAME,
        password=PASSWORD,
        hostkey_verify=False
    )
    print("Connected.\n")

    rows = get_interface_status(conn)
    print_table(rows)

    conn.disconnect()


if __name__ == "__main__":
    main()
