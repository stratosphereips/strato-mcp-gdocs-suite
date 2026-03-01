# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

COPY pyproject.toml ./
COPY src/ src/

RUN uv sync --no-dev

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

ENV TOKEN_STORE_PATH=/tokens

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

RUN useradd --uid 1000 --no-create-home --shell /bin/sh appuser \
    && mkdir -p /tokens \
    && chown appuser:appuser /tokens

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

USER appuser

VOLUME ["/tokens"]

LABEL org.opencontainers.image.title="gdocs-suite-mcp" \
      org.opencontainers.image.description="MCP server exposing Google Docs, Sheets, and Slides as tools for Claude" \
      org.opencontainers.image.source="https://github.com/stratosphereips/strato-mcp-gdocs-suite" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.licenses="MIT"

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["serve"]
