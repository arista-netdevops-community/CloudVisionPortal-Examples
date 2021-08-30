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
| Spine-Number | Spine-Number:1 | For a spine device, its number Each spine must have a unique number. |
| Leaf-Domain | Leaf-Domain:1 | Specifies the leafs within a common AS, which is usually an MLAG pair of leafs. The value must be an integer. Note: This tag is only necessary for MLAG peer relevant configuration.|
| Leaf-Number | Leaf-Number:1 | For a leaf device, its number. Each leaf must have a unique number. <br> Leaf pairs are assumed to be numbered consecutively starting with an odd number (e.g. the device tagged Leaf-Number:9 and the device tagged Leaf-Number:10 are two devices in an MLAG pair of leafs).<br> If a leaf is not part of an MLAG pair, just use one number of the odd-even pair and don’t use the other number for another leaf (e.g. the device tagged Leaf-Number:1 will be configured as a standalone leaf if no other device is tagged Leaf-Number:2). |

> Note: If you do not want to use the L3 Leaf-Spine Fabric Studio, then you will need to create these tags before configuring the EVPN Services Studio.