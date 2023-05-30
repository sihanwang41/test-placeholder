from ray import serve
import aioboto3
import torch
import starlette
import requests
import time


@serve.deployment(
    ray_actor_options={
        "runtime_env": {
            "pip": ["aioboto3"]
        }
    },
    num_replicas=3
)
class ModelInferencer:

    def __init__(self):
        self.bucket_name = "sihan-multiplex-models"
    
    @serve.multiplexed(max_num_models_per_replica=3)
    async def get_model(self, model_id: str):
        session = aioboto3.Session()
        async with session.resource("s3") as s3:
            obj = await s3.Bucket(self.bucket_name)
            await obj.download_file(f"{model_id}/model_scripted.pt", f"model_{model_id}.pt")
            return torch.load(f"model_{model_id}.pt")

    async def __call__(self, request: starlette.requests.Request):
        model_id = serve.get_multiplexed_model_id()
        model = await self.get_model(model_id)
        model.forward(torch.rand(64, 3, 512, 512))
        return "123"

entry = ModelInferencer.bind()

