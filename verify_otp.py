import os
import auth

print("Testing with placeholder credentials...")
os.environ['SMTP_EMAIL'] = 'your_email@gmail.com'
os.environ['SMTP_PASSWORD'] = 'your_app_password'
result = auth.send_otp_email('test@example.com', '123456')
print(f"Result (Expected True): {result}")

print("\nTesting with empty credentials...")
os.environ['SMTP_EMAIL'] = ''
os.environ['SMTP_PASSWORD'] = ''
result = auth.send_otp_email('test@example.com', '123456')
print(f"Result (Expected True): {result}")

print("\nTesting with potential real (but invalid) credentials...")
os.environ['SMTP_EMAIL'] = 'realemail@gmail.com'
os.environ['SMTP_PASSWORD'] = 'somepassword'
# This should attempt SMTP and fail, returning False
result = auth.send_otp_email('test@example.com', '123456')
print(f"Result (Expected False): {result}")
