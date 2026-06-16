FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# In production on Render we serve the API and frontend from the same origin,
# so VITE_API_URL intentionally defaults to an empty string at build time.
ARG VITE_API_URL=""
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN pip install --no-cache-dir "uv==0.10.0"

COPY . .
RUN if [ -f uv.lock ]; then \
      uv sync --frozen --no-dev; \
    else \
      uv sync --no-dev; \
    fi

COPY --from=frontend-build /app/frontend/dist ./frontend/dist

EXPOSE 8000
CMD ["sh", "-c", "uv run uvicorn backend.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
