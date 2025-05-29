#!/bin/bash
set -e

# Устанавливаем зависимости
apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Ждем, пока база будет доступна
until pg_isready -h db -U myuser; do
  echo "Жду, пока база данных станет доступна..."
  sleep 2
done

# Импортируем данные (ошибки не критичны)
python /app/parser/main.py || true

# Запускаем Streamlit
exec streamlit run main.py --server.address=0.0.0.0 --server.port=8501
