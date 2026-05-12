# Flow Monitoring

## Summary
The Flow Monitoring studio configures IPFIX and/or sFlow flow monitoring on Arista EOS devices. It uses a dual-resolver approach with separate device set assignments for IPFIX and sFlow, ensuring no device is assigned to both protocols simultaneously.

## Features
- **IPFIX Support**: Configures `flow tracking sampled` with tracker, exporter, collector, and source interface settings
- **sFlow Support**: Configures sFlow sampling, polling interval, source interface, and collector destination
- **Dual-Protocol Validation**: Prevents a device from being assigned to both IPFIX and sFlow profiles
- **Optional Loopback Creation**: Optionally generates loopback interface configuration for use as the source interface
- **Sensible Defaults**: Default sample rate of 1,000,000 and standard ports (IPFIX: 4739, sFlow: 6343)

## Configuration

### IPFIX Device Sets
Assign IPFIX flow monitoring to a group of devices via tag-based device queries. Each assignment includes:

| Field | Description | Default |
|-------|-------------|---------|
| Source Interface | Interface for IPFIX local interface (e.g. Loopback0) | Required |
| Sample Rate | Packet sample rate (1 in N). EOS range: 1-16,777,215 | 1,000,000 |
| Collector Address | IPFIX collector IP. Use 127.0.0.1 to stream to CVP/CVaaS | 127.0.0.1 |
| Tracker Name | Name of the flow tracker (e.g. tr1) | Required |
| Exporter Name | Name of the flow exporter (e.g. tr1) | Required |
| IPFIX Collector Port | Destination port for IPFIX export | 4739 |

### sFlow Device Sets
Assign sFlow flow monitoring to a group of devices via tag-based device queries. Each assignment includes:

| Field | Description | Default |
|-------|-------------|---------|
| Source Interface | Interface for sFlow source (e.g. Loopback0) | Required |
| Sample Rate | Packet sample rate (1 in N). EOS range: 1-4,294,967,295 | 1,000,000 |
| Collector Address | sFlow collector IP. Use 127.0.0.1 to stream to CVP/CVaaS | 127.0.0.1 |
| sFlow Polling Interval | Counter sampling interval in seconds | 10 |
| sFlow Collector Port | Destination port for sFlow export | 6343 |

### Optional Loopback Creation
Both IPFIX and sFlow sections include an optional loopback interface group. When enabled, the studio generates the loopback interface configuration:

| Field | Description |
|-------|-------------|
| Create Loopback Interface | Toggle to generate loopback config |
| Loopback Number | Interface number (0-8191) |
| Loopback Description | Optional description |
| Loopback IP Address | IP in CIDR notation (e.g. 81.81.81.81/32) |

## Example Output

### IPFIX
```
interface Loopback100
   description ipfix-source
   ip address 81.81.81.81/32
!
flow tracking sampled
   sample 1000000
   tracker tr1
      exporter tr1
         collector 127.0.0.1 port 4739
         local interface Loopback100
   no shutdown
```

### sFlow
```
interface Loopback0
   description sflow-source
   ip address 10.10.10.10/32
!
sflow sample 1000000
sflow polling-interval 10
sflow source-interface Loopback0
sflow destination 127.0.0.1 6343
sflow run
```

## Notes
- Sample rates of 65,535 or less when streaming to CVP/CVaaS may cause flow rate limiting
- IPFIX uses opinionated `flow tracking sampled` mode (hardware 1:1 is not supported)
- `sflow run` and IPFIX `no shutdown` are always rendered to activate the feature
- Removing a device from the profile assignment is how you disable monitoring
