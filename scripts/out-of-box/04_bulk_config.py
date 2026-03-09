"""
05_bulk_config.py
==================
REAL-WORLD script — bulk config change across multiple SR OS nodes.

What it does:
  Connects to every node in the NODES list and applies an NTP server
  config to each one. Produces a summary report at the end.

  This is the template pattern for any bulk automation task:
    1. Define your node list
    2. Define your config function
    3. Loop, connect, apply, disconnect
    4. Report results

Usage:
  python3 05_bulk_config.py

Requirements:
  pip install pysros
"""

from pysros.management import connect


# ── Node inventory ──────────────────────────────────────────────────────────
# Add/remove nodes to match your Containerlab topology
NODES = [
    {"host": "clab-pysros-lab-pe1", "name": "PE1"},
    {"host": "clab-pysros-lab-pe2", "name": "PE2"},
    {"host": "clab-pysros-lab-pe2",  "name": "P1"},
]

# Shared credentials (use SSH keys / vault in production)
USERNAME = "admin"
PASSWORD = "admin"

# ── NTP config ──────────────────────────────────────────────────────────────
NTP_SERVER_IP = "10.0.0.1"


def apply_ntp_server(conn, ntp_ip):
    """Add preferred NTP server to the node's config."""
    path = (
        f"/nokia-conf:configure/system/time/ntp"
        f"/server[ip-address={ntp_ip}]/prefer"
    )
    conn.candidate.set(path, True)
    conn.candidate.commit()


def check_ntp_configured(conn, ntp_ip):
    """Verify NTP server is present in running config."""
    path = (
        f"/nokia-conf:configure/system/time/ntp"
        f"/server[ip-address={ntp_ip}]/prefer"
    )
    try:
        result = conn.running.get(path)
        return result.data is True
    except Exception:
        return False


def main():
    results = []   # collect (name, status, message) per node

    print(f"Applying NTP config ({NTP_SERVER_IP}) to {len(NODES)} nodes...\n")
    print(f"{'NODE':<10} {'STATUS':<10} DETAIL")
    print("-" * 55)

    for node in NODES:
        name = node["name"]
        host = node["host"]
        try:
            conn = connect(
                host=host,
                username=USERNAME,
                password=PASSWORD,
                hostkey_verify=False
            )

            apply_ntp_server(conn, NTP_SERVER_IP)

            # Verify
            ok = check_ntp_configured(conn, NTP_SERVER_IP)
            conn.disconnect()

            if ok:
                status  = "✓ OK"
                detail  = f"NTP {NTP_SERVER_IP} verified in running config"
                results.append((name, "ok", detail))
            else:
                status  = "⚠ WARN"
                detail  = "Committed but verification failed"
                results.append((name, "warn", detail))

        except Exception as e:
            status = "✗ FAIL"
            detail = str(e)
            results.append((name, "fail", detail))

        print(f"{name:<10} {status:<10} {detail}")

    # Summary
    print("-" * 55)
    ok_count   = sum(1 for _, s, _ in results if s == "ok")
    fail_count = sum(1 for _, s, _ in results if s == "fail")
    warn_count = sum(1 for _, s, _ in results if s == "warn")
    print(f"\nSummary: {ok_count} OK  |  {warn_count} warnings  |  {fail_count} failed")

    if fail_count > 0:
        print("\nFailed nodes:")
        for name, status, detail in results:
            if status == "fail":
                print(f"  {name}: {detail}")


if __name__ == "__main__":
    main()
