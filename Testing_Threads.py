# -*- coding: utf-8 -*-
"""
Created on Sat Jan 10 15:11:17 2026

@author: joejo
"""
import threading
import time
import keyboard

user_key = None
console_lock = threading.Lock()

def on_key(event):
    global user_key
    user_key = event.name
    
    with console_lock:
        print(f"\nKey pressed: {user_key}")
    
keyboard.on_press(on_key)




try:
    while True:
        with console_lock:    
            print("Testing 1")
            if user_key:
                print(f"Current key: {user_key}")
        time.sleep(3)
except KeyboardInterrupt:
    with console_lock:    
        print("\nStopped via keyboard interrupt")
finally:
    keyboard.unhook_all()