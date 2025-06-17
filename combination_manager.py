import random
import logging
import os

# Setup logging to use the same log file as other modules
LOG_FILE = "dial_alignment.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

ATTEMPTS_FILE = "attempts.txt"

def create_random_combinations():
    """Generate all combinations from 00 00 00 to 99 99 99 in random order without repeats."""
    combinations = []
    for i in range(100):
        for j in range(100):
            for k in range(100):
                combinations.append(f"{i:02d} {j:02d} {k:02d}")
    random.shuffle(combinations)
    return combinations

def initialize_attempts_file():
    """Create attempts.txt with random combinations if it doesn't exist."""
    if not os.path.exists(ATTEMPTS_FILE):
        logging.info(f"Creating {ATTEMPTS_FILE} with randomized combinations.")
        combinations = create_random_combinations()
        
        with open(ATTEMPTS_FILE, 'w') as f:
            f.write("0\n")  # Current index
            for combo in combinations:
                f.write(f"{combo}\n")
        
        logging.info(f"Created {ATTEMPTS_FILE} with {len(combinations)} combinations.")
    else:
        logging.info(f"{ATTEMPTS_FILE} already exists.")

def load_attempts_data():
    """Load existing attempts data from file."""
    with open(ATTEMPTS_FILE, 'r') as f:
        lines = f.readlines()
    
    current_index = int(lines[0].strip())
    combinations = [line.strip() for line in lines[1:]]
    
    return {
        "current_index": current_index,
        "combinations": combinations,
        "total_attempts": current_index
    }

def save_attempts_data(data):
    """Save attempts data to file."""
    with open(ATTEMPTS_FILE, 'w') as f:
        f.write(f"{data['current_index']}\n")
        for combo in data['combinations']:
            f.write(f"{combo}\n")

def get_next_combination():
    """Get the next combination to try and update the attempts file."""
    data = load_attempts_data()
    
    if data["current_index"] >= len(data["combinations"]):
        logging.warning("All combinations have been attempted!")
        return None
    
    combination = data["combinations"][data["current_index"]]
    data["current_index"] += 1
    data["total_attempts"] += 1
    
    save_attempts_data(data)
    
    logging.info(f"Attempting combination {combination} (attempt #{data['total_attempts']})")
    return combination

def get_attempts_status():
    """Get current status of attempts."""
    if not os.path.exists(ATTEMPTS_FILE):
        return {"remaining": 1000000, "attempted": 0, "total": 1000000}
    
    data = load_attempts_data()
    remaining = len(data["combinations"]) - data["current_index"]
    attempted = data["current_index"]
    total = len(data["combinations"])
    
    return {"remaining": remaining, "attempted": attempted, "total": total}
