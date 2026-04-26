# MPLS Services — CloudVision Studios Package

A CloudVision Studios package for provisioning and managing MPLS circuits across Arista EOS devices. Operators define customers and circuits through the Studios UI, and the package generates complete EOS CLI configlets, pushes them to a Configlet Studio, and manages interface tags for dashboard visibility.

## Supported Service Types

| Service Type | Description |
|---|---|
| **Direct Internet Access** | Internet peering with BGP or directly connected routing |
| **VPN-V4** | MPLS L3VPN using VPNv4 address family with route distinguishers and route targets |
| **L3-EVPN** | Layer 3 EVPN using EVPN address family |
| **L2-EVPN** | Layer 2 EVPN (ELAN) with VXLAN bridging |
| **L2-EVPN + IRB** | Layer 2 EVPN with Integrated Routing and Bridging (SVI with virtual IP) |
| **VPLS** | Virtual Private LAN Service using LDP pseudowires |
| **VPWS** | Virtual Private Wire Service (point-to-point) using BGP VPWS with patch panel |

## Multi-Homing Support

All service types support three multi-homing modes:

- **Single Homed** — one PE router per circuit endpoint
- **Active Active Multi Homing** — two PE routers with EVPN all-active forwarding (requires Port-Channel)
- **Single Active Multi Homing** — two PE routers with designated forwarder election (requires Ethernet)

Multi-homed circuits generate separate CLI for each PE, with deterministic ESI values derived from both PE loopback addresses.

## Package Structure

```
mpls-services/
  config.yaml                          # Package manifest (name, version)

  studio-mpls-service-manager/         # Customer/circuit input studio
    config.yaml                        #   Studio metadata and autofill action bindings
    schema.yaml                        #   Field definitions (service types, interfaces, BGP, QoS)
    layout.yaml                        #   Conditional field visibility rules
    inputs.yaml                        #   Default/seed input data

  studio-mpls-service-configlets/      # Configlet output studio (receives generated CLI)
    config.yaml                        #   Studio metadata
    schema.yaml                        #   Configlet field definitions
    layout.yaml                        #   Display layout
    template.mako                      #   Mako template for rendering configlets

  action-mpls-service-manager/         # Main provisioning action
    config.yaml                        #   Action metadata (name, parameters)
    script.py                          #   Python autofill script (1648 lines, 26 functions)

  action-delete-circuits/              # Cleanup action
    config.yaml                        #   Action metadata
    script.py                          #   Python autofill script (152 lines, 5 functions)

  dashboard-mpls-service-circuits/     # Circuits-per-PE dashboard
    config.yaml                        #   Dashboard widget definitions
    circuits-per-switch.aql            #   AQL query for circuit status per device

  dashboard-mpls-service-customer-records/  # Customer records dashboard
    config.yaml                        #   Dashboard widget definitions
    customer-records.aql               #   AQL query for customer circuit inventory
```

## How It Works

### Provisioning Workflow (action-mpls-service-manager)

1. **Fetch inputs** — reads the selected customer/circuit/PE from the Service Manager Studio and the current state from the Configlet Studio
2. **Resolve PE identities** — looks up each PE's Loopback0 IP via the `router_bgp.router_id` tag for use in route distinguishers and ESI generation
3. **Validate** — checks multi-homing PE count, locked circuit status, and invalid combinations (e.g. BGP routing with SVI interface type)
4. **Clean up stale tags** — removes interface tags from any previous provisioning run (fetched once, applied per device)
5. **Build ESI prefix** — for multi-homed circuits, derives a deterministic ESI from the last two octets of both PE loopbacks
6. **Extract settings** — reads service-type-specific fields (DIA settings, VPN-V4 settings, etc.) into a unified settings dict
7. **Generate CLI** — dispatches to the appropriate builder function (`buildDiaCli`, `buildVpnV4Cli`, `buildL2EvpnCli`, `buildVplsCli`, `buildVpwsCli`) which generates EOS CLI configlets
8. **Merge and push** — combines the new circuit's CLI with existing circuits on the target devices, batch-assigns interface tags, and pushes to the Configlet Studio

### Deletion Workflow (action-delete-circuits)

1. Builds a fast lookup of `circuitId -> device names` from all customer circuits
2. Rebuilds the Configlet Studio inputs, keeping only services whose circuit still exists
3. Reconciles interface tags — deletes stale tags and re-asserts tags for active circuits

### Interface Tags

When interface tagging is enabled (Global Settings), the package tags each provisioned interface with:

- `Customer_Name` — customer name
- `Circuit_ID` — circuit/service identifier
- `Service_Type` — the service type (e.g. VPN-V4, VPWS)
- `Link-Type` — always set to `Customer`
- `Last-Modified` — timestamp of last provisioning
- `Connection_Type` — UNI or NNI

These tags power the two dashboards for circuit-per-device and customer record views.

## Code Architecture (action-mpls-service-manager)

The script is organized into six sections:

| Section | Lines | Functions | Purpose |
|---|---|---|---|
| **Tag Utilities** | 34-93 | `splitTagToDeviceNames`, `interfaceTags`, `clean_up_interface_tags` | Tag parsing, batch accumulation, stale tag cleanup |
| **CLI Generators** | 99-264 | `processFlexEncap`, `processStaticRoutes`, `processPrefixLists`, `processRouteMaps`, `processDiaRcf`, `processMplsRcfIn`, `processMplsRcfOut` | Generate individual EOS CLI blocks (encap, routes, prefix lists, route maps, RCF) |
| **Interface/ESI Helpers** | 270-370 | `processPortChannels`, `calculateEsi`, `buildEsiPrefix` | Port-Channel member config, ESI calculation, ESI prefix from PE loopbacks |
| **Service-Type Processors** | 376-756 | `processL2EvpnInterfaces`, `processMplsInterfaces` | Generate interface + BGP neighbor CLI for L2 EVPN and L3 MPLS service types |
| **Template Builders** | 759-1297 | `buildDiaCli`, `buildVpnV4Cli`, `buildL2EvpnCli`, `buildVplsCli`, `buildVpwsCli` | Assemble complete EOS configlets per service type using a shared context dict |
| **Orchestrator** | 1303-1648 | `getCustomerStdInputs`, `extractServiceSettings`, `processInputs`, `main` | Input extraction, settings parsing, and the main provisioning workflow |

## Configuration

### Global Settings (in the Service Manager Studio)

- **Local ASN** — the BGP autonomous system number for all circuits
- **BGP Session Tracking** — enables/disables `bgp session tracker TRACK-EVPN-PEERS` on interfaces (enabled by default)
- **Interface Tagging** — enables/disables dashboard interface tags (disabled by default)

### Studio IDs

The scripts reference two studio IDs:

- **Configlet Studio** (`cliStdID` in action-mpls-service-manager): `efb1783f-fd75-4165-92a9-434ed2edc2c0`
- **Configlet Studio** (`cliStdID` in action-delete-circuits): `9a0dd312-f056-49fa-a1b9-45b8905bb272`

These must match the actual studio IDs in your CloudVision deployment. If importing into a new environment, update these values in the respective `script.py` files.

### RCF (Route Control Functions)

RCF generation is currently disabled for all three functions. To enable:

- **DIA RCF**: remove `rcf = ""` line in `processDiaRcf()`
- **VPN-V4 RCF IN**: remove `rcf = ""` line in `processMplsRcfIn()`
- **VPN-V4 RCF OUT**: remove `rcf = ""` line in `processMplsRcfOut()`

## Installation

### Import into CloudVision

1. Navigate to **Studios > Packages** in CloudVision
2. Click **Import Package**
3. Upload `mpls-services_0.3.2.tar`
4. Verify the two studios and two dashboards appear

### Install into the arista repo (for development)

```bash
# From the repo root
tar xf mpls-services_0.3.2.tar -C cvp/app/changecontext/studios/
```

The package is registered in `cvp/app/changecontext/studios/pkgs.yaml`:

```yaml
mpls-services:
    - studio-mpls-service-configlets
    - studio-mpls-service-manager
```

## QoS

Each circuit can optionally have a QoS profile with:

- **QOS Type** — service level (A, B, or C)
- **Shape Rate** — in kbps (e.g. 100000 for 100M)
- **Policer Profile** — predefined bandwidth profile (100M through 10G)

When both shape rate and policer profile are set, the generated CLI includes:

```
service-profile USS-QOS-<level>
shape rate <rate>
policer profile <profile> input
```

## Version History

| Version | Changes |
|---|---|
| 0.3.2 | Current version. Reorganized code, bug fixes, performance improvements |
| 0.2.65 | Service type renames, layout dependency updates |
| 0.2.60 | Schema field reordering, YAML cleanup |
| 0.2.58 | Initial import into arista repo with human-readable directory names |
