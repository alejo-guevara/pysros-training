#!/usr/bin/env python3
"""
Script 05 - BGP Neighbor Check (On-box / Runs directly on SR OS)
----------------------------------------------------------------
Runs INSIDE SR OS. Checks all BGP neighbors and flags any that
are NOT in the Established state — useful as a health check
script triggered by an event or scheduled job.

Upload to SR OS and run with:
    pyexec 05_onbox_bgp_check.py

Exit codes:
    0 = all neighbors established
    1 = one or more neighbors NOT established (alerts the scheduler)
"""

import sys
from pysros.management import connect
from pysros.pprint import Table


def main():
    # On-box connection — no arguments needed
    conn = connect()

    system_name = conn.running.get(
        "/nokia-conf:configure/system/name"
    ).data    # .data to get the string value from the Leaf

    path = "/nokia-state:state/router[router-name='Base']/bgp/neighbor"
    neighbors = conn.running.get(path)

    if not neighbors:
        print("[" + system_name + "] No BGP neighbors configured.")
        sys.exit(0)

    cols = [
        (20, "Peer Address"),
        (8,  "Peer AS"),
        (14, "State"),
        (8,  "Health"),
    ]
    table = Table("BGP Health Check -- " + system_name, columns=cols)

    rows = []
    issues = []

    for peer_ip, data in neighbors.items():
        try:
            peer_as = str(data["peer-as"].data)
        except KeyError:
            peer_as = "N/A"

        try:
            state = str(data["statistics"]["session-state"].data)
        except KeyError:
            state = "unknown"

        health = "OK" if state.lower() == "established" else "DOWN"

        if state.lower() != "established":
            issues.append(str(peer_ip))

        rows.append((str(peer_ip), peer_as, state, health))

    table.print(rows)

    if issues:
        print("\n!! " + str(len(issues)) + " neighbor(s) not established:")
        for ip in issues:
            print("   - " + ip)
        sys.exit(1)   # Non-zero exit triggers SR OS event actions
    else:
        print("\nAll BGP neighbors established.")
        sys.exit(0)


if __name__ == "__main__":
    main()