Use case: For customer with no multi-tenancy, all routing in the default vrf.

Caution: This will allow all P2P links to be advertised in the underlay because a requirement for creating a VRF default is that
there can be no route-map on redistribute connected. To prevent this, create a route-map permitting only Loopback IP space in the
underlay. (i.e. neighbor UNDERLAY_SPINE_V4 route-map UNDERLAY_ONLY out). For a full understanding of this deployment, refer to the EVPN Symmetric IRB in Default VRF deployment within the Arista Professional Services EVPN Solution Guide.

