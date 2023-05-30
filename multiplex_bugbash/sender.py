import requests
import random


while True:
    model_id = random.randint(1,9)
    resp = requests.get("http://localhost:8000", headers={"serve_multiplexed_model_id": str(model_id)})
