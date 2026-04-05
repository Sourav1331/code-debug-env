FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Clone OpenEnv
RUN git clone https://github.com/meta-pytorch/OpenEnv.git /app/OpenEnv

# Install dependencies
RUN pip install --no-cache-dir \
        fastapi \
        "uvicorn[standard]" \
        pydantic \
        openai \
        requests \
        openenv-core

# Install your project requirements
COPY . .
RUN pip install --no-cache-dir -r server/requirements.txt

# Install OpenEnv (editable)
RUN pip install --no-cache-dir -e /app/OpenEnv

# Set Python path
ENV PYTHONPATH="/app:/app/OpenEnv:/app/OpenEnv/src"

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]