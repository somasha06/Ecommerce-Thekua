import random

def generate_otp():
    return str(random.randint(100000,999999))

def send_otp(destination,otp):
    print(f"OTP sent to {destination}: {otp}")