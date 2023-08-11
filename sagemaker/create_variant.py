from sagemaker.session import production_variant
import boto3
import sagemaker

model_name = "multiplex-resnet"
endpoint_name = "multiplex-resnet-benchmark3"
variant_name = "multiplex-variant"

container = { 
    'Image': "188439194153.dkr.ecr.us-west-2.amazonaws.com/multiplex-image-resnet:latest",
    'ModelDataUrl': 's3://sihan-multiplex-models/resnet',
    'Mode': 'MultiModel'
}



#iam = boto3.resource('iam')
#role = iam.Role("SageMaker-multiplex-role")
sagemaker_client = boto3.client('sagemaker', region_name="us-west-2")

# Delete endoint
try:
    sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
except Exception as e:
    print(e)

try:
    sagemaker_client.delete_endpoint_config(EndpointConfigName=endpoint_name)
except Exception as e:
    print(e)

try:
    sagemaker_client.delete_model(ModelName=model_name)
except Exception as e:
    print(e)


print(f"Creating model..., {model_name}")
response = sagemaker_client.create_model(
    ModelName = model_name,
    ExecutionRoleArn = "arn:aws:iam::188439194153:role/service-role/SageMaker-multiplex-role",
    Containers = [container]
)


print("Creating endpoint configuration...")
variant1 = production_variant(
    model_name=model_name,
    instance_type="ml.m5.4xlarge",
    initial_instance_count=4,
    variant_name='Variant1',
    initial_weight=1,
)

print("Creating endpoint...")
sm = sagemaker.session.Session(boto3.Session(region_name="us-west-2"))
sm.endpoint_from_production_variants(
    name=endpoint_name,
    production_variants=[variant1]
)

print("Done!")
