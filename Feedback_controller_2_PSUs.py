# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 11:38:22 2025

@author: jrjol

This .py file is for the simultaneously control of 2 joule heating reactors,
with semiconductive properties.

"""

import msvcrt
import time
import serial
import matplotlib.pyplot as plt


class PSU:
    def __init__(self, port, targ_power, name="PSU"):
        self.name = name
        self.serial = serial.Serial(port, baudrate = 9600, timeout = 1)
        self.targ_power = targ_power
        self.volt_log = []
        self.curr_log = []
        self.power_log = []
        self.time_log = []
        self.output_on = False 
        
        self.serial.write(b"VOLT 15\n")
        self.serial.write(b"CURR 7\n")
        self.output(False)
        time.sleep(0.5)
        self.start_time = time.time()
        
    def measure(self):
        """ Reads voltage and current from the PSU. """
        self.serial.write(b"MEAS:VOLT?\n")
        volt = float(self.serial.readline().decode().strip() or 0)
        self.serial.write(b"MEAS:CURR?\n")
        curr = float(self.serial.readline().decode().strip() or 0)
        return volt, curr
    
    def update_logs(self, volt, curr):
        elapsed = round(time.time() - self.start_time, 2)
        self.volt_log.append(volt)
        self.curr_log.append(curr)
        self.power_log.append(volt * curr)
        self.time_log.append(elapsed)
        return elapsed
    
    def set_current(self, curr):
        cmd = f"CURR {curr}\n".encode()
        self.serial.write(cmd)
        
    def output(self, state):
        if state:
            self.serial.write(b"OUTP ON\n")
            self.output_on = True
            print('--------------------------------------------')
            print(f"{self.name}: Output ON")
            print('--------------------------------------------')
        else:
            self.serial.write(b"OUTP OFF\n")
            self.output_on = False
            print('--------------------------------------------')
            print(f"{self.name}: Output OFF")
            print('--------------------------------------------')
            
    def close(self):
        self.output(False)
        self.serial.close()
        
def plotting(psu_list):
    for psu in psu_list:
        plt.figure()
        plt.plot(psu.time_log, psu.volt_log, label="Voltage (V)")
        plt.plot(psu.time_log, psu.curr_log, label="Current (A)")
        plt.title(f"{psu.name} - Voltage/Current vs Time")
        plt.xlabel("Time (s)")
        plt.legend()
        plt.show()
    
        plt.figure()
        plt.plot(psu.time_log, psu.power_log)
        plt.title(f"{psu.name} - Power vs Time")
        plt.xlabel("Time (s)")
        plt.ylabel("Power (W)")
        plt.show()

def main():
    targ_power = 8.0
    volt_mini = 0.5
    MAX_CURRENT = 20
    SLEEP_TIME = 0.1
    
    # Initialize PSUs
    psu1 = PSU("COM3", targ_power, name="PSU Reformer")
    psu2 = PSU("COM4", targ_power, name="PSU WGS")
    psus = [psu1, psu2]
    
    print("\n--- Dual PSU Control ---")
    print("Press 1 to toggle PSU1 ON/OFF")
    print("Press 2 to toggle PSU2 ON/OFF")
    print("Press q to quit program safely.\n")
    input("Press Enter to start the PSU loop...")
    
    try:
        while True:
            # --- Check user input ---
            if msvcrt.kbhit():
                key = msvcrt.getch().decode("utf-8").lower()
                if key == "1":
                    psu1.output(not psu1.output_on)
                elif key == "2":
                    psu2.output(not psu2.output_on)
                elif key == "q":
                    print("\nQuitting program....")
                    break
            
            # --- Loop through PSUs ---
            for psu in psus:
                if not psu.output_on:
                    continue
                
                volt, curr = psu.measure()
                elapsed = psu.update_logs(volt, curr)
                power = volt * curr
                
                print(f"{psu.name} | Time: {elapsed:5.2f}s | V={volt:6.3f}V | "
                      f"I={curr:6.3f}A | P={power:6.3f}W")
                
                # Adjust current to maintain target power
                if volt > volt_mini:
                    new_curr = psu.targ_power / volt
                    if new_curr <= MAX_CURRENT:
                        psu.set_current(new_curr)
                    else:
                        print(f"{psu.name}: New current {new_curr:.2f}A exceeds {MAX_CURRENT}A. Output OFF for safety.")
                        psu.output(False)
                else:
                    print(f"{psu.name}: Voltage below {volt_mini}V. Output OFF for safety.")
                    psu.output(False)
            
            time.sleep(SLEEP_TIME)
    
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Shutting down.")
    
    finally:
        for psu in psus:
            psu.close()
        plotting(psus)
        print("Program ended safely")


        
                    
                