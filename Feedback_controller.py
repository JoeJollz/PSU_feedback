# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 17:17:58 2025

@author: jrjol
"""

import time
import serial

psu = serial.Serial("COM8", baudrate=9600, timeout=1)

targ_power = 50.0 # Watts
SLEEP_TIME = 0.5   # Time inbetween updates (seconds)

psu.write(":VOLT 0.1") # set voltage to 0.1V
psu.write(":CURR 10") # set current limit to 10A
psu.write(":OUTP ON") #turn ON the output

start_time = time.time()

try:
    while True:
        psu.write(b"MEAS:VOLT?\n")
        volt_i = float(psu.readline().decode().strip())
        
        psu.write(b"MEAS:CURR?\n")
        curr_i = float(psu.readline().decode().strip())
        
        elapsed_time = round(time.time() - start_time,2)
        
        data_log.append(f"{elapsed_time},{volt_i},{curr_i}")
        
        print(f"Time: {elapsed_time}s | Voltage: {volt_i}V | Current: {curr_i}A")
        print('----------------------------------------------------------------')
        
        time.sleep(1)
        
        current = float(psu.query(f'MEAS:CURR? CH{CHANNEL}'))
        power = voltage * current
        
        
        if voltage >0.5: # Safety Barrier - avoids division by small voltages, hence leading to dangerously high currents.
            n_curr = targ_power/voltage
            psu.write(f'CURR CH{CHANNEL},{n_curr:.3f}')
        else: # if voltage is too low, current will be increased, hence becoming dangerous if increased too much. Current restricted to 0A.
            n_curr = 0
            psu.write(f'CURR CH{CHANNEL},0')
        
                
        
        time.sleep(SLEEP_TIME)
        
except KeyboardInterrupt: # TO INTERUPT - PRESS Ctrl C

    psu.write(b"OUTP OFF\n")
    print('Stopped logging data. 0A. 0V')
    psu.write(f'OUTP CH{CHANNEL},OFF')
    print("Stopped by user")
