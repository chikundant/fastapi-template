FROM python:3.11-slim as base

WORKDIR /tmp

RUN pip install uv

COPY ./pyproject.toml ./uv.lock* /tmp/

RUN uv export --format requirements.txt --output-file requirements.txt

FROM base as base-requirements

WORKDIR /app

COPY --from=base /tmp/requirements.txt /requirements.txt

ENV PYTHONPATH=./

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

FROM base-requirements as dev
ARG GIT_HASH
ARG GIT_BRANCH
ARG GIT_TAG
ENV GIT_HASH=${GIT_HASH}
ENV GIT_BRANCH=${GIT_BRANCH}
ENV GIT_TAG=${GIT_TAG}

WORKDIR /app

COPY . .

ENTRYPOINT ["python", "app/run.py"]
