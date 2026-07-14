import requests
import random

API_BASE = "http://localhost:5000/api/transactions"

# Example users (replace with real user_ids from your DB)
USER_IDS = [
    "11111111-aaaa-bbbb-cccc-222222222222",
    "33333333-dddd-eeee-ffff-444444444444"
]

DESCRIPTIONS = [
    "Grocery shopping",
    "Online payment",
    "Electricity bill",
    "Movie tickets",
    "Salary credit",
    "Refund processed"
]


def insert_mock_transactions(n=5):
    for _ in range(n):
        user_id = random.choice(USER_IDS)
        amount = round(random.uniform(50, 5000), 2)
        description = random.choice(DESCRIPTIONS)
        status = random.choice(["pending", "completed", "failed"])

        payload = {
            "user_id": user_id,
            "amount": amount,
            "description": description,
            "status": status
        }

        resp = requests.post(API_BASE, json=payload)
        if resp.status_code == 201:
            print("✅ Created:", resp.json()["transaction"])
        else:
            print("❌ Error:", resp.text)


if __name__ == "__main__":
    insert_mock_transactions(10)  # Insert 10 mock txns
