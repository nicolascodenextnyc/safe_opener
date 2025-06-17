import pigpio
import time

# GPIO Pins
DIR_PIN = 20
PULSE_PIN = 21

# Step parameters
GRANULARITY = 800  # e.g. 1.8°/step with 1/16 microstepping
TICK_STEPS = GRANULARITY // 100  # Steps per 1 tick

# Pulse timing
PULSE_WIDTH_US = 1000  # High for 1000 µs
PULSE_GAP_US = 500     # Low for 500 µs

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    print("❌ Cannot connect to pigpio daemon.")
    exit(1)

def rotate_ticks_pigpio(tick_count, direction='CW'):
    # Set direction pin
    dir_value = 0 if direction.upper() == 'CW' else 1
    pi.write(DIR_PIN, dir_value)
    time.sleep(0.1)

    # Generate wave pulses
    total_steps = tick_count * TICK_STEPS
    waveform = []
    for _ in range(total_steps):
        waveform.append(pigpio.pulse(1 << PULSE_PIN, 0, PULSE_WIDTH_US))  # High
        waveform.append(pigpio.pulse(0, 1 << PULSE_PIN, PULSE_GAP_US))    # Low

    # Apply waveform
    pi.set_mode(PULSE_PIN, pigpio.OUTPUT)
    pi.set_mode(DIR_PIN, pigpio.OUTPUT)
    pi.wave_clear()
    pi.wave_add_generic(waveform)
    wave_id = pi.wave_create()
    if wave_id >= 0:
        pi.wave_send_once(wave_id)
        while pi.wave_tx_busy():
            time.sleep(0.01)
        pi.wave_delete(wave_id)
    else:
        print("Failed to create wave.")

    time.sleep(0.5)

def cleanup():
    pi.wave_clear()
    pi.stop()

if __name__ == "__main__":
    try:
        ticks = int(input("Enter number of ticks to rotate: "))
        direction = input("Enter direction (CW or CCW): ").strip().upper()
        if direction not in ['CW', 'CCW']:
            print("Invalid direction.")
        else:
            rotate_ticks_pigpio(ticks, direction)
    except KeyboardInterrupt:
        print("Interrupted.")
    finally:
        cleanup()
