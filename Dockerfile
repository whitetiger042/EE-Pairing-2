# ============================================================================
# MULTI-STAGE DOCKERFILE
# Environments: dev, uat, prod
# ============================================================================

ARG PYTHON_VERSION=3.12.8-slim-bookworm

# -----------------------------------------------------------------------------
# STAGE 1: BUILDER - Install dependencies
# -----------------------------------------------------------------------------
FROM python:${PYTHON_VERSION} AS builder

WORKDIR /app


RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"


COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# -----------------------------------------------------------------------------
# STAGE 2: DEV 
# -----------------------------------------------------------------------------
FROM python:${PYTHON_VERSION} AS dev

WORKDIR /app

RUN useradd --create-home appuser

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    FLASK_DEBUG=1 \
    ENV=dev

COPY --chown=appuser:appuser app.py .

USER appuser
EXPOSE 8080

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080", "--reload"]


# -----------------------------------------------------------------------------
# STAGE 3: UAT 
# -----------------------------------------------------------------------------
FROM python:${PYTHON_VERSION} AS uat

WORKDIR /app

RUN useradd --create-home appuser

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    ENV=uat

COPY --chown=appuser:appuser app.py .

USER appuser
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

CMD ["python", "app.py"]


# -----------------------------------------------------------------------------
# STAGE 4: PROD 
# -----------------------------------------------------------------------------
FROM python:${PYTHON_VERSION} AS prod

WORKDIR /app

RUN useradd --create-home appuser && \
    apt-get update && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENV=prod

COPY --chown=appuser:appuser app.py .

RUN chmod 444 app.py

USER appuser
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

CMD ["python", "app.py"]
