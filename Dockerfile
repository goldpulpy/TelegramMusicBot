FROM python:3.12-alpine@sha256:6d43704baacd1bfbe7c295d7f13079d5d8104ed33568873133f8fc69980419df

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --require-hashes -r requirements.txt

COPY --chown=appuser:appgroup bot/ bot/
COPY --chown=appuser:appgroup database/ database/
COPY --chown=appuser:appgroup locales/ locales/
COPY --chown=appuser:appgroup service/ service/
COPY --chown=appuser:appgroup main.py configs.py ./

RUN pybabel compile -d locales -D messages

USER appuser

CMD ["python", "main.py"]