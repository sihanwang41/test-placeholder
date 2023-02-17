from ray import serve
from transformers import AutoTokenizer, AutoModelForCausalLM
from fastapi import FastAPI, Request
import torch


app = FastAPI()

@serve.deployment(ray_actor_options={"num_gpus": 1}, autoscaling_config={"min_replicas": 1, "max_replicas": 8}, max_concurrent_queries=2)
@serve.ingress(app)
class Model:
    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-multi")
        self.model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-multi").to(self.device)

    @app.post("/")
    async def run(self, req: Request):
        data = await req.json()
        text = data["text"]
        input_ids = self.tokenizer(text, return_tensors="pt").input_ids
        input_ids = input_ids.to(self.device)
        generated_ids = self.model.generate(input_ids, max_length=128)
        return self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)

model = Model.bind()
