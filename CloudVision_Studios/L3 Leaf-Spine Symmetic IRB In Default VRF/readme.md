Use case: For customer with no multi-tenancy, all routing in the default vrf.

Changes: This removes the route-map in BGP "RM-CONN-BGP" and its associated prefix-list "PL-LOOPBACKS-EVPN-OVERLAY". Instead, "redistribute-connected" will be used in BGP without a route-map. For a full understanding of this deployment, refer to the EVPN Symmetric IRB in Default VRF deployment solution.

Note: This will allow all P2P links to be advertised in the underlay. To prevent this, create a route-map permitting only Loopback IP space in the underlay peer-group. (i.e. neighbor UNDERLAY_SPINE_V4 route-map UNDERLAY_ONLY out). 

