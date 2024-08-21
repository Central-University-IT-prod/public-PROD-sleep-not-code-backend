FROM docker.io/python:3.12-alpine AS builder

RUN apk add --no-cache curl build-base

ENV PDM_HOME=/opt/pdm
RUN curl -sSL https://pdm-project.org/install-pdm.py | python3 -

WORKDIR /opt/app
COPY pyproject.toml pdm.lock .
COPY src/ src/

RUN $PDM_HOME/bin/pdm sync --no-editable --production


FROM docker.io/python:3.12-alpine

COPY --from=builder /opt/app /opt/app

ENV LITESTAR_APP=app.app:create_app

EXPOSE 8080

WORKDIR /opt/app
CMD [".venv/bin/litestar", "run", "--port=8080", "--host=0.0.0.0"]
