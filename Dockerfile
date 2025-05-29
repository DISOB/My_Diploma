# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt и устанавливаем зависимости
COPY chatbot-dashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY chatbot-dashboard/ .
COPY data/init.sql ./data/
COPY chatbot_metrics.xlsx ./data/
COPY parser/ ./parser/
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

EXPOSE 8501

CMD ["/app/entrypoint.sh"]