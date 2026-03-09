"""
03_onbox_interface_check.py
============================
ON-BOX script — deploy to SR OS and run with: pyexec /cf3:/scripts/03_onbox_interface_check.py

What it does:
  Same interface status check as Script 01 but runs *inside* SR OS.
  Uses connect() with no arguments — pySROS handles the local connection.

How to deploy to Containerlab SR OS node:
  scp 03_onbox_interface_check.py admin@clab-srexperts-pe1:/cf3:/scripts/

How to run on SR OS (MD-CLI):
  [/]
  A:admin@pe1# pyexec /cf3:/scripts/03_onbox_interface_check.py

Requirements:
  pySROS is pre-installed on SR OS 21.10+
"""

from pysros.management import connect
from pysros.pprint import Table          # SR OS built-in pretty table


PORT_STATE_PATH = "/nokia-state:state/port"


def get_interface_status(conn):
    """Return a list of (port_id, admin_state, oper_state) tuples."""
    ports = conn.running.get(PORT_STATE_PATH)
    results = []
    for port_id, port_data in ports.items():
        admin = port_data.get("admin-state", None)
        oper  = port_data.get("oper-state",  None)
        results.append((
            str(port_id),
            admin.data if admin else "n/a",
            oper.data  if oper  else "n/a",
        ))
    return sorted(results)


def main():
    # ON-BOX: no host/credentials needed — connects to local SR OS instance
    conn = connect()

    rows = get_interface_status(conn)

    # Use pySROS built-in Table for SR OS-style output
    cols = [
        ("Port",       18),
        ("Admin State", 14),
        ("Oper State",  14),
    ]
    table = Table("Interface Status", columns=cols)

    for port_id, admin, oper in rows:
        table.add(port_id, admin, oper)

    table.print()
    conn.disconnect()


if __name__ == "__main__":
    main()
