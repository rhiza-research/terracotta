FROM python:3.12.2-slim-bullseye AS build_wheel

RUN apt-get update \
    && apt-get install \
    -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*
    
COPY ./ /terracotta

WORKDIR /terracotta

RUN python -m pip install --upgrade pip \
    && python setup.py bdist_wheel

FROM python:3.12.2-slim-bullseye

COPY --from=build_wheel /terracotta/dist/*.whl /terracotta/

RUN apt-get update \
    && apt-get install \
    -y --no-install-recommends \
    build-essential \
    apt-transport-https \
    ca-certificates \
    git \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && apt-get update -y && apt-get install google-cloud-cli -y


RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        $(ls /terracotta/*.whl) \
        pymysql>=1.0.0 \
        psycopg2-binary \
        gunicorn \
        werkzeug==0.16.0 \
        markupsafe==2.0.1 \
    && rm -rf /terracotta

COPY docker/resources /

ENV TC_SERVER_PORT=5000
EXPOSE $TC_SERVER_PORT

CMD ["/entrypoint.sh"]
