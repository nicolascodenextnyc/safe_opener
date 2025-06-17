import os
import time
import logging
from datetime import datetime
import pigpio
from camera import capture_image
from model import classify_image

# --- Configuration ---
PULSE_PIN = 21
DIRECTION_PIN = 20
GRANULARITY = 1600  # steps per full turn
TICK_PER_POSITION = int(GRANULARITY / 100)
PULSE_WIDTH_US = 2000  # Slower for accuracy
PULSE_GAP_US = 2000

LOG_FILE = "dial_alignment.log"
ERROR_IMAGE_DIR = "misaligned_snaps"
os.makedirs(ERROR_IMAGE_DIR, exist_ok=True)

# --- Logging setup ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --- Pigpio setup ---
pi = pigpio.pi()
if not pi.connected:
    logging.error("Cannot connect to pigpio daemon.")
    raise RuntimeError("Failed to connect to pigpio")

# --- Rotation + validation function ---
def rotate(target_position, direction, current_position, passes=0):
    if direction.upper() not in ("CW", "CCW"):
        logging.error(f"Invalid direction: {direction}")
        return None

    # Calculate steps needed to reach target
    if direction.upper() == "CW":
        steps = (target_position - current_position) % 100
    else:  # CCW
        steps = (current_position - target_position) % 100
    
    # Add full circles (passes * 100 steps)
    total_steps = steps + (passes * 100)
    
    if total_steps == 0:
        logging.info(f"Already at target position {target_position}, no passes needed")
        return current_position
        
    logging.info(f"Rotating {passes} full passes + {steps} steps to reach {target_position}")

    dir_val = 0 if direction.upper() == "CW" else 1
    pi.set_mode(PULSE_PIN, pigpio.OUTPUT)
    pi.set_mode(DIRECTION_PIN, pigpio.OUTPUT)
    pi.write(DIRECTION_PIN, dir_val)
    time.sleep(0.05)

    # Break large movements into chunks to avoid pigpio limits
    MAX_STEPS_PER_CHUNK = 50  # Max 50 positions per waveform
    
    remaining_steps = total_steps
    while remaining_steps > 0:
        chunk_steps = min(remaining_steps, MAX_STEPS_PER_CHUNK)
        motor_steps = chunk_steps * TICK_PER_POSITION
        
        pulses = []
        for _ in range(motor_steps):
            pulses.append(pigpio.pulse(1 << PULSE_PIN, 0, PULSE_WIDTH_US))
            pulses.append(pigpio.pulse(0, 1 << PULSE_PIN, PULSE_GAP_US))

        pi.wave_clear()
        pi.wave_add_generic(pulses)
        wave_id = pi.wave_create()

        if wave_id >= 0:
            pi.wave_send_once(wave_id)
            while pi.wave_tx_busy():
                time.sleep(0.01)
            pi.wave_delete(wave_id)
        else:
            logging.error("Waveform creation failed.")
            return None
            
        remaining_steps -= chunk_steps
        time.sleep(0.1)  # Small delay between chunks

    time.sleep(1.0)  # Longer settling time

    # Capture and validate
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pos_{current_position}_to_{steps}_{timestamp}.jpg"
    image_path = os.path.join(ERROR_IMAGE_DIR, filename)

    capture_image(image_path)
    recogninzedAs = classify_image(image_path)

    if abs(recogninzedAs - target_position)>1 and not abs(recogninzedAs - target_position)==99:
        logging.warning(f"Position mismatch: expected {target_position}, recognized as {recogninzedAs}")
        logging.warning(f"Image saved to: {image_path}")
        return None

    # Save training images to dial_images2 directory
    training_image_dir = "/media/admin/IMG/dial_images2"
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(training_image_dir, exist_ok=True)
        
        # Check if directory is writable
        if not os.access(training_image_dir, os.W_OK):
            logging.error(f"Training image directory not writable: {training_image_dir}")
        else:
            # Get next sequential ID for this specific label by counting existing files
            existing_files = [f for f in os.listdir(training_image_dir) 
                            if f.startswith(f"dial2_{target_position}_")]
            next_id = len(existing_files)
            
            import shutil
            
            if recogninzedAs == target_position:
                # Perfect match - save as correctly aligned training data
                training_filename = f"dial2_{target_position}_{next_id}.jpg"
                training_path = os.path.join(training_image_dir, training_filename)
                
                # Move the captured image to training directory
                shutil.move(image_path, training_path)
                logging.info(f"Training image saved (aligned): {training_path}")
            else:
                # Close match but not exact - save as misaligned with target label
                training_filename = f"dial2_{target_position}_{next_id}_misaligned.jpg"
                training_path = os.path.join(training_image_dir, training_filename)
                
                # Move the captured image to training directory
                shutil.move(image_path, training_path)
                logging.info(f"Training image saved (misaligned): {training_path}")
                
    except (OSError, IOError) as e:
        logging.error(f"Failed to save training image to {training_image_dir}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error saving training image: {e}")

    logging.info(f"Rotation successful: {current_position} → {target_position}")
    return target_position

# --- Cleanup helper ---
def cleanup():
    pi.wave_clear()
    pi.stop()
