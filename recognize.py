import sys
import os


from model import classify_image
from camera import capture_image

def main():
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        if not os.path.isfile(image_path):
            print(f"[ERROR] File not found: {image_path}")
            return
    else:
        image_path = "live_capture.jpg"
        print("[INFO] No input image provided. Capturing from camera...")
        capture_image(image_path)

    print(f"[INFO] Classifying image: {image_path}")
    prediction = classify_image(image_path)
    print(f"[RESULT] Predicted dial position: {prediction}")

if __name__ == "__main__":
    main()
