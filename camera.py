import cv2

def capture_image(filename):
    cap = cv2.VideoCapture(0)
    
    # Set camera properties for better focus
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus
    cap.set(cv2.CAP_PROP_FOCUS, 0)      # Set focus to auto
    
    # Allow more time for camera to warm up and focus
    for _ in range(30):  # Increased from 10 to 30 frames
        cap.read()
    
    # Add delay for autofocus to complete
    import time
    time.sleep(2)
    
    ret, frame = cap.read()
    cap.release()
    if ret:
        cv2.imwrite(filename, frame)
    else:
        print("Failed to capture image")
