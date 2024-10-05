FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

###########################################
# Install dependencies                    #
###########################################

RUN apt-get update && \
    apt-get install -y \
    postgresql \
    python3.10 \
    python3-pip \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install psycopg2 \
    google-auth \
    google-auth-oauthlib \
    google-auth-httplib2 \
    google-api-python-client

WORKDIR /app

COPY . .

CMD [ "python3", "main.py" ]
