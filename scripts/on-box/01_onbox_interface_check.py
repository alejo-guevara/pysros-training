"""
01_onbox_interface_check.py
============================
ON-BOX script -- deploy to SR OS and run with: pyexec /cf3:/scripts/interface_check

What it does:
  Same interface status check as Script 01 but runs *inside* SR OS.
  Uses connect() with no arguments -- pySROS handles the local connection.

How to deploy to Containerlab SR OS node:
  scp 01_onbox_interface_check.py admin@clab-pysros-lab-pe1:/cf3:/scripts/interface_check

How to run on SR OS (MD-CLI):
  [/]
  A:admin@pe1# tools perform python-script reload "interface_check"
  A:admin@pe1# pyexec "interface_check"

Requirements:
  pySROS is pre-installed on SR OS 21.10+
"""

from pysros.management import connect
from pysros.pprint import Table


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
    conn = connect()

    rows = get_interface_status(conn)

    # Column format: (width, "Heading") -- width MUST come first
    cols = [
        (18, "Port"),
        (14, "Admin State"),
        (14, "Oper State"),
    ]
    table = Table("Interface Status", columns=cols)

    # Build rows list, pass to table.print() in one call (Rule 5)
    table.print(rows)

    conn.disconnect()


if __name__ == "__main__":
    main()