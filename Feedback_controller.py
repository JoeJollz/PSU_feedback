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


try:
    while True:
        voltage = float(psu.query(f'MEAS:VOLT? CH{CHANNEL}'))
        current = float(psu.query(f'MEAS:CURR? CH{CHANNEL}'))
        power = voltage * current
        
        
        if voltage >0.5: # Safety Barrier - avoids division by small voltages, hence leading to dangerously high currents.
            n_curr = targ_power/voltage
            psu.write(f'CURR CH{CHANNEL},{n_curr:.3f}')
        else: # if voltage is too low, current will be increased, hence becoming dangerous if increased too much. Current restricted to 0A.
            n_curr = 0
            psu.write(f'CURR CH{CHANNEL},0')
        
        
        print(f"V{voltage:.2f}V, I={current:.2f}A, P={power:.2f}W -> curr_new={n_curr:.3f}A")
        print('')
        
        
        time.sleep(SLEEP_TIME)
        
except KeyboardInterrupt: # TO INTERUPT - PRESS Ctrl C
    psu.write(f'OUTP CH{CHANNEL},OFF')
    print("Stopped by user")
