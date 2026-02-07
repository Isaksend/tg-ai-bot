# Используем Python 3.11 как указано в ТЗ [cite: 19]
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем директорию для данных, если она нужна локально [cite: 120]
RUN mkdir -p data/images

# Запуск приложения через uvicorn [cite: 22]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]