"""
02_bgp_neighbors.py
====================
OUT-OF-BOX script — runs from your laptop via NETCONF.

What it does:
  Connects to an SR OS node and prints the session state
  of all BGP neighbors in the Base routing instance.

Usage:
  python3 02_bgp_neighbors.py

Requirements:
  pip install pysros
"""

from pysros.management import connect


# ── Connection details ──────────────────────────────────────────────────────
HOST     = "clab-pysros-lab-pe1"
USERNAME = "admin"
PASSWORD = "admin"

# YANG path for BGP neighbor state
# Note: router-name=Base targets the default/Base routing instance
BGP_PATH = (
    "/nokia-state:state/router[router-name=Base]"
    "/bgp/neighbor"  # we'll drill into /statistics for session-state
)


def get_bgp_neighbors(conn):
    """Return a list of (ip, session_state, peer_as, uptime) tuples."""
    try:
        neighbors = conn.running.get(BGP_PATH)
    except Exception:
        # BGP may not be configured on this node
        return []

    results = []
    for ip, data in neighbors.items():
        # session-state lives inside the statistics sub-container
        stats      = data.get("statistics",  None)
        peer_as    = data.get("peer-as",     None)

        session_state = stats["session-state"].data if stats and "session-state" in stats else "n/a"
        last_state    = stats["last-state"].data    if stats and "last-state"    in stats else "n/a"
        peer_as_val   = str(peer_as.data)           if peer_as                           else "n/a"

        results.append((str(ip), session_state, last_state, peer_as_val))
    return sorted(results)


def print_table(rows):
    """Pretty-print BGP neighbor table."""
    header = f"{'NEIGHBOR':<22} {'SESSION-STATE':<18} {'LAST-STATE':<14} {'PEER-AS':<12}"
    separator = "-" * len(header)
    print(separator)
    print(header)
    print(separator)

    if not rows:
        print("  No BGP neighbors found (BGP may not be configured).")
    else:
        for ip, state, peer_as, last_event in rows:
            # Highlight non-established sessions
            flag = " ← CHECK" if oper_state != "established" else ""
            print(f"{ip:<22} {oper_state:<18} {peer_as:<12} {last_event:<20}{flag}")

    print(separator)
    established = sum(1 for _, s, _, _ in rows if s.lower() == "established")
    print(f"Total: {len(rows)} neighbors  |  Established: {established}")


def main():
    print(f"Connecting to {HOST}...")
    conn = connect(
        host=HOST,
        username=USERNAME,
        password=PASSWORD,
        hostkey_verify=False
    )
    print("Connected.\n")

    rows = get_bgp_neighbors(conn)
    print_table(rows)

    conn.disconnect()


if __name__ == "__main__":
    main()
