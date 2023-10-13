FROM python:3.11 as builder

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYROOT /pyroot
ENV PYTHONUSERBASE $PYROOT

RUN env


FROM builder AS base

# Install pipenv and compilation dependencies
RUN pip install --no-cache pipenv

COPY Pipfile .
COPY Pipfile.lock .
RUN PIP_USER=1 PIP_IGNORE_INSTALLED=1 pipenv install --system --deploy

FROM base AS base-dev

RUN PIP_USER=1 PIP_IGNORE_INSTALLED=1 pipenv install --system --deploy --dev

FROM base-dev AS dev

COPY --from=base-dev $PYROOT/lib/ $PYROOT/lib/

WORKDIR /app

COPY entrypoint.dev.sh .
RUN chmod +x entrypoint.dev.sh
RUN pip3 install --no-cache-dir awscli

RUN mkdir -p /app/system_configs
RUN env

# Install application into container
COPY . .

RUN rm -rf /parser/system_configs

# Run the application
CMD ["sh", "/app/entrypoint.dev.sh"]
