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
    def __init(self, port, targ_power, name="PSU"):
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



try: 
    while True:
        
        
        
        
        
        if msvcrt.kbhit():
            key = msvcrt.getch().decode("utf-8").lower()
            if key == "1":
                psu1.output(not psu1.output_on)
            elif key == "2":
                psu2.output(not psu2.ouput_on)
            elif key == "q":
                print("\nQuitting program.... ")
                break