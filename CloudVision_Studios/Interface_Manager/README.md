Interface Manager V2 Studio

  Overview

  Interface Manager V2 is a CloudVision Portal (CVP) studio package for declarative network interface and profile configuration across Arista devices. It provides a
  centralized, template-driven approach to managing device interfaces, supporting everything from simple access ports to complex multi-device MLAG deployments with
  advanced security and QoS policies.

  Key Features

  - Profile-based configuration — Define interface profiles once and apply them across hundreds of devices
  - Brownfield migration — Import existing interface configurations from device running-config via the Ports Table autofill action
  - Layer 2 — Access, trunk, and routed port modes with VLAN management, native VLAN, allowed VLANs, port-fast, BPDU guard
  - Layer 3 — IPv4/IPv6 addressing, VRF assignment, static routing
  - Link Aggregation — Port-channels, LACP, MLAG, multi-homing with auto port-channel numbering
  - Security — MAC-Sec, IP-Sec, 802.1X, port security, IP locking, IPv4/IPv6 ACLs
  - QoS — Policy maps, class maps, traffic shaping, bandwidth allocation
  - Multicast — PIM sparse-mode, IGMP, anycast RPs
  - Other — PTP, NAT, DHCP helpers, storm control, POE, logging, tagging profiles
  - Platform-aware — Automatically detects hardware platform and applies appropriate settings (TCAM profiles, reload delays, feature support)
  - Dashboards — Built-in AQL dashboards for viewing interfaces by device, profile, or type

  Package Contents

  ┌──────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────┐
  │        Component         │                                      Description                                       │
  ├──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ studio-interface-v2-pkg/ │ Studio definition — schema, layout, and Mako config template                           │
  ├──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ action-ports-table/      │ Autofill action to populate port tables from profiles, running-config, or manual entry │
  ├──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ action-stackids/         │ Autofill action to auto-assign switch IDs to stack members                             │
  ├──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ DevicesDashboard/        │ AQL dashboard — interfaces grouped by device                                           │
  ├──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ ProfileDashboard/        │ AQL dashboard — devices grouped by profile                                             │
  ├──────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────┤
  │ TypeDashboard/           │ AQL dashboard — interfaces grouped by type                                             │
  └──────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────┘

  Getting Started

  Installation

  1. Download or build the interface-v2-pkg.tar package
  2. In CVP, navigate to Provisioning > Studios > Package Management
  3. Upload the .tar file to install or upgrade the package

  Basic Workflow

  1. Create Profiles — Define one or more interface profiles under the profile sections:
    - General Profiles — VLAN/access/trunk/routed settings
    - Port Channel Profiles — LAG/LACP configuration
    - Multi-Homing Profiles — MLAG/ESI settings
    - Additional profiles for QoS, ACLs, MAC-Sec, IP-Sec, 802.1X, etc.
  2. Create a Profile of Profiles — Combine individual profiles into a named composite profile. This is what gets assigned to interfaces. For example, a "Server-Access"
  profile of profiles might reference a general profile for access VLAN settings, a port-channel profile for LAG, and a QoS profile.
  3. Add Sites and Device Groups — Organize your devices using the site/device group hierarchy:
    - Create a Site and assign devices using tag queries
    - Within a site, create Device Groups with their own tag queries
    - For stacked devices, define Stack Members with switch IDs
  4. Assign Interfaces — In the Interface Ranges (port table) for each device group:
    - Specify interface names or ranges (e.g., Ethernet1-24)
    - Assign a Profile of Profiles to each range
    - Optionally set per-interface overrides (speed, description, etc.)
  5. Use Autofill (Optional) — Run the Ports Table autofill action to populate interfaces automatically:
    - Generate — Create interface entries from profile definitions
    - Running-config — Import existing interfaces from device running-config (brownfield)
    - Clear — Remove all port table entries
  6. Build and Review — Build the workspace to generate EOS configuration. Review the generated config per device before submitting.

  VLAN Interfaces

  To configure SVI (VLAN interface) settings:
  1. Add entries under VLAN Interfaces in a device group
  2. Assign a Profile of Profiles with the desired Layer 3 settings
  3. Specify VLAN ID, IP addressing, VRF, and other attributes

  Tunnel Interfaces

  For IPSec tunnel configurations:
  1. Define an IP-Sec Profile with IKE policy, SA policy, and connection settings
  2. Add entries under Tunnel Interfaces in a device group
  3. Assign a Profile of Profiles that references the IP-Sec profile
  4. Configure tunnel source, destination, and underlay VRF

  Stack Configuration

  For devices in a stack (e.g., modular or virtual stacking):
  1. Add stack member entries under a device group
  2. Run the Stack IDs autofill action to auto-assign switch IDs
  3. In interface ranges, use the member number selector to target specific stack members or "all-switches"

  Input Hierarchy

  Sites
  └── Device Groups (matched by tag query)
      ├── Stack Members
      ├── Interface Ranges (port table)
      │   ├── Member Number (which stack members)
      │   ├── Interface Name/Range
      │   ├── Profile of Profiles
      │   └── Per-interface overrides
      ├── VLAN Interfaces
      ├── Tunnel Interfaces
      └── VLAN Collection

  Profile Hierarchy

  Profile of Profiles
  ├── General Profile (access/trunk/routed)
  ├── Port Channel Profile (LAG/LACP)
  ├── Multi-Homing Profile (MLAG/ESI)
  ├── QoS Profile
  ├── ACL Profile
  ├── MAC-Sec Profile
  ├── IP-Sec Profile
  ├── 802.1X Profile
  ├── Port Security Profile
  ├── PTP Profile
  ├── PIM/Multicast Profile
  ├── IGMP Profile
  ├── IP Locking Profile
  ├── NAT Profile
  ├── Storm Control Profile
  ├── Logging Profile
  ├── POE Profile
  └── Tagging Profile

  Development

  Running Tests

  Run all interface-v2-pkg tests:
  go test -tags integration,studio,yaml ./cvp/app/changecontext/test --run TestStudioYaml -v \
    -test-suite studio-interface-v2-pkg

  Run a single test:
  go test -tags integration,studio,yaml ./cvp/app/changecontext/test --run TestStudioYaml -v \
    -test-file interface-manager-v2-basic-autofill-test.yaml

  Debugging flags: -show-logs, -show-tags, -show-configs

  Building the Package

  cd arista/cvp/app/changecontext/studios
  tar cf interface-v2-pkg.tar interface-v2-pkg/

  Changelog

  Version 2.34.4

  Bug Fixes
  - Fixed missing raise keyword for ActionFailed exception in ports action
  - Fixed HTTP error handling — caught correct exception type (RequestException instead of RpcError)
  - Fixed IPSec integrity field rendered as encryption instead of integrity in IKE policy
  - Removed duplicate dpd key in IPSec profile dict literal
  - Fixed pylint no-else-raise warning

  Security
  - Enabled TLS verification on HTTP requests carrying Bearer tokens

  Improvements
  - Removed vendored setStudioInputs — now uses library import from cloudvision.cvlib
  - Replaced ~190 lines of hardcoded platform_settings with device_capabilities from cloudvision.cvlib.device
  - O(1) profile lookups via profileOfProfilesMap dict, replacing O(n) linear scans across 11 functions
  - Refactored profile lookup pattern using walrus operator (:=) with early return
  - Updated copyright year from 2024 to 2025

  Test Coverage
  - Added integrity field coverage to IPSec tunnel test
