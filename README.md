# Setup for Labjack T4

To use over Ethernet, plug into your machine. The T4 currently lives on 192.168.20.3
To access it, you will need to configure a static IP on your own machine. Go into your machine's wired NIC and configure the following static settings

```
IP Address: 192.168.20.2
Subnet: 255.255.255.0
Gateway: 192.168.20.1
```
What needs to be done:

- Buy LJTick-InAmp to configure Load Cell, see https://labjack.com/pages/support?doc=/app-notes/sensor-types-app-note/bridge-circuits-app-note/#section-header-two-ocsys for more information
- Configure power source. Will probably need to buy a dc-dc stepdown converter like our current setup. Need output to be USB-type B 5v-2.1A
- Figure out our ethernet setup. Category 5 cabling & 10BASE/T calls for a maximum length of 100m so we will need to figure out how to amplify signal to go greater than this, most likely a ethernet repeater. We will have to cut our current spool in half to allow for a switch/repeater to be placed in the middle. We currently don't use this bc we don't send packets, just a signal to ignite the motor. Due to the T4 sending actual packets, we need to follow the Cat5 standards.
- Once both sensors are read through command line, start writing GUI, with graphs and save to file capabilities.
