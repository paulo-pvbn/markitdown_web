# MarkItDown Web — imagem única, portátil, roda igual local, no Tailscale
# ou em um VPS.
FROM python:3.12-slim

WORKDIR /app

# Dependências de sistema usadas pelos conversores (ex.: lxml, magika)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia o pacote markitdown deste repo e a webapp
COPY packages/markitdown /app/packages/markitdown
COPY webapp /app/webapp

RUN pip install --no-cache-dir -r /app/webapp/requirements.txt

WORKDIR /app/webapp

ENV HOST=0.0.0.0
ENV PORT=5000

EXPOSE 5000

# Para uso além do laptop pessoal (Tailscale/VPS), troque por gunicorn:
#   CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
CMD ["python", "app.py"]
