# -*- coding: utf-8 -*-
"""
This script is built on from the Feedback_controller.py file, whereby pulses of 
ON and OFF will be completed, for several hundred cycles. 

e.g. cycle 8W on for 5 minutes, then 0W for 5 minutes, repeat x 1000.

TO CHECK: Once powered down, is the PSU still able to take measurements?
If yes great, if no, implement a conditional checker for P ON or OFF, if OFF 
do not write measurement, simply set V_t=0V and I_t=0V. If ON, then write to PSU
and store the live V_t and I_t values. 



Created on Mon Jun 30 13:21:17 2025

@author: jrjol
"""

import time
import serial
import matplotlib.pyplot as plt


def power_on(V, I):
    #psu.write(b"VOLT 15\n") # set voltage to 0.1V
    #psu.write(b"CURR 7\n") # set current limit to 10A
    psu.write(f"VOLT {V}\n".encode())
    psu.write(f"CURR {I}\n".encode())
    psu.write(b"OUTP ON\n") #turn ON the output
    time.sleep(1)
    
def current_update(targ_power, volt_i, curr_i):
    curr_i_1 = targ_power/volt_i
    command = f"CURR {curr_i_1}\n".encode()
    psu.write(command)
    print("Sent new current: ", curr_i_1, 'A')
    return curr_i_1

def power_off():
    psu.write(b"CURR 0\n")
    psu.write(b"VOLT 0\n")
    psu.write(b"OUTP OFF\n")
    psu.close()
    
def measure():
    psu.write(b"MEAS:VOLT?\n")
    volt_i = float(psu.readline().decode().strip())
    
    psu.write(b"MEAS:CURR?\n")
    curr_i = float(psu.readline().decode().strip())
    return volt_i, curr_i

def log(data_log, time_log, volt_log, curr_log, power_log, v_i, c_i_1):
    global start_time
    
    elap_t = round(time.time()-start_time,2)
    p = v_i * c_i_1
    data_log.append(f'{elap_t},{v_i},{c_i_1},{p}')
    time_log.append(elap_t)
    volt_log.append(v_i)
    curr_log.append(c_i_1)
    power_log.append(p)

def plotting():
    fig, ax1 = plt.subplots()
    # Plot voltage on the primary y-axis
    ax1.plot(time_log, volt_log, 'b-', label="Voltage (V)")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Voltage (V)", color="b")
    ax1.tick_params(axis="y", labelcolor="b")
    
    # Create secondary y-axis for current
    ax2 = ax1.twinx()
    ax2.plot(time_log, curr_log, 'r-', label="Current (A)")
    ax2.set_ylabel("Current (A)", color="r")
    ax2.tick_params(axis="y", labelcolor="r")
    
    # Show plot
    plt.title(f"IV vs Time. Power={targ_power}W")
    plt.show()
    
    plt.plot(time_log, power_log)
    plt.title(f'Power vs Time. Power={targ_power}W')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (W)')
    plt.show()
    
psu = serial.Serial("COM8", baudrate=9600, timeout=1)


start_time = time.time()
last_time_point = start_time

P_ON = 1
P_OFF = 0
cycle_on_duration = 5*60 # 5 minutes power down. 
cycle_off_duration = 5*60 # 5minutes power off
numb_cycles = 21 # n-1. number of cycles.
cyc_counter = 1
update_time = 0.2
targ_power = 12# target power for each of the cylcles (W).
v_min = 0.5 # minimum working voltage.
c_max = 20 # A safety maximum current 

power_on(4,7)


data_log = []
time_log = []
volt_log = []
curr_log = []
power_log = []

try:
    while True:
        current_time = time.time()
        cycle_duration = current_time-last_time_point
        
        if P_ON == 1 and cycle_duration<cycle_on_duration:
            v_i, c_i = measure()
            print('volts measured: ', v_i, 'current measured: ', c_i)
            
            if v_i > v_min: # voltage is suitably high, hence the current 
                c_i_1 = current_update(targ_power, v_i, c_i)
            else: # voltage is too low, hence stopping the current reaching too high. 
                power_off()
                print(f'Voltage exceeded the minimum working voltage: {v_min}V, \
                      stopping current at c_i+1 becoming dangerous high.')
                plotting()

            if c_i >c_max or c_i_1 > c_max:
                power_off()
                print(f'Current has exceeded the maximum current ({c_max}A) and hence shut\
                       down.')
                plotting()
            
            log(data_log, time_log, volt_log, curr_log, power_log, v_i, c_i)
            time.sleep(update_time)
            
                
            
        
        elif P_ON ==1 and cycle_duration>cycle_on_duration:
            # it is ON and needs to switch to OFF.
            
            
            P_ON = 0
            P_OFF = 1
            last_time_point = time.time()
            log(data_log, time_log, volt_log, curr_log, power_log, 0, 0)
            time.sleep(update_time)
            print('-----------------------------------------------------------')
            print(f'---------- Cycle {cyc_counter} complete. -----------------')
            print('-----------------------------------------------------------')
            
        elif P_OFF == 1 and cycle_duration>cycle_off_duration:
            # it is OFF and needs to swtich ONN
            
            P_ON = 1
            P_OFF = 0
            cyc_counter +=1
            last_time_point = time.time()
            log(data_log, time_log, volt_log, curr_log, power_log, 0, 0)
            time.sleep(update_time)
        
        elif P_OFF == 1 and cycle_duration<cycle_off_duration:
            # currently in the OFF cycle.
            log(data_log, time_log, volt_log, curr_log, power_log, 0, 0)
            time.sleep(update_time)
            
        if cyc_counter == numb_cycles: # total number of cycles have been reached. Close down sequence initiated. 
            print('Total number of power cycles complete. Power down.')
            power_off()
            plotting()
            
            break
        
        
except KeyboardInterrupt: # TO INTERUPT - PRESS Ctrl + C
    psu.write(b"OUTP OFF\n")
    print('Stopped logging data. 0A. 0V')
    print("Stopped by user")
    psu.close()
    
    
    plotting()
    
file_path = r"C:\Users\jrjol\OneDrive - University of Cambridge\Documents\Cambridge PhD\Andy Paper\power and iv data\IVPdata_20cycles.txt"

with open(file_path, 'w') as f:
    for item in data_log:
        f.write(str(item) + '\n')
    