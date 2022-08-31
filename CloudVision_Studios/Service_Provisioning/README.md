# Service Provisioning Studio
## Summary
The Service Provisioning studio should be run after the L3 Leaf Spine Studio which will provision the fabric underlay and set up for overlay services.  This studio depends upon tags created and applied in the L3 Leaf Spine studio.

This studio supports several features:
- Creation of L3 VRFs with specified route distinguisher, route target, and optional leaking to and from vpn-ipv4 
- Creation of L2 VLANs with specified VLAN id, optional SVI provisioning with ipv4/ipv6 addressing, basic multicast configuration, and dhcp relaying for both address families.
- Per VRF service loopback interfaces and addresses 
- Configuration of L2-only vlan-aware-bundles with specified RD and RT values

The studio will also allow for specifying a new tag of Border-Leaf allowing for EVPN fabric edge devices which do not have anycast gateways enabled on them, but advertise a default route into the fabric

