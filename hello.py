from ray import serve

@serve.deployment
class Model:
    def __call__(self):
        return "hello"

serve.run(Model.bind(), name="my_app")
