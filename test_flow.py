#!/usr/bin/env python
"""Test script to debug create-room and chat access"""
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Create session with retries and don't follow redirects for testing
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)

BASE_URL = 'http://192.168.19.52:5000'

print("=" * 60)
print("TEST 1: Get home page")
print("=" * 60)
try:
    response = session.get(f'{BASE_URL}/', timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Cookies: {session.cookies.get_dict()}")
    print()
except Exception as e:
    print(f"Error: {e}")

print("=" * 60)
print("TEST 2: Create room")
print("=" * 60)
try:
    response = session.post(
        f'{BASE_URL}/create-room',
        json={'name': 'TestRoom'},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    data = response.json()
    room_id = data.get('room_id')
    print(f"Room ID: {room_id}")
    print(f"Cookies after create: {session.cookies.get_dict()}")
    print()
except Exception as e:
    print(f"Error: {e}")

if room_id:
    print("=" * 60)
    print(f"TEST 3: Access chat page (don't follow redirects)")
    print("=" * 60)
    try:
        response = session.get(f'{BASE_URL}/chat/{room_id}', timeout=5, allow_redirects=False)
        print(f"Status: {response.status_code}")
        if response.status_code == 302:
            print(f"REDIRECT TO: {response.headers.get('Location')}")
            print(f"Cookies: {session.cookies.get_dict()}")
        elif response.status_code == 200:
            print("OK - Successfully accessed chat page")
        print()
    except Exception as e:
        print(f"Error: {e}")

