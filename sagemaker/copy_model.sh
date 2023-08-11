#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <num_copies>"
    exit 1
fi

num_copies=$1
source_bucket="sihan-multiplex-models"
#source_key="resnet/1/resnet.tar.gz"
source_key="1/model_scripted.pt"
destination_bucket="sihan-multiplex-models"

for ((i = 2; i <= num_copies; i++)); do
    destination_key="${i}/model_scripted.pt"
    #destination_key="resnet/${i}/resnet.tar.gz"
    aws s3 cp "s3://${source_bucket}/${source_key}" "s3://${destination_bucket}/${destination_key}"
done
