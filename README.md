# No Dev? No Problem. — pySROS for Network Engineers

Training materials for a hands-on 90-minute session on **pySROS** — the Python library for Nokia SR OS — aimed at network engineers with no prior coding background.

> "If you know the CLI, you're ready."

---

## What Is This?

This repo contains everything needed to run or follow along with the training:

- Slide decks (Getting Started + Scripting)
- Ready-to-run Python scripts (out-of-box and on-box)
- A two-node Containerlab lab (Nokia 7750 SR-1 × 2, BGP pre-configured)
- Reference docs and cheat sheets

The only prerequisite is a working Containerlab environment with a Nokia SR OS vSIM image and a valid license. See [Lab Setup](#lab-setup) below.

---

## Repo Structure

```
.
├── README.md
│
├── slides/
│   ├── pySROS_Getting_Started.pptx   # Deck 1: venv, install, interactive mode
│   └── pySROS_Scripting.pptx         # Deck 2: out-of-box, on-box, config changes
│
├── scripts/
│   ├── check_lab.py                  # Health check — run this first after deploying
│   │
│   ├── out-of-box/                   # Run from your laptop via NETCONF
│   │   ├── 01_interface_status.py
│   │   ├── 02_bgp_neighbors.py
│   │   ├── 03_set_description.py
│   │   └── 04_bulk_config.py
│   │
│   └── on-box/                       # Deploy to SR OS, run with pyexec
│       ├── 01_onbox_interface_check.py
│       └── 02_onbox_bgp_check.py
│
├── lab/
│   ├── pysros-lab.clab.yml           # Containerlab topology
│   └── configs/
│       ├── pe1.partial.cfg           # PE1 startup config (MD-CLI)
│       └── pe2.partial.cfg           # PE2 startup config (MD-CLI)
│
└── docs/
    ├── 01_virtualenv_setup.txt       # Step-by-step venv and install guide
    ├── 02_interactive_mode_commands.txt  # Interactive mode walkthrough + BGP drill-down
    └── 03_scripts_reference.txt     # All scripts condensed, with quick reference card
```

---

## Lab Topology

```
  ┌─────────────────────────────────────────┐
  │           Management Network            │
  │   172.20.20.11          172.20.20.12    │
  └──────────┬──────────────────┬───────────┘
             │                  │
      ┌──────┴──────┐    ┌──────┴──────┐
      │     pe1     │    │     pe2     │
      │  10.0.0.1   │    │  10.0.0.2   │
      │  AS 65001   │    │  AS 65001   │
      └──────┬──────┘    └──────┬──────┘
             │  192.168.1.1/30  │
             │  ──────────────  │
             │  192.168.1.2/30  │
             └──────────────────┘
                    1/1/1 <-> 1/1/1

  Underlay:  OSPF area 0
  Overlay:   iBGP between loopbacks (10.0.0.1 <-> 10.0.0.2)
  Platform:  Nokia 7750 SR-1 (vSIM)
```

| | PE1 | PE2 |
|---|---|---|
| System name | `pe1` | `pe2` |
| Loopback | 10.0.0.1/32 | 10.0.0.2/32 |
| Link IP | 192.168.1.1/30 | 192.168.1.2/30 |
| BGP peer | 10.0.0.2 | 10.0.0.1 |
| Mgmt IP | 172.20.20.11 | 172.20.20.12 |

---

## Lab Setup

### Prerequisites

- [Containerlab](https://containerlab.dev) installed
- `nokia_srsim` Docker image (SR-SIM — fully containerised, no QEMU)
- Valid SR OS license file

### 1 — Obtain the SR-SIM image

The `nokia_srsim` image is available via Nokia's container registry. Contact your Nokia account team or check the [SR-SIM documentation](https://containerlab.dev/manual/kinds/sros/) for access details.

Verify the image is available locally:
```bash
docker images | grep nokia_srsim
```

Update the image tag in `lab/pysros-lab.clab.yml` if yours differs from `localhost/nokia/srsim:25.10.R1`.

### 2 — License file location

The topology expects the license file at `../../sros_25-10.txt` relative to the topology file — meaning two directories above `lab/`. Adjust the path in `pysros-lab.clab.yml` if your license file is named or located differently:

```yaml
kinds:
  nokia_srsim:
    license: ../../sros_25-10.txt   # ← update this path if needed
```

### 3 — Deploy

```bash
cd lab/
sudo clab deploy -t pysros-lab.clab.yml
```

Boot takes approximately 1–2 minutes. Monitor with:

```bash
watch docker ps
```

Wait until both containers show `(healthy)`.

### 4 — Verify

```bash
sudo clab inspect -t pysros-lab.clab.yml
ssh admin@clab-pysros-lab-pe1    # password: admin
```

---

## pySROS Setup

```bash
# Create and activate a virtual environment
python3 -m venv pysros-env
source pysros-env/bin/activate      # Linux/Mac
# pysros-env\Scripts\activate       # Windows

# Install pySROS
pip install pysros

# Verify
python3 -c "import pysros; print('pySROS ready')"
```

See `docs/01_virtualenv_setup.txt` for detailed setup instructions and troubleshooting.

### Run the health check

```bash
python3 scripts/check_lab.py
```

Expected output:

```
  Node: pe1  (clab-pysros-lab-pe1)
  ══════════════════════════════════════════════════════════════
  System name : pe1
  Location    : Amsterdam, Netherlands
  SR OS ver   : TiMOS-B-24.x.Rx ...
  Port 1/1/1  : admin=enable  oper=up
  BGP neighbors (1 found):
    10.0.0.2           state=Established   last=Active
```

---

## Scripts

### Out-of-Box (run from your laptop)

All scripts in `scripts/out-of-box/` connect to the nodes via NETCONF. Update the `HOST` variable at the top of each script if your node names differ.

| Script | What it does |
|---|---|
| `01_interface_status.py` | Prints admin/oper state of all ports, flags admin-up/oper-down |
| `02_bgp_neighbors.py` | BGP session state table, flags non-established sessions |
| `03_set_description.py` | Sets port descriptions via candidate datastore and commits |
| `04_bulk_config.py` | Applies NTP config to all nodes in a list, prints pass/fail summary |

### On-Box (deploy to SR OS, run with `pyexec`)

Scripts in `scripts/on-box/` use `connect()` with no arguments — they connect to the local SR OS instance.

```bash
# Copy to the router
scp scripts/on-box/01_onbox_interface_check.py admin@clab-pysros-lab-pe1:/cf3:/scripts/

# Run on the router
ssh admin@clab-pysros-lab-pe1
pyexec /cf3:/scripts/01_onbox_interface_check.py
```

| Script | What it does |
|---|---|
| `01_onbox_interface_check.py` | Interface status table, runs natively on SR OS |
| `02_onbox_bgp_check.py` | BGP neighbor check, runs natively on SR OS |

---

## Interactive Mode Quick Start

```bash
source pysros-env/bin/activate
python3
```

```python
from pysros.management import connect

conn = connect(
    host="clab-pysros-lab-pe1",
    username="admin",
    password="admin",
    hostkey_verify=False
)

# System info
conn.running.get("/nokia-conf:configure/system/name")
conn.running.get("/nokia-conf:configure/system/location")

# BGP neighbor state
neighbors = conn.running.get(
    "/nokia-state:state/router[router-name=Base]/bgp/neighbor"
)
n = neighbors["10.0.0.2"]

# Always check keys first — SR OS state data is sparse
for k in n.keys():
    print(k)
# ip-address   statistics   graceful-restart

# session-state lives inside statistics
n["statistics"]["session-state"].data    # 'Established'
n["statistics"]["last-state"].data       # 'Active'
n["statistics"]["last-event"].data       # 'recvOpen'

conn.disconnect()
```

See `docs/02_interactive_mode_commands.txt` for a full walkthrough.

---

## Key YANG Paths

| Data | Path |
|---|---|
| System name | `/nokia-conf:configure/system/name` |
| System location | `/nokia-conf:configure/system/location` |
| SR OS version | `/nokia-state:state/system/version/version-number` |
| All ports | `/nokia-state:state/port` |
| BGP neighbors | `/nokia-state:state/router[router-name="Base"]/bgp/neighbor` |
| BGP session state | `...bgp/neighbor[ip-address="10.0.0.2"]/statistics/session-state` |
| Port description (rw) | `/nokia-conf:configure/port[port-id="1/1/1"]/description` |

> **Note:** `session-state` is nested inside `statistics`, not at the top level of the neighbor container. Always use `.keys()` to explore before accessing fields — SR OS state data is sparse and field availability varies by version.

---

## Slides

| Deck | Contents |
|---|---|
| `pySROS_Getting_Started.pptx` | What is pySROS, venv setup, install, interactive mode, YANG paths, cheat sheet |
| `pySROS_Scripting.pptx` | Interactive mode deep-dive, out-of-box scripts, on-box scripts, config changes, real-world patterns |

---

## Session Outline (90 min)

| | Topic | Time |
|---|---|---|
| 1 | Recap: MDM + pySROS concepts | 5 min |
| 2 | venv + install + interactive mode | 20 min |
| 3 | Out-of-box scripts via NETCONF | 20 min |
| 4 | On-box scripts (running on SR OS) | 15 min |
| 5 | Config changes (set/commit) | 15 min |
| 6 | Real-world patterns | 10 min |
| 7 | Q&A | 5 min |

---

## Requirements

- Python 3.10+
- `pysros` (install via `pip install pysros`)
- Containerlab (for the lab environment)
- Nokia SR OS vSIM image + license (sourced from Nokia)

---

## License

Training materials are provided for educational use.
Nokia SR OS, pySROS, and Containerlab are products of their respective owners.
