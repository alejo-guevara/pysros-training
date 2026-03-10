"""
01_onbox_interface_check.py
============================
ON-BOX script -- deploy to SR OS and run with: pyexec "interface_check"

What it does:
  Interface status check running *inside* SR OS.
  Shows only breakout Ethernet ports (1/1/cX/Y) -- skips connectors
  and management ports. Admin state comes from config tree; oper state
  from state tree.

How to deploy:
  scp 01_onbox_interface_check.py admin@clab-pysros-lab-pe1:/cf3:/scripts/interface_check

How to run on SR OS (MD-CLI):
  A:admin@pe1# tools perform python-script reload "interface_check"
  A:admin@pe1# pyexec "interface_check"
"""

from pysros.management import connect
from pysros.pprint import Table


def main():
    conn = connect()

    # Admin state lives in config tree; oper state in state tree
    conf_ports  = conn.running.get("/nokia-conf:configure/port")
    state_ports = conn.running.get("/nokia-state:state/port")

    rows = []
    for port_id in sorted(state_ports.keys()):
        port_str = str(port_id)

        # Only show breakout Ethernet ports -- skip connectors and mgmt
        # Breakout ports have format 1/1/cX/Y (four slash-separated parts)
        parts = port_str.split("/")
        if len(parts) != 4:
            continue

        # Admin state from config tree
        if port_str in conf_ports.keys():
            try:
                admin = str(conf_ports[port_id]["admin-state"].data)
            except KeyError:
                admin = "n/a"
        else:
            admin = "n/a"

        # Oper state from state tree
        try:
            oper = str(state_ports[port_id]["oper-state"].data)
        except KeyError:
            oper = "n/a"

        rows.append((port_str, admin, oper))

    cols = [
        (18, "Port"),
        (14, "Admin State"),
        (14, "Oper State"),
    ]
    table = Table("Interface Status", columns=cols)
    table.print(rows)

    conn.disconnect()


if __name__ == "__main__":
    main()