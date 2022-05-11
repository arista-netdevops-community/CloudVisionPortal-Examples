# Connected Endpoints - Beta
## This studio is in beta, it can and most likely will change

## Summary
The Connected Endpoints studio allows for configuration of L2 interfaces to end hosts and outbound connections alike. Eth and PortChannel interfaces are both configurable on a given range of Eth interfaces, with features like PTP, STP, QOS and more.

## Configuration
Profiles can be created to apply a template of an interface configuration for multiple devices with minor changes on each. Anything configured at the profile will apply to the adapter the profile is applied to. Any changes made at the adapter level have a higher priority than those at the profile lever at build time.

Dot1x is the only global config generated. Dot1x configurations will generate the global config necesary for their operation, except a RADIUS server.
