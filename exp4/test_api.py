import requests
import json

BASE_URL = "http://127.0.0.1:5000"

data = {
    "features": [5.1, 3.5, 1.4, 0.2]
}

response = requests.post(
    f"{BASE_URL}/api/predict",
    headers={"Content-Type": "application/json"},
    json=data
)

print(json.dumps(response.json(), indent=2))
