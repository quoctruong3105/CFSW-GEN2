FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

###########################################
# Install dependencies                    #
###########################################

RUN apt-get update && \
    apt-get install -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir robotframework robotframework-requests

WORKDIR /test/testcases

COPY /testcases .

WORKDIR /test
