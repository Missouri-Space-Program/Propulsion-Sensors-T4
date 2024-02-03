from labjack import ljm
TRANSDUCERMINVOLTAGE = 0.5
TRANSDUCERMAXVOLTAGE = 4.5
TRANSDUCERMAXPRESSURE = 1600 #In PSI
TRANSDUCERSCALINGFACTOR = TRANSDUCERMAXPRESSURE / (TRANSDUCERMAXVOLTAGE-TRANSDUCERMINVOLTAGE)
# Open first found LabJack
handle = ljm.openS("ANY","ANY","192.168.20.3")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# AIN0 (pressure transducer):
#     The T4 only has single-ended analog inputs.
#     The range of AIN0-AIN3 is +/-10 V.
#     The range of AIN4-AIN11 is 0-2.5 V.
#     Resolution index = 0 (default)
#     Settling = 0 (auto)
aNames = ["AIN0_RESOLUTION_INDEX", "AIN0_SETTLING_US"]
aValues = [0, 0]
numFrames = len(aNames)
ljm.eWriteNames(handle,numFrames,aNames,aValues)
pressVoltage = 0.0
pressure = 0.0
pressAdjVoltage = 0.0
counter = 0

#AIN5 (Load Cell)

loadVoltage = 0.0
loadAdjVoltage = 0.0
load = 0.0
while(True):
    pressVoltage = ljm.eReadName(handle,"AIN0")
    loadVoltage = ljm.eReadName(handle,"AIN5")
    pressAdjVoltage = pressVoltage - TRANSDUCERMINVOLTAGE
    pressure = pressAdjVoltage * TRANSDUCERSCALINGFACTOR
    #1.25 and 201 taken from dip switches active on the LJ-Tick-InAmp. For more info see https://labjack.com/pages/support?doc=/datasheets/accessories/ljtick-inamp-datasheet/
    loadAdjVoltage = (loadVoltage - 1.25) / 201
    #Load = RatedLoad *(VAIN- Voffset)/ (gain * Sensitivity * Vexc) in kilos
    #our load cell's senitivity is 2 mV/V
    #need to figure out Vexc, which is the excitition of the load cell circuit
    Vexc = 2.5
    #load = 500 * (loadVoltage - 1.25) / (201 * 2 * Vexc)
    load = 500 * loadAdjVoltage / (2 * 2.5)
    #found by calculating the slope and intercept between two known weights and the adjusted voltage
    calibratedLoad = 92290.3226 * loadAdjVoltage - 2.5356
    print("  %d  Raw Voltage - %f, Adjusted Voltage : %f, Pressure (PSI): %f" % (counter, pressVoltage, pressAdjVoltage, pressure))
    print("  %d  Raw Voltage - %f, Adjusted Voltage : %f, Load (kg) : %f " % (counter, loadVoltage, loadAdjVoltage, calibratedLoad))
    counter += 1