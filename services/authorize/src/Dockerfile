FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

###########################################
# Install dependencies                    #
###########################################

RUN apt-get update && \
    apt-get install -y \
    curl \
    python3.10 \
    python3-pip \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install flask psycopg2-binary python-dotenv

WORKDIR /app

COPY . .

CMD [ "python3", "app.py" ]
