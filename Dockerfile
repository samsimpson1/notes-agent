FROM ghcr.io/astral-sh/uv:0.10.12-debian

COPY . /app

ENV UV_NO_DEV=1

WORKDIR /app
RUN uv sync --locked

ENTRYPOINT [ "uv", "run", "main.py" ]