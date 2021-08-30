# L3 Leaf-Spine Fabric Studio
## Summary
The L3 Leaf-Spine Studio configures Day 1 deployment of the network, and EVPN Services configures Day 2 operations.

> Note: In its beta-version, this studio does not currently support the configuration of super-spines, multiple parallel transit connections between the same leaf and spine switches, detect/set speed on interfaces, and doesn’t support recirc channels on platforms that require them for VXLAN routing.

The Studio has been designed to support the following Arista validated L3 leaf-spine design:
![L3 Leaf-Spine Toplogy](./images/l3-leaf-spine.png)

> Note: In order to build this design, you’ll first need to use the Inventory and Topology Studio to either accept the LLDP derived topology connections or manually add devices and interface connections.

## Required Tags
You’ll need to have the following device tags in place before you can configure the inputs in this Studio. You can create these tags within the same Workspace by accessing Tags.

| Tag | Example | Description |
| ----------- | ----------- | ----------- |
| DC | DC:DC1 | DC defines the data center that is being configured. |
| DC-Pod | DC-Pod:DC1 | Data center pod name. |
| Role | Role:Leaf, Role:Spine | Device Role. Can either be a leaf or spine. |
| Spine-Number | Spine-Number:1 | For a spine device, its number Each spine must have a unique number. |
| Leaf-Domain | Leaf-Domain:1 | Specifies the leafs within a common AS, which is usually an MLAG pair of leafs. The value must be an integer. |
| Leaf-Number | Leaf-Number:1 | For a leaf device, its number. Each leaf must have a unique number. <br> Leaf pairs are assumed to be numbered consecutively starting with an odd number (e.g. the device tagged Leaf-Number:9 and the device tagged Leaf-Number:10 are two devices in an MLAG pair of leafs).<br> If a leaf is not part of an MLAG pair, just use one number of the odd-even pair and don’t use the other number for another leaf (e.g. the device tagged Leaf-Number:1 will be configured as a standalone leaf if no other device is tagged Leaf-Number:2). |

Tag placement is illustrated in the following diagram:
![L3 Leaf-Spine Toplogy](./images/l3-leaf-spine-tags.png)