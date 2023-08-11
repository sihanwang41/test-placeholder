import requests

import torch
import random
import requests
import time
import io


from locust import HttpUser, task, constant, events

class CodeGenClient(HttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        image = "http://images.cocodataset.org/test-stuff2017/000000024309.jpg"
        utils = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_convnets_processing_utils')
        input = utils.prepare_input_from_uri(image)
        self.inputs = torch.cat(
            [input]
        )
    wait_time = constant(1)

    @task
    def send_serve_requests(self):

        #model_id = random.randint(1, 20)
        model_id = 1
        print("Choose model id: ", model_id)
        for _ in range(1):
            request_meta = {
                "request_type": "InvokeEndpoint",
                "name": "SageMaker",
                "start_time": time.time(),
                "response_length": 0,
                "response": None,
                "context": {},
                "exception": None,
            }
            start_perf_counter = time.perf_counter()

            buff = io.BytesIO()
            torch.save(self.inputs, buff)
            buff.seek(0)
        
            # Service specific config
            base_url = "https://multiplex-benchmark-simple-jrvwy.cld-kvedzwag2qa8i5bj.s.anyscaleuserdata-staging.com"
            token = "MKi8FZMSFWeZotecGC52MM1jz8s7Li03BOElEK71scA"
            headers = {"Authorization": f"Bearer {token}"}
            
            # Requests config
            path = "/"
            full_url = f"{base_url}{path}"
            resp = requests.get(full_url, headers=headers, data=buff)
            #resp = requests.get(full_url, headers=headers)
            if resp.status_code != 200:
                print(resp)
            else:
                request_meta["response_time"] = (
                    time.perf_counter() - start_perf_counter
                ) * 1000
                events.request.fire(**request_meta)


