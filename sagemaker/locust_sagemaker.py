import boto3
import io
from locust import HttpUser, task, constant, events
import torch
import time
import random

endpoint_name = "multiplex-resnet-benchmark3"


class CodeGenClient(HttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        image = "http://images.cocodataset.org/test-stuff2017/000000024309.jpg"
        utils = torch.hub.load('NVIDIA/DeepLearningExamples:torchhub', 'nvidia_convnets_processing_utils')
        input = utils.prepare_input_from_uri(image)
        self.inputs = torch.cat(
            [input] * 5
        )
        self.client = boto3.client('sagemaker-runtime', region_name="us-west-2")


    wait_time = constant(1)

    @task
    def send_serve_requests(self):

        model_id = random.randint(1, 20)
        print("Choose model id: ", model_id)
        for _ in range(10):
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
        
            resp = self.client.invoke_endpoint(
                EndpointName = endpoint_name,
                Body = buff,
                TargetModel = f"/{model_id}/resnet.tar.gz"
            )
            if resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
                print(resp)
            else:
                request_meta["response_time"] = (
                    time.perf_counter() - start_perf_counter
                ) * 1000
                events.request.fire(**request_meta)

