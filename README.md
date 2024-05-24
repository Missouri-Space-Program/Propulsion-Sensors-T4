# Sensor Configuration With Labjack T4

## Prerequisites
- Download & install the LJM library at [Labjack's Website](https://labjack.com/pages/support/software?doc=%2Fsoftware-driver%2Finstaller-downloads%2Fljm-installation-instructions%2F)
- Download all packages with `pip install -r requirements.txt`

To use over Ethernet, plug into your machine. The T4 currently lives on 192.168.20.3
To access it, you will need to configure a static IP on your own machine. Go into your machine's wired NIC and configure the following static settings

```
IP Address: 192.168.20.2
Subnet: 255.255.255.0
Gateway: 192.168.20.1
```
## What needs to be done:

- ~~Buy LJTick-InAmp to configure Load Cell, see [here](https://labjack.com/pages/support?doc=/app-notes/sensor-types-app-note/bridge-circuits-app-note/#section-header-two-ocsys) for more information~~
- Configure power source for T4. Purchased buck converter for use to step down battery voltage. Need output to be USB-type B 5v-2.1A (battery should have plenty of amps)
- ~~Figure out our ethernet setup. Category 5 cabling & 10BASE/T calls for a maximum length of 100m so we will need to figure out how to amplify the signal to go greater than this, most likely a ethernet repeater. We will have to cut our current spool in half to allow a switch/repeater to be placed in the middle. We currently don't use this bc we don't send packets, just a signal to ignite the motor. Due to the T4 sending actual packets, we need to follow the Cat5 standards.~~
- ~~We must cut our ethernet spool at 200ft (~60m) and add RJ45 to either side. Do recon at RTF and see if we can power the switch through an external outlet, otherwise, we need the battery and a connector to the switch. We will use the 200ft section from the test stand to the building (hopefully), place the switch there, and have the rest of the spool from there to the safe distance where we stand for tests.~~ Ethernet cable spliced & ready, confirmed working with switch in between. Outlet exists on outside of RTF, so we will power switch there.
- ~~Once both sensors are read through command line~~, start writing GUI, with graphs and save to file capabilities.
- Optimize code. Ideally like > 200 samples/second, but we can get by with less. At a MINIMUM of 100 samples/sec. This will need to be done to ensure we get solid data.
