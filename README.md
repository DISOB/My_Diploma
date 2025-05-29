# Chatbot Dashboard

Проект для визуализации и анализа метрик чат-бота с автоматическим импортом данных из Excel.

## 🚀 Возможности

- Импорт метрик из Excel-файла в PostgreSQL
- Два режима просмотра: менеджерский и аналитический дашборд
- Автоматическое обновление данных
- Docker-контейнеризация для простого развертывания

## 📋 Требования

- Docker Desktop
- Docker Compose

## 🔧 Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/chatbot-dashboard.git
cd chatbot-dashboard
```

2. Запустите проект:
```bash
docker compose up --build
```

3. Откройте дашборд:
http://localhost:8501

## 📁 Структура проекта

```
chatbot-dashboard/
├── dashboard/          # Streamlit-дашборд
├── parser/            # Парсер Excel-файла
├── data/             # SQL-скрипты и данные
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 🛠 Технологии

- Python 3.11
- Streamlit
- PostgreSQL
- Docker
- Pandas
