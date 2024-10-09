from labjack import ljm
import dearpygui.dearpygui as dpg
import time
import threading
import csv
from scipy import integrate
import os
import numpy as np
TRANSDUCERMINVOLTAGE = 0.5
TRANSDUCERMAXVOLTAGE = 4.5
TRANSDUCERMAXPRESSURE = 1600 #In PSI
TRANSDUCERSCALINGFACTOR = TRANSDUCERMAXPRESSURE / (TRANSDUCERMAXVOLTAGE-TRANSDUCERMINVOLTAGE)
SAMPLES = 5

igniter_armed = False
countdown_active = False
recording_data = False
decreasing = False
# Open first found LabJack
handle = ljm.openS("ANY","ANY","ANY")
ljm.eWriteName(handle,"DAC0",0.0)
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
aNames = ["AIN5_RESOLUTION_INDEX", "AIN5_SETTLING_US"]
aValues = [0, 0]
numFrames = len(aNames)
ljm.eWriteNames(handle,numFrames,aNames,aValues)
loadVoltage = 0.0
loadAdjVoltage = 0.0
load = 0.0
# while(True):
#     #pressVoltage = ljm.eReadName(handle,"AIN0")
#     #loadVoltage = ljm.eReadName(handle,"AIN5")
#     avgCounter = 0
#     pressVoltageSum = 0.0
#     loadVoltageSum = 0.0
#     #taking average of specified sample number
#     while(avgCounter < SAMPLES):
#       pressVoltageSum += ljm.eReadName(handle,"AIN0")
#       loadVoltageSum += ljm.eReadName(handle,"AIN5") 
#       avgCounter += 1

#     pressVoltage = pressVoltageSum / SAMPLES
#     loadVoltage = loadVoltageSum / SAMPLES
#     pressAdjVoltage = pressVoltage - TRANSDUCERMINVOLTAGE
#     pressure = pressAdjVoltage * TRANSDUCERSCALINGFACTOR
#     #1.25 and 201 taken from dip switches active on the LJ-Tick-InAmp. For more info see https://labjack.com/pages/support?doc=/datasheets/accessories/ljtick-inamp-datasheet/
#     loadAdjVoltage = (loadVoltage - 1.25) / 201
#     #Load = RatedLoad *(VAIN- Voffset)/ (gain * Sensitivity * Vexc) in kilos
#     #our load cell's senitivity is 2 mV/V
#     #Excition voltage available on Input 6.
#     Vexc = ljm.eReadName(handle, "AIN6")
#     print(Vexc)
#     #load = 500 * (loadVoltage - 1.25) / (201 * 2 * Vexc)
#     load = 500 * loadAdjVoltage / (2 * 2.5)
#     #found by calculating the slope and intercept between two known weights and the adjusted voltage
#     calibratedLoad = 100387.5 * loadAdjVoltage - 3.8069375
#     print("  %d  Raw Voltage - %f, Adjusted Voltage : %f, Pressure (PSI): %f" % (counter, pressVoltage, pressAdjVoltage, pressure))
#     print("  %d  Raw Voltage - %f, Adjusted Voltage : %f, Load (kg) : %f " % (counter, loadVoltage, loadAdjVoltage, calibratedLoad))
#     counter += 1


# Initialize data storage
load_cell_data = []
pressure_data = []
time_data = []
max_points = 500  # Maximum number of points to display on the plot
recorded_time = []
recorded_load_cell = []
recorded_pressure = []
decr_time = []
decr_thrust = []
data_dict = {}
# Function to read data from LabJack
def read_data():
    avgCounter = 0
    pressVoltageSum = 0.0
    loadVoltageSum = 0.0
    #taking average of specified sample number
    while(avgCounter < SAMPLES):
      pressVoltageSum += ljm.eReadName(handle,"AIN0")
      loadVoltageSum += ljm.eReadName(handle,"AIN5") 
      avgCounter += 1

    pressVoltage = pressVoltageSum / SAMPLES
    loadVoltage = loadVoltageSum / SAMPLES
    pressAdjVoltage = pressVoltage - TRANSDUCERMINVOLTAGE
    pressure = pressAdjVoltage * TRANSDUCERSCALINGFACTOR
    #1.25 and 201 taken from dip switches active on the LJ-Tick-InAmp. For more info see https://labjack.com/pages/support?doc=/datasheets/accessories/ljtick-inamp-datasheet/
    loadAdjVoltage = (loadVoltage - 1.25) / 201
    #Load = RatedLoad *(VAIN- Voffset)/ (gain * Sensitivity * Vexc) in kilos
    #our load cell's senitivity is 2 mV/V
    #Excition voltage available on Input 6.
    Vexc = ljm.eReadName(handle, "AIN6")
    #print(Vexc)
    #load = 500 * (loadVoltage - 1.25) / (201 * 2 * Vexc)
    #load = 500 * loadAdjVoltage / (2 * 2.5)
    #found by calculating the slope and intercept between two known weights and the adjusted voltage
    calibratedLoad = 100387.5 * loadAdjVoltage - 3.8069375
    #calibration value is set in kg, to get the reading in N, need to multiply by 9.81. Will check calibration factor when back in shop.
    calibratedLoad = calibratedLoad * 9.81
    return calibratedLoad, pressure

def determine_motor_class(impulse):
  if impulse <= 2.5:
    return 'A'
  elif impulse <= 5:
    return 'B'
  elif impulse <= 10:
    return 'C'
  elif impulse <= 20:
    return 'D'
  elif impulse <= 40:
    return 'E'
  elif impulse <= 80:
    return 'F'
  elif impulse <= 160:
    return 'G'
  elif impulse <= 320:
    return 'H'
  elif impulse <= 640:
    return 'I'
  elif impulse <= 1280:
    return 'J'
  elif impulse <= 2560:
    return 'K'
  elif impulse <= 5120:
    return 'L'
  elif impulse <= 10240:
    return 'M'
  elif impulse <= 20480:
    return 'N'
  elif impulse <= 40960:
    return 'O'
  elif impulse <= 81920:
    return 'P'
  return ""

def save_to_file(sender, app_data, user_data):
  path = app_data['file_path_name']
  curve_time = data_dict['time']
  curve_thrust = data_dict['thrust']
  curve_press = data_dict['pressure']
  cur_time = time.time()
  with open(os.path.join(path, "TestData" + str(cur_time) + ".csv"), 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['time','thrust (N)', 'pressure (PSI)'])
    for timer, thrust, press in zip(curve_time, curve_thrust, curve_press):
      writer.writerow([timer,thrust,press])
  time.sleep(0.05)
  dpg.output_frame_buffer(os.path.join(path, "Test" + str(cur_time) + "Plots_Data.png"))

def plot_and_write(load_cell, pressure, timer):
  global data_dict
  curve_time = []
  curve_press = []
  curve_thrust = []
  first = False
  time_start = 0.0
  cur_time = time.time()
  with open("data_backup_full_recording" + str(cur_time) + ".csv", 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    writer.writerow(['time','thrust (N)', 'pressure (PSI)'])
    for times, thrust, press in zip(timer, load_cell, pressure):
      writer.writerow([times,thrust,press])
  # need to format data to only capture thrust curve for plots, etc
  for ti, thr, pr in zip(timer, load_cell, pressure):
    if thr > 25:
      if not first:
         #first value, get time at this point and save
        time_start = ti
        first = True
        curve_time.append(0)
      else:
        t = ti - time_start
        curve_time.append(t)
      #only get data when thrust is greater than 50 N
      curve_thrust.append(thr)
      curve_press.append(pr)
  data_dict['time'] = curve_time
  data_dict['thrust'] = curve_thrust
  data_dict['pressure'] = curve_press
  dpg.set_item_user_data("save_data", data_dict)
  #now let's calculate burn time, avg Thrust, Avg Pressure, Max Thrust, Impulse
  burn_time = curve_time[len(curve_time)-1]
  avg_thrust = sum(curve_thrust) / len(curve_thrust)
  avg_pressure = sum(curve_press) / len(curve_press)
  max_thrust = max(curve_thrust)
  max_pressure = max(curve_press)
  total_impulse = integrate.simpson(curve_thrust,x=curve_time)
  motor_class = determine_motor_class(total_impulse)
  dpg.configure_item("save_data", show=True)
  with dpg.window(label="Plots/Results", width=640,height=595,pos=[640,125], no_close=True, no_scrollbar=True,no_move=True, no_collapse=True, tag="plots_results"):
    with dpg.plot(label='Thrust Data', width=610,height=225, anti_aliased=True, use_local_time=True):
      thrust_x = dpg.add_plot_axis(dpg.mvXAxis, label='Time (s)',tag='thrust_x_recorded')
      thrust_y = dpg.add_plot_axis(dpg.mvYAxis, label='Thrust (N)', tag='thrust_y_recorded')
      dpg.add_line_series(curve_time,curve_thrust,label='Thrust',parent='thrust_y_recorded',tag='thrust_curve_recorded')
      dpg.bind_item_theme("thrust_curve_recorded","thrust_theme")
    with dpg.plot(label='Pressure Data',width=610,height=225, anti_aliased=True):
      pressure_x = dpg.add_plot_axis(dpg.mvXAxis, label='Time (s)',tag='pressure_x_recorded')
      pressure_y = dpg.add_plot_axis(dpg.mvYAxis, label='Pressure (PSI)', tag='pressure_y_recorded')
      dpg.add_line_series(curve_time,curve_press,label='Pressure',parent='pressure_y_recorded',tag='pressure_curve_recorded')
      dpg.bind_item_theme("pressure_curve_recorded","pressure_theme")
    dpg.bind_font(default_font)
    dpg.add_text("Average Thrust: " + '{0:,.2f}'.format(avg_thrust) + " N",pos=[20,490])
    dpg.add_text("Max Thrust: " + '{0:,.2f}'.format(max_thrust) + " N",pos=[20,510])
    dpg.add_text("Average Pressure: " + '{0:,.2f}'.format(avg_pressure) + " PSI",pos=[220,490])
    dpg.add_text("Max Pressure: " + '{0:,.2f}'.format(max_pressure) + " PSI",pos=[220,510])
    dpg.add_text("Burn Time: " + '{0:.2f}'.format(burn_time) + " s",pos=[420,490])
    dpg.add_text("Total Impulse: " + '{0:.2f}'.format(total_impulse) + " Ns",pos=[420,510])
    dpg.add_text("Motor Designation: " + motor_class + '{0:.0f}'.format(avg_thrust),pos=[220,530])

def check_decreasing(time, thrust, order=1):
  result = np.polyfit(time, thrust,order)
  slope = result[-2]
  if slope < 0:
    return True
  return False

# Function to update the data and plot
def update_data():
  global decreasing
  global recording_data
  start_time = time.time()
  while True:
    calLoad, pressure = read_data()
    
    current_time = time.time() - start_time
    load_cell_data.append(calLoad)
    pressure_data.append(pressure)
    time_data.append(current_time)
    decr_time.append(current_time)
    decr_thrust.append(calLoad)
    if len(load_cell_data) > max_points:
      load_cell_data.pop(0)
      pressure_data.pop(0)
      time_data.pop(0)
    if len(decr_thrust) > 50:
      decr_thrust.pop(0)
      decr_time.pop(0)
    if recording_data:
      recorded_load_cell.append(calLoad)
      recorded_pressure.append(pressure)
      recorded_time.append(current_time)
      if len(recorded_load_cell) > 100 and check_decreasing(decr_time,decr_thrust):
        #decreasing
        decreasing = True
      if decreasing and recorded_load_cell[-2] > 25 and recorded_load_cell[-1] < 25:
        #hit cut off of 25 N and decreasing, stop recording and begin plots
        recording_data = False
        plot_and_write(recorded_load_cell, recorded_pressure, recorded_time)
    # Update plot data
    dpg.set_value('thrust_curve', [time_data, load_cell_data])
    dpg.fit_axis_data('thrust_x')
    dpg.fit_axis_data('thrust_y')

    dpg.set_value('pressure_curve', [time_data, pressure_data])
    dpg.fit_axis_data('pressure_x')
    dpg.fit_axis_data('pressure_y')
    time.sleep(0.0025)  # Update rate of 250 Hz

def arm_igniter():
  global igniter_armed
  global countdown_active
  global timer
  if igniter_armed is False:
    igniter_armed = True
    dpg.set_value("arm_status","Igniter Status: ARMED")
    dpg.bind_item_theme("arm_status",armed_status)
  elif igniter_armed is True and countdown_active is True:
    igniter_armed = False
    dpg.set_value("arm_status","Igniter Status: UNARMED")
    dpg.bind_item_theme("arm_status",disarmed_status)
    countdown_active = False
    dpg.set_value("countdown_status", "Countdown Status: Canceled Countdown!")
    timer.cancel()
    timer = threading.Timer(5.0, ignite_motor)
  elif igniter_armed is True:
    igniter_armed = False
    dpg.set_value("arm_status","Igniter Status: UNARMED")
    dpg.bind_item_theme("arm_status",disarmed_status)

def start_stop_countdown(active_timer):
  global countdown_active
  global timer
  if countdown_active is False and igniter_armed is True:
    countdown_active = True
    dpg.set_value("countdown_status", "Countdown Status: Countdown Started, Igniting in 5 seconds!")
    timer.start()
  elif countdown_active is False and igniter_armed is False:
    dpg.set_value("countdown_status", "Countdown Status: Unable to start count, Igniter Unarmed!")
  elif countdown_active is True:
    dpg.set_value("countdown_status", "Countdown Status: Canceled Countdown!")
    countdown_active = False
    timer.cancel()
    timer = threading.Timer(5.0,ignite_motor)

def ignite_motor():
  global countdown_active 
  global timer
  global recording_data
  global handle
  timer = threading.Timer(5.0,ignite_motor)
  countdown_active = False
  dpg.set_value("countdown_status","Countdown Status: Igniting Motor!")
  #write 5V to igniter wire
  recording_data = True
  ljm.eWriteName(handle,"DAC0",5.0)
  #wait 5 seconds, return back to 0V
  threading.Timer(5,ljm.eWriteName(handle,"DAC0",0.0))

dpg.create_context()
dpg.add_file_dialog(
    directory_selector=True, show=False, callback=save_to_file, tag="file_dialog_id", width=700 ,height=400)
with dpg.theme() as disarmed_status:
    with dpg.theme_component(dpg.mvAll):
       dpg.add_theme_color(dpg.mvThemeCol_Text, [0,255,0])

with dpg.theme() as armed_status:
    with dpg.theme_component(dpg.mvAll):
       dpg.add_theme_color(dpg.mvThemeCol_Text, [255,0,0])

width, height, channels, data = dpg.load_image("assets/MSPLogoWhite.png")
with dpg.texture_registry(show=True):
    dpg.add_static_texture(width=width, height=height, default_value=data, tag="MSP_image_tag")

with dpg.font_registry():
   default_font = dpg.add_font("assets/Roboto-Regular.ttf",15)
   nasa_font = dpg.add_font("assets/nasalization-rg.otf",30)

with dpg.window(label="Live Data", width=640,height=720, no_close=True, no_scrollbar=True,no_move=True, no_collapse=True):
  with dpg.theme(tag="thrust_theme"):
      with dpg.theme_component(dpg.mvLineSeries):
          dpg.add_theme_color(dpg.mvPlotCol_Line, (224, 86, 44), category=dpg.mvThemeCat_Plots)
  with dpg.theme(tag="pressure_theme"):
      with dpg.theme_component(dpg.mvLineSeries):
          dpg.add_theme_color(dpg.mvPlotCol_Line, (46, 111, 232), category=dpg.mvThemeCat_Plots)
  with dpg.plot(label='Thrust Data', width=625,height=320, anti_aliased=True, use_local_time=True):
    thrust_x = dpg.add_plot_axis(dpg.mvXAxis, label='Time since program start (s)',tag='thrust_x')
    thrust_y = dpg.add_plot_axis(dpg.mvYAxis, label='Thrust (N)', tag='thrust_y')
    dpg.add_line_series(x=list(time_data),y=list(load_cell_data),label='Thrust',parent='thrust_y',tag='thrust_curve')
    dpg.bind_item_theme("thrust_curve","thrust_theme")

  with dpg.plot(label='Pressure Data',width=625,height=320, anti_aliased=True):
    pressure_x = dpg.add_plot_axis(dpg.mvXAxis, label='Time since program start (s)',tag='pressure_x')
    pressure_y = dpg.add_plot_axis(dpg.mvYAxis, label='Pressure (PSI)', tag='pressure_y')
    dpg.add_line_series(x=list(time_data),y=list(pressure_data),label='Pressure',parent='pressure_y',tag='pressure_curve')
    dpg.bind_item_theme("pressure_curve","pressure_theme")
  dpg.bind_font(default_font)

with dpg.window(label="Options", width=640,height=125,pos=[640,0], no_close=True, no_scrollbar=True,no_move=True, no_collapse=True):
  dpg.add_button(label="Save Data", width=150, height=68, tag="save_data", pos=[312,29], callback=lambda: dpg.show_item("file_dialog_id"), show=False, user_data=data_dict)
  dpg.add_button(label="ARM/DISARM IGNITER", width=150, height=68, tag="arm_disarm_igniter",callback=arm_igniter)
  dpg.add_text("Igniter Status: UNARMED",pos=[10,100], tag="arm_status")
  dpg.bind_item_theme("arm_status",disarmed_status)
  dpg.add_button(label="Start/Stop Ignition \n       Countdown", width=150, height=68, tag="ignite_motor", callback=start_stop_countdown, pos=[160,29])
  dpg.add_text("Countdown Status: Inactive\n",pos=[160,100], tag="countdown_status")
  dpg.add_image("MSP_image_tag", width=126, height=88, pos=[475,20])

with dpg.window(label="Plots/Results", width=640,height=595,pos=[640,125], no_close=True, no_scrollbar=True,no_move=True, no_collapse=True, tag="plots_results_default"):
  #placeholder window, will be filled after recording is done.
  dpg.add_text()

with dpg.theme() as global_theme:

    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (60, 60, 60), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)

    with dpg.theme_component(dpg.mvInputInt):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (140, 255, 23), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)


dpg.bind_theme(global_theme)
dpg.create_viewport(title='MSP Propulsion Data Acquisition', width=1280, height=720)
dpg.setup_dearpygui()
dpg.show_viewport()
thread = threading.Thread(target=update_data)
thread.start()
dpg.start_dearpygui()
dpg.destroy_context()