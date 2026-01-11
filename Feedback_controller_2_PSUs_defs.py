# -*- coding: utf-8 -*-
"""
Created on Sat Jan 10 19:45:21 2026

@author: joejo

This code is for dual PSU control using just definitions. No classes... yet. 
This is a fall back, is the Classes method fails, this code can be used to get 
the data during In-Hours periods.

TODO: 
"""

import threading
import time
import keyboard
import serial
import matplotlib.pyplot as plt
import serial.tools.list_ports
import csv
import os

user_key = None
console_lock = threading.Lock()

TP = 8.0 # Watts, target power
SLEEP_TIME = 0.2   # Time inbetween updates (seconds)
volt_mini = 0.5 # V
current_max = 20# safety limit in A

psu1 = serial.Serial("COM3", baudrate=9600, timeout=1)
psu2 = serial.Serial("COM4", baudrate=9600, timeout=1)


def on_key(event):
    global user_key
    user_key = event.name
    
    with console_lock:
        print(f"\nKey pressed: {user_key}")
    
def log_data(log, t, c, v, p):
    log['time'].append(t)
    log['current'].append(c)
    log['voltage'].append(v)
    log['power'].append(p)
    
def plotting(log, psu_num):
    fig, ax1 = plt.subplots()
    ax1.plot(log['time'], log['voltage'], 'b-' , label = 'Voltage (V)')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel("Voltage (V)", color = "b")
    ax1.tick_params(axis="y", labelcolor = "b")
    
    ax2 = ax1.twinx()
    ax2.plot(log['time'], log['current'], '-r', label = 'Current (A)')
    ax2.set_ylabel("Current (A)", color = "r")
    ax2.tick_params(axis="y", labelcolor="r")
    
    plt.title(f"IV vs Time. PSU{psu_num}")
    plt.show()
    
    plt.plot(log['time'], log['power'])
    plt.title(f'Power vs Time. PSU{psu_num}')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (W)')
    plt.show()
    
def save_log_to_csv(log, filename):
    filepath = os.path.join(os.getcwd(), filename)
    
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        writer.writerow(log.keys())
        
        for row in zip(*log.values()):
            writer.writerow(row)
        
    print(f"Data log for {filename} saved.")
        
def PSU1_ON():
    if not psu1.is_open:
        psu1.open()
    psu1.write(b"VOLT 15\n") # set voltage to 0.1V
    psu1.write(b"CURR 7\n") # set current limit to 10A
    psu1.write(b"OUTP ON\n") #turn ON the output
    time.sleep(2) # 2seconds to allow for cuurent and voltage to be reached. 
    
def PSU1_OFF():
    psu1.write(b"CURR 0\n")
    psu1.write(b"VOLT 0\n")
    psu1.write(b"OUTP OFF\n")
    

def PSU1_measure():
    psu1.write(b"MEAS:VOLT?\n")
    try:
        volt1_i = float(psu1.readline().decode().strip())
    except ValueError:
        volt1_i = float('nan')
    
    psu1.write(b"MEAS:CURR?\n")
    try:
        curr1_i = float(psu1.readline().decode().strip())
    except ValueError:
        curr1_i = float('nan')
        
    return volt1_i, curr1_i

def PSU1_update(TP, volt1_i, curr1_i, volt_mini, current_max):
    if volt1_i >volt_mini: # Safety Barrier - avoids division by small voltages, hence leading to dangerously high currents.
        curr1_i_1 = TP/volt1_i
        command = f"CURR {curr1_i_1}\n".encode()
        psu1.write(command)
        print("Sent new current")
    else: # if voltage is too low, current will be increased, hence becoming dangerous if increased too much. Current restricted to 0A.
        psu1.write(b"CURR 0\n")
        psu1.write(b"VOLT 0\n")
        psu1.write(b"OUTP OFF\n")
        print(f'Automatic shut down. Voltage <{volt_mini}V, protected current becoming too large.')
        plotting(data_log_psu1, 1)
    
    if curr1_i_1>current_max: # if current exceeds the maximum safety operating current - close off. 
        psu1.write(b"OUTP OFF\n")
        print(f'Exceeded maximum current of {current_max}A')
        plotting(data_log_psu1, 1)
        
def PSU2_ON():
    if not psu2.is_open:
        psu2.open()
    psu2.write(b"VOLT 15\n") # set voltage to 0.1V
    psu2.write(b"CURR 7\n") # set current limit to 10A
    psu2.write(b"OUTP ON\n") #turn ON the output
    time.sleep(2) # 2seconds to allow for cuurent and voltage to be reached. 
    
def PSU2_OFF():
    psu2.write(b"CURR 0\n")
    psu2.write(b"VOLT 0\n")
    psu2.write(b"OUTP OFF\n")
    

def PSU2_measure():
    psu2.write(b"MEAS:VOLT?\n")
    try:
        volt2_i = float(psu2.readline().decode().strip())
    except ValueError:
        volt2_i = float('nan')
    
    psu2.write(b"MEAS:CURR?\n")
    try:
        curr2_i = float(psu2.readline().decode().strip())
    except ValueError:
        curr2_i = float('nan')
    return volt2_i, curr2_i

def PSU2_update(TP, volt2_i, curr2_i, volt_mini, current_max):
    if volt2_i >volt_mini: # Safety Barrier - avoids division by small voltages, hence leading to dangerously high currents.
        curr2_i_1 = TP/volt2_i
        command = f"CURR {curr2_i_1}\n".encode()
        psu2.write(command)
        print("Sent new current")
    else: # if voltage is too low, current will be increased, hence becoming dangerous if increased too much. Current restricted to 0A.
        psu2.write(b"CURR 0\n")
        psu2.write(b"VOLT 0\n")
        psu2.write(b"OUTP OFF\n")
        print(f'Automatic shut down. Voltage <{volt_mini}V, protected current becoming too large.')
        plotting(data_log_psu2, 2)
    
    if curr2_i_1>current_max: # if current exceeds the maximum safety operating current - close off. 
        psu2.write(b"OUTP OFF\n")
        print(f'Exceeded maximum current of {current_max}A')
        plotting(data_log_psu2, 2)
    
    
    
def PSUs_OFF(): # turns off both PSUs via keyboard shut down. 
    psu1.write(b"CURR 0\n")
    psu1.write(b"VOLT 0\n")
    psu1.write(b"OUTP OFF\n")
    psu1.close()
    
    psu2.write(b"CURR 0\n")
    psu2.write(b"VOLT 0\n")
    psu2.write(b"OUTP OFF\n")
    psu2.close()
    
 
keyboard.on_press(on_key)

available_ports = [p.device for p in serial.tools.list_ports.comports()]
print("Available COM ports:", available_ports)

psu_1 = 0
psu_2 = 0

data_log_psu1 = {
                'time': [], 
                'current': [],
                'voltage': [],
                'power': []
                }
data_log_psu2 = {
                'time': [],
                'current': [],
                'voltage': [],
                'power': []
                }

start_time = time.time()

try:
    while True:
        with console_lock:    
            print("Testing 1")
            
            
            t = round(time.time() - start_time, 2)
            # ================= PSU UPDATING AND LOGGING CODE =================
            if psu_1 ==1: #PSU 1 is on, and need power controlling
                v1_i, c1_i = PSU1_measure()
                PSU1_update(TP, v1_i, c1_i, volt_mini, current_max)
                log_data(data_log_psu1, t, c1_i, v1_i, (c1_i*v1_i))
                print('------------------------------------------------------')
                print(f'PSU1 ON. Time={t}s. Current={c1_i}A. Volts={v1_i}V. Power={(c1_i*v1_i)}W')
                
                
            elif psu_1 == 0: # PSU1 off, empty log
                log_data(data_log_psu1, t, 0, 0, 0)
                print('------------------------------------------------------')
                print(f'PSU1 OFF. Time={t}s. Current=0A. Volts=0V. Power=0W')
                
            
            
            if psu_2 == 1: #PSU 2 is on, and also needs power control. 
                v2_i, c2_i = PSU2_measure()
                PSU2_update(TP, v2_i, c2_i, volt_mini, current_max)
                log_data(data_log_psu2, t, c2_i, v2_i, (c2_i*v2_i))
                print('------------------------------------------------------')
                print(f'PSU2 ON. Time={t}s. Current={c2_i}A. Volts={v2_i}V. Power={(c2_i*v2_i)}W')
                
            elif psu_2 == 0: # PSU2 off, empty log.
                log_data(data_log_psu2, t, 0, 0, 0)
                print('------------------------------------------------------')
                print(f'PSU2 OFF. Time={t}s. Current=0A. Volts=0V. Power=0W')
                
            
            # ============== PSU TOGGLE ON/OFF STATUS CODE ====================
            if user_key:
                print(f"Current key: {user_key}")
            
            if user_key =='1': #Altering the ON/OFF status of PSU1
                if psu_1 == 0: # Power on PSU1
                    print('Powering on PSU1')
                    PSU1_ON()
                    psu_1 = 1 # PSU 1 is in the ON State
                elif psu_1 == 1: # Power off PSU1
                    print('Powering off PSU1')
                    PSU1_OFF()
                    psu_1 = 0
            
            if user_key == '2': # Altering the ON/OFF status of PSU2
                if psu_2 == 0: # Power on PSU2
                    print('Powering on PSU2')
                    PSU2_ON()
                    psu_2 = 1
                elif psu_2 == 1: # Power off PSU2
                    print('Powering off PSU2')
                    PSU2_OFF()
                    psu_2 = 0
            
            user_key = None
                
    
        time.sleep(SLEEP_TIME)
except KeyboardInterrupt:
    with console_lock:    
        print("\nStopped via keyboard interrupt")
        PSUs_OFF()
        plotting(data_log_psu1, 1)
        plotting(data_log_psu2, 2)
        save_log_to_csv(data_log_psu1, "PSU1_data.csv")
        save_log_to_csv(data_log_psu2, "PSU2_data.csv")
finally:
    keyboard.unhook_all()