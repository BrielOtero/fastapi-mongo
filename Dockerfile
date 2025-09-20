ARG FUNCTION_DIR="/function"
ARG PYTHON_VERSION="3.13"
# Stage 1 - build
FROM python:${PYTHON_VERSION}-slim AS build-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Create folder
RUN mkdir -p ${FUNCTION_DIR}

# ARG FUNCTION_DIR
WORKDIR ${FUNCTION_DIR}

# Copy the code
COPY ./app ./app
# Copy requirements.txt
COPY ./requirements.txt .
# Copy the start script
COPY ./scripts/entry.sh .

# Change the permissions
RUN chmod +x entry.sh

# Install necessary packages
RUN apt update && \
    apt install -y git && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Install pip dependencies
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt --target .

# Use a slim version of the base Python image to reduce the final image size
FROM python:${PYTHON_VERSION}-slim

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Install necessary packages
# RUN apt update && \
#     apt install -y libgl1  && \
#     apt clean && \
#     rm -rf /var/lib/apt/lists/*

# Copy the lambda emulator to emulate lambda if the runtime is local
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie

# Change the permissions
RUN chmod 755 /usr/bin/aws-lambda-rie

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

# Set runtime interface client as default command for the container runtime
ENTRYPOINT [ "/function/entry.sh" ]

# Pass the name of the function handler as an argument to the runtime
CMD [ "app.main.handler" ]
