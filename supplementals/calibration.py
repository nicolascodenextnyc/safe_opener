from time import sleep
import RPi.GPIO as gpio
import sys
import tty
import termios

# Constants
CW = True
CCW = False
GRANULARITY = 1600  # Full steps per revolution
DIRECTION_PIN = 20
PULSE_PIN = 21

# Setup GPIO
gpio.setmode(gpio.BCM)
gpio.setup(DIRECTION_PIN, gpio.OUT)
gpio.setup(PULSE_PIN, gpio.OUT)

# Input character
def read_one_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char

# Perform rotation
def rotate_fraction_tick(direction, fraction):
    tick_steps = int(GRANULARITY / 100 / fraction)  # e.g. 1/4 tick = 4x more steps

    gpio.output(DIRECTION_PIN, 0 if direction == CW else 1)
    sleep(0.1)

    for _ in range(tick_steps):
        gpio.output(PULSE_PIN, gpio.HIGH)
        sleep(0.001)
        gpio.output(PULSE_PIN, gpio.LOW)
        sleep(0.0005)

# Main loop
def main():
    direction = CW
    print("Motor Calibration Started.")
    print("w = set CW, c = set CCW, e = exit")
    print("1 = full tick, 2 = 1/2, 4 = 1/4, 8 = 1/8 tick")

    while True:
        print("Enter command: ", end="", flush=True)
        char = read_one_char()
        print(f"{char}")

        if char == "e":
            print("Exiting...")
            gpio.cleanup()
            break
        elif char == "w":
            direction = CW
            print("Direction set to CW")
        elif char == "c":
            direction = CCW
            print("Direction set to CCW")
        elif char in {"1", "2", "4", "8"}:
            fraction = int(char)
            print(f"Rotating {1/fraction} of a tick in {'CW' if direction else 'CCW'} direction")
            rotate_fraction_tick(direction, fraction)
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
