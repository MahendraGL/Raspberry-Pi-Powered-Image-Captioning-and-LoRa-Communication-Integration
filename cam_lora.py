import os
import speech_recognition as sr
import picamera
import sys
import sx126x
import termios
import tty

old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

# serial_num (PiZero, Pi3B+, and Pi4B use "/dev/ttyS0")
# Frequency is set to 868 MHz
# Address is set to 0

node = sx126x.sx126x(serial_num="/dev/ttyS0", freq=868, addr=0, power=22, rssi=True, air_speed=2400, relay=False)

def send_message(message):
    offset_frequency = 868 - 850  # Calculate offset for 868 MHz

    data = bytes([0]) + bytes([0]) + bytes([offset_frequency]) + bytes([node.addr >> 8]) + bytes([node.addr & 0xff]) + bytes([node.offset_freq]) + message.encode()

    node.send(data)

# Define the path to the desktop directory
desktop_path = "/home/raspberry/Desktop/IoT Project"

r = sr.Recognizer()

# Adjust microphone settings (you may need to customize these values)
with sr.Microphone(sample_rate=44100, chunk_size=1024) as source:
    print("Say 'capture' to take a picture...")
    r.adjust_for_ambient_noise(source)  # Adjust for ambient noise

    while True:
        try:
            audio = r.listen(source, timeout=None)  # Listen continuously

            # Recognize speech using Google Web Speech API
            words = r.recognize_google(audio)

            # Print the recognized speech
            print("You said:", words)

            if "capture" in words.lower():
                # Capture an image using the Raspberry Pi camera
                with picamera.PiCamera() as camera:
                    image_path = os.path.join(desktop_path, "captured_image.jpg")
                    camera.capture(image_path)
                print(f"Image captured and saved as '{image_path}'")

                # Send a message to the LoRa node
                send_message("Image captured")

        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            print("Google Web Speech API could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Web Speech API; {e}")

# To stop the code, you can press Ctrl+C to exit the infinite loop

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
