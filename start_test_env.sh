#!/bin/bash

# Docker build
docker build -t create_agent_lambda_test_image .

# Docker run
docker run \
--env-file .env \
-v ./:/app \
-d \
--name create_agent_lambda_test_container \
recomendation_engine_test_image

# Launch bash
docker exec -it create_agent_lambda_test_container bash