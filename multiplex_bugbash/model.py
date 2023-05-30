from ray import serve
import starlette
import asyncio

@serve.deployment(
    num_replicas=3
)
class ModelInferencer:
    
    @serve.multiplexed(max_num_models_per_replica=5)
    async def get_model(self, model_id: str):
        await asyncio.sleep(1)
        return model_id

    async def __call__(self, request: starlette.requests.Request):
        model_id = serve.get_multiplexed_model_id()
        model = await self.get_model(model_id)
        await asyncio.sleep(1)
        return model

entry = ModelInferencer.bind()
