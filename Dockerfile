FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/meta-pytorch/OpenEnv.git /app/OpenEnv

RUN pip install --no-cache-dir \
        fastapi \
        "uvicorn[standard]" \
        pydantic \
        openai \
        requests \
        openenv-core && \
    pip install --no-cache-dir -e /app/OpenEnv || true

COPY . .

ENV PYTHONPATH="/app:/app/OpenEnv:/app/OpenEnv/src"

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/health')"

EXPOSE 7860

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]