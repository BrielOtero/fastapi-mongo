#!/bin/bash
# Author: Gabriel Otero

set -o pipefail

# Build and run
IMAGE="fastapi-mongo"

echo "Cleaning up any existing containers..."
docker stop $IMAGE
docker rm $IMAGE

# Get the Python version from the .python-version file
PYTHON_VERSION=$(cat .python-version)

echo "Building the image..."
docker build \
    --platform linux/arm64 \
    --build-arg PYTHON_VERSION=${PYTHON_VERSION} \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg BUILDKIT_MAX_PARALLELISM=$(nproc) \
    -t $IMAGE \
    -f Dockerfile \
    --progress=plain \
    --no-cache . 


echo "Running the container..."
docker run \
    -dit \
    -v ~/.aws:/root/.aws \
    --platform linux/arm64 \
    --name $IMAGE \
    -p 8000:8000 \
    -p 9001:8080 $IMAGE

# Simulate payload from API Gateway -> Proxy -> Lambda
echo "Testing..."
sleep .1
curl -s -o /dev/null -w "Total time: %{time_total}s\n" \
  -X POST "http://localhost:9001/2015-03-31/functions/function/invocations" \
  -d @tests/lambda/test_main.json

echo "Test successful!"
