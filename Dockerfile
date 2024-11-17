FROM python:3.11-slim AS build

WORKDIR /workspace

RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get -yq dist-upgrade && \
  DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
    gettext \
    curl \
    build-essential \
    libpq-dev

RUN curl -sSL https://pdm-project.org/install-pdm.py | python3 -

COPY pdm.lock pyproject.toml .
RUN ~/.local/bin/pdm install --prod

COPY . .

FROM python:3.11-slim AS runtime

RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get -yq dist-upgrade && \
  DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
    curl \
    libpq-dev

COPY --from=build /workspace /workspace
WORKDIR /workspace

CMD [ "./entrypoint.sh" ]
