"""
04_set_description.py
======================
CONFIG CHANGE script — runs from your laptop via NETCONF.

What it does:
  Sets port descriptions on one or more ports using the candidate
  datastore, then commits. A safe pattern with rollback on error.

Usage:
  python3 04_set_description.py

Requirements:
  pip install pysros
"""

from pysros.management import connect


# ── Connection details ──────────────────────────────────────────────────────
HOST     = "clab-pysros-lab-pe1"
USERNAME = "admin"
PASSWORD = "admin"

# ── Ports to configure: {port_id: description} ─────────────────────────────
PORT_DESCRIPTIONS = {
    "1/1/c1/1": "Uplink to Core-01",
    "1/1/2": "Peering Link - AS65001",
    "1/1/3": "Customer - ACME Corp",
}


def set_port_description(conn, port_id, description):
    """Set the description on a single port via candidate config."""
    path = (
        f"/nokia-conf:configure/port[port-id={port_id}]"
        f"/description"
    )
    conn.candidate.set(path, description)
    print(f"  Staged: {port_id} → '{description}'")


def main():
    print(f"Connecting to {HOST}...")
    conn = connect(
        host=HOST,
        username=USERNAME,
        password=PASSWORD,
        hostkey_verify=False
    )
    print("Connected.\n")

    print("Staging config changes...")
    try:
        for port_id, description in PORT_DESCRIPTIONS.items():
            set_port_description(conn, port_id, description)

        print("\nCommitting...")
        conn.candidate.commit()
        print("✓ Config committed successfully.\n")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("  Rolling back — no changes applied.")
        # candidate is discarded automatically on error or disconnect

    finally:
        conn.disconnect()

    # Verify — read back what we set
    print("Verifying changes...")
    conn = connect(
        host=HOST,
        username=USERNAME,
        password=PASSWORD,
        hostkey_verify=False
    )
    for port_id in PORT_DESCRIPTIONS:
        path = f"/nokia-conf:configure/port[port-id={port_id}]/description"
        try:
            result = conn.running.get(path)
            print(f"  {port_id}: '{result.data}'")
        except Exception:
            print(f"  {port_id}: (not configured)")
    conn.disconnect()


if __name__ == "__main__":
    main()
