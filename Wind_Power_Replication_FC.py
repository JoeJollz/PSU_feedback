
"""
This programme delievers a power profile that matches that of Wind generation 
from the UK. 

The time series data set shows every 5 minutes the new wind profile. 
Therefore to update the power profile, a loop which extracts the next power value
will be utilised, where a 300 second (5 minute) time.sleep function is added. 

To do- Add section which handels COM disconntection. 
        Edge case test, when the .txt wind power gen profiles runs out of data points - turn off sequence and data saving needs to be error free.

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
    
def power_update(P, volt_i, curr_i):
    curr_i_1 = targ_power/volt_i
    command = f"CURR {curr_i_1}\n".encode()
    psu.write(command)
    print("Sent new current")
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
    plt.title(f"IV vs Time")
    plt.show()
    
    plt.plot(time_log, power_log)
    plt.title(f'Power vs Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (W)')
    plt.show()
    
file_path = 'Power_gen_profiles/Wind_25062025.txt'

with open(file_path, 'r') as f:
    WPP = [float(line.strip()) for line in f if line.strip()] # WPP = Wind Power Profile
WPP = WPP[1:] # ingnoring the first WPP[0] = 0W. Specific to the power gen profile .txt file. 


psu = serial.Serial("COM8", baudrate=9600, timeout=1)

data_log = []
time_log = []
volt_log = []
curr_log = []
power_log = []


start_time = time.time()
last_trigger = start_time 

i = 0 
SLEEP_TIME = 0.1
targ_power = WPP[i]
v_min = 0.1 # minium safe working voltage, otherwise I will be too high. 
Cmax = 20 # A. Maxim safe working current. 

#setting some limis for V and I.
power_on(4, 7)
v_i, c_i = measure()
power_update(targ_power, v_i, c_i)


try:
    while True:
        current_time = time.time()
        
        if current_time - last_trigger >= 8:
            print('8s passed. Resetting')
            last_trigger = current_time
            i += 1
            
            if i == len(WPP):
                print("All power targets processed. Exiting loop.")
                power_off()
                plotting()
                
                break
            
            targ_power = WPP[i]
            
        v_i, c_i = measure()
        if v_i > v_min: # voltage is sufficiently high - continue updating current.
            c_i_1 = power_update(targ_power, v_i, c_i)
        
        else: # projection from small voltages with high power - hence high current. Shut down.
            power_off()
            print(f"Power OFF - minimum working voltage exceeded. V_i={v_i}V<Vmin={v_min}V")
            plotting()
            
            
        
        if c_i > Cmax or c_i_1 > Cmax: # current exceeds current max limit. Shut down.
            power_off()
            print("Power OFF - maximum current exceeded.")
            plotting()
            
        elapsed_time = round(time.time()-start_time,2)
        p = v_i * c_i_1
        data_log.append(f"{elapsed_time},{v_i},{c_i_1},{p}")
        time_log.append(elapsed_time)
        curr_log.append(c_i_1)
        volt_log.append(v_i)
        power_log.append(p)
        
        
        print(f"Time: {elapsed_time}s | Voltage: {v_i}V | Current: {c_i_1}A")
        print(f"Power: {p}W")
        print('----------------------------------------------------------------')
        
        time.sleep(SLEEP_TIME)
        
        
        
except KeyboardInterrupt:
    power_off()
    plotting()
    

# file_path = r"C:\Users\jrjol\OneDrive - University of Cambridge\Documents\Cambridge PhD\Methanol Reforming Paper\GC data\NiALD_20Ce_C\data_log_14W.txt"

# with open(file_path, 'w') as f:
#     for item in data_log:
#         f.write(str(item) + '\n')

 