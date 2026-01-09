# -*- coding: utf-8 -*-
"""
Created on Fri Jan  9 15:35:49 2026

@author: jrjol

a1 = attempt 1 fix.
"""

import time
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import threading
import queue

# --- PSU class ---
class PSU:
    def __init__(self, port, targ_power, name="PSU"):
        self.name = name
        self.targ_power = targ_power
        self.output_on = False
        self.volt_log, self.curr_log, self.power_log, self.time_log = [], [], [], []

        try:
            self.serial = serial.Serial(port, baudrate=9600, timeout=1)
        except serial.SerialException as e:
            raise serial.SerialException(f"{name} could not open port {port}: {e}")

        self.serial.write(b"VOLT 15\n")
        self.serial.write(b"CURR 7\n")
        self.output(False)
        time.sleep(0.5)
        self.start_time = time.time()

    def measure(self):
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
        self.serial.write(f"CURR {curr}\n".encode())

    def output(self, state):
        self.serial.write(b"OUTP ON\n" if state else b"OUTP OFF\n")
        self.output_on = state
        print(f"{self.name}: {'ON' if state else 'OFF'}")

    def close(self):
        self.output(False)
        self.serial.close()


# --- Input thread ---
def input_thread(q):
    while True:
        cmd = input()
        q.put(cmd.lower())
        if cmd.lower() == 'q':
            break


# --- Plotting ---
def plotting(psus):
    for psu in psus:
        if not psu.time_log:
            continue
        plt.figure()
        plt.plot(psu.time_log, psu.volt_log, label="Voltage (V)")
        plt.plot(psu.time_log, psu.curr_log, label="Current (A)")
        plt.title(f"{psu.name} - V/I vs Time")
        plt.xlabel("Time (s)")
        plt.legend()
        plt.show()

        plt.figure()
        plt.plot(psu.time_log, psu.power_log)
        plt.title(f"{psu.name} - Power vs Time")
        plt.xlabel("Time (s)")
        plt.ylabel("Power (W)")
        plt.show()


# --- Main function ---
def main():
    targ_power = 8.0
    volt_mini = 0.5
    MAX_CURRENT = 20
    SLEEP_TIME = 0.2

    # Initialize PSUs
    available_ports = [p.device for p in serial.tools.list_ports.comports()]
    print("Available COM ports:", available_ports)
    psus = []
    for name, port in [("PSU Reformer", "COM3"), ("PSU WGS", "COM4")]:
        if port in available_ports:
            try:
                psus.append(PSU(port, targ_power, name))
            except serial.SerialException as e:
                print(e)
        else:
            print(f"{name} port {port} not found. Skipping.")

    if not psus:
        print("No PSUs available. Exiting.")
        return

    print("\n--- Dual PSU Control ---")
    print("Type 1 to toggle PSU1 ON/OFF")
    print("Type 2 to toggle PSU2 ON/OFF")
    print("Type q to quit program safely\n")
    print("Press Enter to start the PSU loop...")
    input()

    # Input queue
    q = queue.Queue()
    thread = threading.Thread(target=input_thread, args=(q,), daemon=True)
    thread.start()

    try:
        while True:
            # --- Process input ---
            while not q.empty():
                cmd = q.get()
                if cmd == 'q':
                    raise KeyboardInterrupt
                elif cmd == '1' and len(psus) > 0:
                    psus[0].output(not psus[0].output_on)
                elif cmd == '2' and len(psus) > 1:
                    psus[1].output(not psus[1].output_on)
                else:
                    print("Invalid command.")

            # --- PSU feedback loop ---
            for psu in psus:
                if not psu.output_on:
                    continue

                volt, curr = psu.measure()
                elapsed = psu.update_logs(volt, curr)
                power = volt * curr
                print(f"{psu.name} | Time {elapsed:.1f}s | V={volt:.2f}V | I={curr:.2f}A | P={power:.2f}W")

                # Maintain target power
                if volt > volt_mini:
                    new_curr = psu.targ_power / volt
                    if new_curr <= MAX_CURRENT:
                        psu.set_current(new_curr)
                    else:
                        print(f"{psu.name}: Exceeded MAX_CURRENT. Turning OFF.")
                        psu.output(False)
                else:
                    print(f"{psu.name}: Voltage too low. Turning OFF.")
                    psu.output(False)

            time.sleep(SLEEP_TIME)

    except KeyboardInterrupt:
        print("\nShutting down...")

    finally:
        for psu in psus:
            psu.close()
        plotting(psus)
        print("Program ended safely.")


if __name__ == "__main__":
    main()
