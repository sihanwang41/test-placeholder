from ray import serve
import torch
import starlette
import tarfile
import aiofiles.os
import io
import time

@serve.deployment(ray_actor_options={"runtime_env": {"pip": ["aioboto3"]}}, num_replicas=16, max_concurrent_queries=3)
class ResnetModel:

    def __init__(self):
        self.bucket_name = "sihan-multiplex-models"

    @serve.multiplexed(max_num_models_per_replica=20)
    async def get_model(self, model_id: str):
        start = time.time()
        import aioboto3
        session = aioboto3.Session()
        async with session.resource("s3") as s3:
            obj = await s3.Bucket(self.bucket_name)
            #await aiofiles.os.makedirs(f'{model_id}', exist_ok=True)
            await obj.download_file(f"resnet/{model_id}/resnet.tar.gz", f"{model_id}/resnet.tar.gz")
            #with tarfile.open(f"{model_id}/resnet.tar.gz") as tar:
            #    tar.extractall(path=f"{model_id}/")
            #model = torch.load(f"{model_id}/resnet.pt")
            with tarfile.open('sample.tar.gz') as tar:
                tar.extractall(path='/other/folder')
        print("finish loading ", time.time() - start)
        return model
    
    async def __call__(self, request: starlette.requests.Request):
        data = await request.body()
        model_id = serve.get_multiplexed_model_id()
        model = await self.get_model(model_id)
        data = torch.load(io.BytesIO(data))
        resp = model(data).detach().numpy()
        return resp


entry = ResnetModel.bind()
