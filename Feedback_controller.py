# -*- coding: utf-8 -*-
'''
Attempted LAN connection. Struggled, yet ping IPAddress was successful, and a 
connected LAN was established, there was a communication blockage between the
computer and QPX750SP. 

In order to find the QPX IP address and TCP/IP Port, follow these steps. 
1. power on the QPX
2. Select Menu -> Interface -> LAN Status -> Next Page.
3. The IP Address of the QPX is shown, along with the Subnet Mask. 
4. With this information. Enter into a browser 'http://{IP_Address}'
5. The following information will be displayed including, TCP/IP Socket Port,
and full Instrument String Address.
was a communication blockage

To address this LAN communication issue, various attempts were trialled.
- Disabling Windows FireWall for Private Ethernet communications.
- Adding a new rule for Windows FireWall Advanced settings for Inbound communication
  (this will require your TCP/IP port number). 
Yet neither resulted in success. Strangely ping {IP address} did show that connection was established.

Due to the LAN communication blockage, USB communication was choosen. Via the following steps.

'''

"""
Created on Mon Jun  9 17:17:58 2025

@author: jrjol
"""

import time
import serial
import matplotlib.pyplot as plt
 
psu = serial.Serial("COM3", baudrate=9600, timeout=1)

data_log = []
time_log = []
volt_log = []
curr_log = []
power_log = []

targ_power = 8.0 # Watts
SLEEP_TIME = 0.2   # Time inbetween updates (seconds)
volt_mini = 0.5 # V
MAX_CURRENT = 20# safety limit in A

psu.write(b"VOLT 15\n") # set voltage to 0.1V
psu.write(b"CURR 7\n") # set current limit to 10A
psu.write(b"OUTP ON\n") #turn ON the output
time.sleep(2) # 2seconds to allow for cuurent and voltage to be reached. 
start_time = time.time()

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
    plt.title(f"IV vs Time -  {targ_power}W")
    plt.show()
    
    plt.plot(time_log, power_log)
    plt.title(f'Power vs Time {targ_power}W')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (W)')
    plt.show()
    

try:
    while True:
        psu.write(b"MEAS:VOLT?\n")
        volt_i = float(psu.readline().decode().strip())
        
        psu.write(b"MEAS:CURR?\n")
        curr_i = float(psu.readline().decode().strip())
        
        elapsed_time = round(time.time() - start_time,2)
        
       
        time_log.append(elapsed_time)
        curr_log.append(curr_i)
        volt_log.append(volt_i)
        power_log.append(volt_i*curr_i)
        
        p = curr_i*volt_i 
        data_log.append(f"{elapsed_time},{volt_i},{curr_i},{p}")
        print(f"Time: {elapsed_time}s | Voltage: {volt_i}V | Current: {curr_i}A")
        print(f"Power: {p}W")
        print('----------------------------------------------------------------')
        
        
        if volt_i >volt_mini: # Safety Barrier - avoids division by small voltages, hence leading to dangerously high currents.
            curr_i_1 = targ_power/volt_i
            command = f"CURR {curr_i_1}\n".encode()
            psu.write(command)
            print("Sent new current")
        else: # if voltage is too low, current will be increased, hence becoming dangerous if increased too much. Current restricted to 0A.
            psu.write(b"CURR 0\n")
            psu.write(b"VOLT 0\n")
            psu.write(b"OUTP OFF\n")
            psu.close()
            print(f'Automatic shut down. Voltage <{volt_mini}V, protected current becoming too large.')
            plotting()
        
        if curr_i>MAX_CURRENT: # if current exceeds the maximum safety operating current - close off. 
            psu.write(b"OUTP OFF\n")
            print(f'Exceeded maximum current of {MAX_CURRENT}A')
            plotting()
        if elapsed_time>360:
            psu.write(b"OUTP OFF\n")
            psu.close()
            plotting()
            
        
        time.sleep(SLEEP_TIME)
        
except KeyboardInterrupt: # TO INTERUPT - PRESS Ctrl C

    psu.write(b"OUTP OFF\n")
    print('Stopped logging data. 0A. 0V')
    print("Stopped by user")
    psu.close()
    
    
    plotting()
    
# file_path = r"C:\Users\jrjol\OneDrive - University of Cambridge\Documents\Cambridge PhD\Methanol Reforming Paper\GC data\NiALD_20Ce_C\data_log_14W.txt"

# with open(file_path, 'w') as f:
#     for item in data_log:
#         f.write(str(item) + '\n')

