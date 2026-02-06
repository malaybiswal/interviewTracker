#!/usr/bin/env python3
"""
Update Apple interview Round 2 to Failed status
"""

import requests

# Login
login_response = requests.post('http://localhost:5080/api/login', json={
    'username': 'malay',
    'password': 'malay123'
})

token = login_response.json()['access_token']

# Get Apple interview rounds
rounds_response = requests.get(
    'http://localhost:5080/api/interviews/3/rounds',
    headers={'Authorization': f'Bearer {token}'}
)

print("Current rounds:", rounds_response.json())

# Update the interview overall status to Rejected
update_response = requests.put(
    'http://localhost:5080/api/interviews/3',
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    json={'status': 'Rejected'}
)

print("Update response:", update_response.json())
