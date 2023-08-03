from ray import serve
from ray.serve.drivers import DAGDriver

@serve.deployment
class D1:
    def __call__(self, *args):
        return "D1"

@serve.deployment
class D2:
    def __call__(self, *args):
        return "D2"

@serve.deployment
class D3:
    def __call__(self, *args):
        return "D3"

@serve.deployment
class D4:
    def __call__(self, *args):
        return "D4"

@serve.deployment
class D5:
    def __call__(self, *args):
        return "D5"

entry = DAGDriver.bind(
    {
        "/d1": D1.bind(),
        "/d2": D2.bind(),
        "/d3": D3.bind(),
        "/d4": D4.bind(),
        "/d5": D5.bind(),
    }
)

'''
serve.run(entry)

import requests
print(requests.post(f"http://127.0.0.1:8000/d1", json=1).json())
print(requests.post(f"http://127.0.0.1:8000/d2", json=1).json())
print(requests.post(f"http://127.0.0.1:8000/d3", json=1).json())
print(requests.post(f"http://127.0.0.1:8000/d4", json=1).json())
print(requests.post(f"http://127.0.0.1:8000/d5", json=1).json())
'''
