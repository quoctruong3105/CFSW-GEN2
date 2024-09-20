FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

###########################################
# Install dependencies                    #
###########################################

RUN apt-get update && \
    apt-get install -y \
    python3.10 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install robotframework robotframework-requests

WORKDIR /test/testcases

COPY /testcases .

WORKDIR /test

CMD [ "python3", "-m", "robot", "-d", "result/", "testcases/api_test.robot" ]
