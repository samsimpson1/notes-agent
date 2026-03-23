FROM ghcr.io/astral-sh/uv:0.10.12-debian

COPY . /app

ENV UV_NO_DEV=1
ENV UV_NO_CACHE=1

WORKDIR /app
RUN uv sync --locked

ENTRYPOINT [ "uv", "run", "main.py" ]

LABEL org.opencontainers.image.source="https://github.com/samsimpson1/notes-agent"