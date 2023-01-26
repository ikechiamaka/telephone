import RPi.GPIO as GPIO
import time
import subprocess
import os

# Set up the GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# Welcome message
subprocess.run(["aplay", "/path/to/welcome_message.mp3"])

while True:
    input_state = GPIO.input(23)
    if input_state == False:
        # Record audio for 60 seconds
        subprocess.run(["arecord", "-d", "60", "-f", "S16_LE", "-r", "16000", "/path/to/recording.wav"])
        # Convert audio to mp3
        subprocess.run(["lame", "-b", "128", "/path/to/recording.wav", "/path/to/recording.mp3"])
        try:
            date = time.strftime("%Y-%m-%d")
            # Create a folder with the current date on the SD card
            sd_folder_path = "/path/to/sd_card/recordings/{}".format(date)
            create_folder(sd_folder_path)
            # Create a folder with the current date on the USB stick
            usb_folder_path = "/path/to/usb_stick/recordings/{}".format(date)
            create_folder(usb_folder_path)
            # Move the recording to the folder on the SD card
            subprocess.run(["mv", "/path/to/recording.mp3", "{}/recording_{}.mp3".format(sd_folder_path, date)])
            # Backup the recording to the USB stick
            subprocess.run(["cp", "{}/recording_{}.mp3".format(sd_folder_path, date), "{}/recording_{}.mp3".format(usb_folder_path, date)])
            # Check for wifi connection
            try:
                subprocess.check_output(["ping", "-c", "1", "google.com"])
                # Upload the recording to a cloud folder
                subprocess.run(["rclone", "copy", "{}/recording_{}.mp3".format(sd_folder_path, date), "remote:cloud_folder/{}/".format(date)])
            except subprocess.CalledProcessError as e:
                print("Command failed with exit status: ", e.returncode)
        except Exception as e:
            print("An error occurred: ", e)
