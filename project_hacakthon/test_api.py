import requests
import time

BASE_URL = 'http://127.0.0.1:5000/api'

print("Starting tests in 2 seconds...")
time.sleep(2)

print("\n--- 1. Registering a Patient ---")
try:
    res = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "patient@test.com",
        "password": "password123",
        "full_name": "John Doe",
        "role": "patient"
    })
    print("Status Code:", res.status_code)
    print("Response:", res.json())
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to the server at http://127.0.0.1:5000")
    print("Make sure your Flask server is running in the other terminal!")
    exit(1)

print("\n--- 2. Registering a Therapist ---")
res = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "therapist@test.com",
    "password": "password123",
    "full_name": "Dr. Jane Smith",
    "role": "therapist",
    "license_number": "LIC-987654",
    "hourly_rate": 120.0,
    "bio": "Experienced social anxiety specialist."
})
print("Status Code:", res.status_code)
print("Response:", res.json())

print("\n--- 3. Logging in as Patient to get Token ---")
res = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "patient@test.com",
    "password": "password123"
})
token = res.json().get('access_token')
print("Status Code:", res.status_code)
print("Token received!" if token else "Failed to login")

print("\n--- 4. Getting List of Therapists ---")
res = requests.get(f"{BASE_URL}/therapists/")
therapists = res.json()
print("Status Code:", res.status_code)
print("Therapists:", therapists)

if therapists and token:
    therapist_id = therapists[0]['id']
    print(f"\n--- 5. Booking an Appointment with Therapist ID {therapist_id} ---")
    headers = {'Authorization': f'Bearer {token}'}
    res = requests.post(f"{BASE_URL}/appointments/book", headers=headers, json={
        "therapist_id": therapist_id,
        "start_time": "2026-05-01T10:00:00",
        "end_time": "2026-05-01T11:00:00"
    })
    print("Status Code:", res.status_code)
    print("Booking Details:", res.json())
