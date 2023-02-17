from ray import serve

@serve.deployment
class Model:
    def __call__(self):
        return "hello"

model = Model.bind()
