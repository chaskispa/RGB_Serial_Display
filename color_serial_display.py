import os
os.environ["SDL_AUDIODRIVER"] = "dummy"

import serial
import pygame
import sys
import time

print("[DEBUG] Script started")

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600

# Initialize serial
try:
    print(f"[DEBUG] Attempting to open serial port {SERIAL_PORT} at {BAUD_RATE} baud...")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("[DEBUG] Serial port opened successfully")
except Exception as e:
    print(f"[ERROR] Could not open serial port: {e}")
    time.sleep(5)
    sys.exit(1)

# Initialize pygame
pygame.init()
pygame.mixer.quit()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
info = pygame.display.Info()
print(f"[DEBUG] Pygame display set to FULLSCREEN ({info.current_w}x{info.current_h})")

# Draw waiting screen
font = pygame.font.SysFont(None, 48)
waiting_text = font.render("Iniciando", True, (255, 255, 255))
screen.fill((0, 0, 0))
screen.blit(waiting_text, (info.current_w // 2 - 200, info.current_h // 2))
pygame.display.flip()
print("[DEBUG] Waiting screen drawn")

# Serial handling
receiving = False
buffer = bytearray()
serial_active = False
last_data_time = time.time()

# Main loop
while True:
    try:
        # Keep pygame responsive (no keyboard input handling)
        pygame.event.pump()

        if ser.in_waiting:
            try:
                byte = ser.read()
                if byte == b'#':
                    if receiving:
                        if len(buffer) == 3:
                            r, g, b = buffer
                            print(f"[DEBUG] Received RGB: {r}, {g}, {b}")
                            screen.fill((r, g, b))
                            pygame.display.flip()
                            serial_active = True
                            last_data_time = time.time()
                        else:
                            print(f"[DEBUG] Invalid buffer length: {len(buffer)}: {buffer}")
                        buffer.clear()
                        receiving = False
                    else:
                        buffer.clear()
                        receiving = True
                elif receiving:
                    buffer.append(ord(byte))
            except serial.SerialException as e:
                print(f"[ERROR] Serial error: {e}")
                receiving = False
                buffer.clear()
                time.sleep(1)

        # Redraw waiting screen if no color yet
        if not serial_active and time.time() - last_data_time > 5:
            screen.fill((0, 0, 0))
            screen.blit(waiting_text, (info.current_w // 2 - 200, info.current_h // 2))
            pygame.display.flip()

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        time.sleep(2)
