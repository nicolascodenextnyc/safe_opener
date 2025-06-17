
from initialize import initialize_dial_to_zero
import pigpio
import logging

from combination_manager import get_attempts_status, get_next_combination, initialize_attempts_file
from dial_control import rotate

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    logging.error("Failed to connect to pigpio daemon.")
    raise RuntimeError("Cannot connect to pigpio daemon.")

if __name__ == "__main__":

    # Initialize the attempts file
    initialize_attempts_file()

    try:
        result = initialize_dial_to_zero()
        if not result:
            print("Dial alignment failed. Check log for details.")
            exit(1)
        else:
            print("Dial aligned to position 0 successfully.")
        current_position = 0 # Current dial position
        
        while True:
            combination = get_next_combination()
            if not combination:
                status = get_attempts_status()
                logging.info(f"Combinations - Total: {status['total']}, Attempted: {status['attempted']}, Remaining: {status['remaining']}")
                print(f"Combinations - Total: {status['total']}, Attempted: {status['attempted']}, Remaining: {status['remaining']}")
                print(f"WE ARE DONE")
                break
            
            # Split combination into three integers
            first, second, third = map(int, combination.split())
            logging.info(f"Trying combination: {first} {second} {third}")
            
            # Step 1: Turn LEFT, stop at first number on 4th pass (3 full passes + target)
            logging.info(f"Step 1: Turn LEFT to {first} on 4th pass")
            current_position = rotate(first, "CW", current_position, passes=3)
            if current_position is None:
                logging.error(f"Error on step 1 for combination {combination}")
                break
            
            # Step 2: Turn RIGHT, stop at second number on 3rd pass (2 full passes + target)
            logging.info(f"Step 2: Turn RIGHT to {second} on 3rd pass")
            current_position = rotate(second, "CCW", current_position, passes=2)
            if current_position is None:
                logging.error(f"Error on step 2 for combination {combination}")
                break
            
            # Step 3: Turn LEFT, stop at third number on 2nd pass (1 full pass + target)
            logging.info(f"Step 3: Turn LEFT to {third} on 2nd pass")
            current_position = rotate(third, "CW", current_position, passes=1)
            if current_position is None:
                logging.error(f"Error on step 3 for combination {combination}")
                break
                
            # Step 4: Turn RIGHT full 100 positions - if position mismatch, lock opened
            logging.info("Step 4: Turn RIGHT full 100 positions until lock opens")
            # Calculate position after full 100 CW rotation
            attempt_pos = current_position  # Same position after full circle
            final_position = rotate(attempt_pos, "CCW", current_position, passes=1)
            if final_position is None:
                logging.info(f"LOCK OPENED! Combination was: {first} {second} {third}")
                print(f"SUCCESS! Lock opened with combination: {first} {second} {third}")
                break
                
            logging.info(f"Completed combination attempt: {first} {second} {third} - continuing...")
            current_position = final_position
    finally:
        pi.wave_clear()
        pi.stop()