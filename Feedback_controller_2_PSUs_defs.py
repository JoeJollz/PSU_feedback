# -*- coding: utf-8 -*-
"""
Created on Sat Jan 10 19:45:21 2026

@author: joejo

This code is for dual PSU control using just definitions. No classes... yet. 
This is a fall back, is the Classes method fails, this code can be used to get 
the data during In-Hours periods.

TODO: continue with the main loop, for measurements from both PSUs, and updates of the current.
      Wipe the user_key each iteration so the PSUs are not rapidly turned on and off. 
      Add print statements which display the on/off status of both PSUs 1 and 2, followed with their 
      values for current, voltage and power. 
"""

import threading
import time
import keyboard
import serial
import matplotlib.pyplot as plt

user_key = None
console_lock = threading.Lock()

targ_power = 8.0 # Watts
SLEEP_TIME = 0.2   # Time inbetween updates (seconds)
volt_mini = 0.5 # V
MAX_CURRENT = 20# safety limit in A

psu1 = serial.Serial("COM3", baudrate=9600, timeout=1)
psu2 = serial.Serial("COM4", baudrate=9600, timeout=1)


def on_key(event):
    global user_key
    user_key = event.name
    
    with console_lock:
        print(f"\nKey pressed: {user_key}")
        
        
def PSU1_ON():
    psu1.write(b"VOLT 15\n") # set voltage to 0.1V
    psu1.write(b"CURR 7\n") # set current limit to 10A
    psu1.write(b"OUTP ON\n") #turn ON the output
    time.sleep(2) # 2seconds to allow for cuurent and voltage to be reached. 
    
def PSU1_OFF():
    psu1.write(b"CURR 0\n")
    psu1.write(b"VOLT 0\n")
    psu1.write(b"OUTP OFF\n")
    psu1.close()
    

def PSU1_measure():
    psu1.write(b"MEAS:VOLT?\n")
    volt1_i = float(psu1.readline().decode().strip())
    
    psu1.write(b"MEAS:CURR?\n")
    curr1_i = float(psu1.readline().decode().strip())

def PSU1_update(TP, volt1_i, curr1_i, volt_mini, current_max):
    if volt1_i >volt_mini: # Safety Barrier - avoids division by small voltages, hence leading to dangerously high currents.
        curr1_i_1 = targ_power/volt1_i
        command = f"CURR {curr1_i_1}\n".encode()
        psu1.write(command)
        print("Sent new current")
    else: # if voltage is too low, current will be increased, hence becoming dangerous if increased too much. Current restricted to 0A.
        psu1.write(b"CURR 0\n")
        psu1.write(b"VOLT 0\n")
        psu1.write(b"OUTP OFF\n")
        psu1.close()
        print(f'Automatic shut down. Voltage <{volt_mini}V, protected current becoming too large.')
        plotting()
    
    if curr1_i>MAX_CURRENT: # if current exceeds the maximum safety operating current - close off. 
        psu1.write(b"OUTP OFF\n")
        print(f'Exceeded maximum current of {MAX_CURRENT}A')
        plotting()
        
def PSU2_ON():
    psu2.write(b"VOLT 15\n") # set voltage to 0.1V
    psu2.write(b"CURR 7\n") # set current limit to 10A
    psu2.write(b"OUTP ON\n") #turn ON the output
    time.sleep(2) # 2seconds to allow for cuurent and voltage to be reached. 
    
def PSU2_OFF():
    psu2.write(b"CURR 0\n")
    psu2.write(b"VOLT 0\n")
    psu2.write(b"OUTP OFF\n")
    psu2.close()
    

def PSU2_measure():
    psu2.write(b"MEAS:VOLT?\n")
    volt2_i = float(psu2.readline().decode().strip())
    
    psu2.write(b"MEAS:CURR?\n")
    curr2_i = float(psu2.readline().decode().strip())

def PSU2_update(TP, volt2_i, curr2_i, volt_mini, current_max):
    if volt2_i >volt_mini: # Safety Barrier - avoids division by small voltages, hence leading to dangerously high currents.
        curr2_i_1 = targ_power/volt2_i
        command = f"CURR {curr2_i_1}\n".encode()
        psu2.write(command)
        print("Sent new current")
    else: # if voltage is too low, current will be increased, hence becoming dangerous if increased too much. Current restricted to 0A.
        psu2.write(b"CURR 0\n")
        psu2.write(b"VOLT 0\n")
        psu2.write(b"OUTP OFF\n")
        psu2.close()
        print(f'Automatic shut down. Voltage <{volt_mini}V, protected current becoming too large.')
        plotting()
    
    if curr2_i>MAX_CURRENT: # if current exceeds the maximum safety operating current - close off. 
        psu2.write(b"OUTP OFF\n")
        print(f'Exceeded maximum current of {MAX_CURRENT}A')
        plotting()
    
    
    
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

try:
    while True:
        with console_lock:    
            print("Testing 1")
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
                
            
                
            
            
        time.sleep(3)
except KeyboardInterrupt:
    with console_lock:    
        print("\nStopped via keyboard interrupt")
finally:
    keyboard.unhook_all()