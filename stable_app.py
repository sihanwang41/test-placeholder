from io import BytesIO
from fastapi import FastAPI
from fastapi.responses import Response
import torch

from ray import serve

app = FastAPI()


@serve.deployment(num_replicas=1, route_prefix="/", autoscaling_config={"min_replicas": 1, "max_replicas": 5},)
@serve.ingress(app)
class APIIngress:
    def __init__(self, gpu_handle) -> None:
        self.handle = gpu_handle

    @app.get(
        "/imagine",
        responses={200: {"content": {"image/png": {}}}},
        response_class=Response,
    )
    async def generate(self, prompt: str, img_size: int = 512):
        assert len(prompt), "prompt parameter cannot be empty"

        image_ref = await self.handle.generate.remote(prompt, img_size=img_size)
        image = await image_ref
        file_stream = BytesIO()
        image.save(file_stream, "PNG")
        return Response(content=file_stream.getvalue(), media_type="image/png")

@serve.deployment(
    ray_actor_options={"num_gpus": 1, "runtime_env": {"pip": ["diffusers==0.14.0", "transformers==4.25.1", "accelerate==0.17.1",]}},
    autoscaling_config={"min_replicas": 1, "max_replicas": 2},
)
class GPUModel:
    def __init__(self):
        from diffusers import EulerDiscreteScheduler, StableDiffusionPipeline

        model_id = "stabilityai/stable-diffusion-2"

        scheduler = EulerDiscreteScheduler.from_pretrained(
            model_id, subfolder="scheduler"
        )
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_id, scheduler=scheduler, revision="fp16", torch_dtype=torch.float16
        )
        self.pipe = self.pipe.to("cuda")

    def generate(self, prompt: str, img_size: int = 512):
        assert len(prompt), "prompt parameter cannot be empty"

        image = self.pipe(prompt, height=img_size, width=img_size).images[0]
        return image


entry = APIIngress.bind(GPUModel.bind())
