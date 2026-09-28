import cv2
import base64
import os
import getpass
from openai import OpenAI

# Securely ask for the API key in the terminal every time you run it
api_key = getpass.getpass("🔑 Enter your OpenAI API Key (input will be hidden): ")

# Clean the key to strip invisible trailing/leading spaces or breaks
clean_key = api_key.strip()

# Pass the cleaned key into the client
client = OpenAI(api_key=clean_key)

# Initialize the OpenAI client. It automatically looks for the OPENAI_API_KEY environment variable.
client = OpenAI()

def encode_image_to_base64(frame):
    """Convert an OpenCV frame into a base64 string for the API."""
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')

def analyze_medication(base64_image):
    """Sends the image to OpenAI Vision API to check medication and label."""
    print("\n[AI] Analyzing image... please wait.")
    
    prompt = (
        "You are a strict medical safety assistant. Look closely at this image. "
        "1. Identify the medication name and strength from the physical pill bottle/box. "
        "2. Identify the medication name and strength from the prescription/cartfill label. "
        "3. Compare them and state clearly if they MATCH or DO NOT MATCH. "
        "Provide your answer in a clear, easy-to-read format."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Using a multimodal vision model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error connecting to AI API: {str(e)}"

def main():
    # Open the laptop's default camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        print("macOS Note: Ensure VS Code or Terminal has permission to access your Camera in System Settings.")
        return

    print("==================================================")
    print("Medication Verification Scanner Active")
    print("Instructions:")
    print("1. Hold the medication bottle and the label up to the camera.")
    print("2. Ensure text is clear, well-lit, and in focus.")
    print("3. Press 'SPACEBAR' to capture and verify.")
    print("4. Press 'Q' to quit.")
    print("==================================================")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Display the live camera feed
        cv2.imshow("Medication Scanner (Press Space to Verify)", frame)

        key = cv2.waitKey(1) & 0xFF
        
        # Press Spacebar to capture
        if key == ord(' '):
            # Encode frame to base64
            base64_image = encode_image_to_base64(frame)
            
            # Send to AI
            result = analyze_medication(base64_image)
            
            print("\n=== VERIFICATION RESULT ===")
            print(result)
            print("===========================\n")
            print("Ready for next scan. Press Space to scan again, or 'Q' to quit.")

        # Press 'q' to quit
        elif key == ord('q'):
            break

    # Clean up windows and camera resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
