import requests
import json

# API endpoint
url = "http://localhost:8000/process-sopquery"

# Request payload
payload = {
    "query": "If a payment status isn't reflected, first call the `/getPaymentStatus/{userID}` API to confirm the status.  \nIf the status is not SUCCESS, check the bank statement document; if the transaction appears there, the account will update in a few days.  \nIf the bank statement also lacks the transaction, file a support ticket with the bank to resolve the issue. Please use this user id as tool input: 12424",
    "issueDescription": "Payment status not reflected for user ID 12424"
}

# Make the API call
try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Raw Response: {response.text}")
    if response.text:
        try:
            print(f"JSON Response: {json.dumps(response.json(), indent=2)}")
        except:
            print("Response is not valid JSON")
except Exception as e:
    print(f"Error: {e}")