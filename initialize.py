import os
import time
import logging
from camera import capture_image
from model import classify_image
from dial_control import rotate
import pigpio

# Logging setup
LOG_FILE = "dial_alignment.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# GPIO Pins
PULSE_PIN = 21
DIRECTION_PIN = 20
GRANULARITY = 1600
TICK_PER_POSITION = int(GRANULARITY / 100)
PULSE_WIDTH_US = 3000  # Increased for more reliable steps
PULSE_GAP_US = 3000   # Slower timing for accuracy

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    logging.error("Failed to connect to pigpio daemon.")
    raise RuntimeError("Cannot connect to pigpio daemon.")

def initialize_dial_to_zero():
    logging.info("Starting dial alignment procedure.")

    # Step 1: Capture and classify current position
    first_img = "start_position.jpg"
    capture_image(first_img)
    initial_position = classify_image(first_img)
    logging.info(f"Detected initial dial position: {initial_position}")

    if not isinstance(initial_position, int) or not (0 <= initial_position < 100):
        logging.error("Invalid dial position detected.")
        return False

    # Step 2: Rotate to position 0 using dial_control.rotate()
    if initial_position == 0:
        logging.info("Already at position 0, no rotation needed.")
        return True
    else:
        logging.info(f"Rotating from position {initial_position} to 0 (counterclockwise).")
        final_position = rotate(0, 'CCW', initial_position)
        
        if final_position is None:
            logging.error("Failed to rotate to position 0.")
            return False
        elif final_position == 0:
            logging.info("Dial successfully aligned to position 0.")
            return True
        else:
            logging.warning(f"Expected dial to be at 0 but ended at {final_position}.")
            return False


