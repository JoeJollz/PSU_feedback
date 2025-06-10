# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 17:17:58 2025

@author: jrjol
"""

import time
import serial

psu = serial.Serial("COM8", baudrate=9600, timeout=1)

data_log = []

targ_power = 50.0 # Watts
SLEEP_TIME = 0.5   # Time inbetween updates (seconds)
volt_mini = 0.5 # V

psu.write(b"VOLT 0.1\n") # set voltage to 0.1V
psu.write(b"CURR 10\n") # set current limit to 10A
psu.write(b"OUTP ON\n") #turn ON the output

start_time = time.time()

try:
    while True:
        psu.write(b"MEAS:VOLT?\n")
        volt_i = float(psu.readline().decode().strip())
        
        psu.write(b"MEAS:CURR?\n")
        curr_i = float(psu.readline().decode().strip())
        
        elapsed_time = round(time.time() - start_time,2)
        
        data_log.append(f"{elapsed_time},{volt_i},{curr_i}")
        
        p = curr_i*volt_i
        print(f"Time: {elapsed_time}s | Voltage: {volt_i}V | Current: {curr_i}A")
        print(f"Power: {p}W")
        print('----------------------------------------------------------------')
        
        
        if volt_i >volt_mini: # Safety Barrier - avoids division by small voltages, hence leading to dangerously high currents.
            curr_i_1 = targ_power/volt_i
            psu.write(b"CURR {curr_i_1}\n".encode())
        else: # if voltage is too low, current will be increased, hence becoming dangerous if increased too much. Current restricted to 0A.
            psu.write(b"CURR 0\n")
            psu.write(b"VOLT 0\n")
            psu.write(b"OUTP OFF\n")
            psu.close()
            print(f'Automatic shut down. Voltage <{volt_mini}V, protected current becoming too large.')
        
                
        
        time.sleep(SLEEP_TIME)
        
except KeyboardInterrupt: # TO INTERUPT - PRESS Ctrl C

    psu.write(b"OUTP OFF\n")
    print('Stopped logging data. 0A. 0V')
    print("Stopped by user")
    psu.close()
