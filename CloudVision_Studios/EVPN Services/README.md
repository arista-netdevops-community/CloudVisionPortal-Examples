# EVPN Services Studio
## Summary
The EVPN Services Studio allows you to deploy L2 and L3 network services. These services are applied to tenants that you create. Each tenant shares a common Virtual Network Identifier (VNI) range for MAC-VRF assignment.  

> Note: EVPN Services Studio is designed to implement Day 2 operations on top of the Day 1 fabric created with the Layer 3 Leaf-Spine Studio.

## Required Tags
The following tags are required for this Studio. They will already be in place if you have deployed an L3 leaf-spine fabric with the Layer 3 Leaf-Spine Fabric Studio.

| Tag | Example | Description |
| ----------- | ----------- | ----------- |
| router_bgp.as | router_bgp.as:65050 | Defines the BGP ASN that the switch will use when configuring overlay VRFs, VLANs, and VLAN aware bundles. |
| router_bgp.router_id | router_bgp.router_id:172.16.0.1 | Defines the BGP Router ID used on the switch and makes up part of the route-distinguisher and route-target fields. |
| mlag_configuration.peer_link | mlag_configuration.peer_link:Port-Channel2000 | Specifies the MLAG peer link used on a switch that has an MLAG peer. |
| NodeId | NodeId:1 | This is the node id per node type (leaf, spine, super-spine, or l2-leaf) per DC-Pod (or per DC in case of super-spine). |
| NetworkServices | NetworkServices:L2, NetworkServices:L3 | When a NetworkServices tag with an L2 value is applied to a device, it signifies that the device operates at layer2. When a NetworkServices tag with an L3 value is applied to a device, it signifies that the device operates at layer3. A device operating at both layer 2 and layer 3 should have both network_service tag values applied to it. |
| Vtep | Vtep:True, Vtep:False | Determines if the device is a VTEP or not.  If the device is not a VTEP, the Vtep tag is not necessary. |

> Note: If you do not want to use the L3 Leaf-Spine Fabric Studio, then you will need to create and apply these tags before configuring the EVPN Services Studio.