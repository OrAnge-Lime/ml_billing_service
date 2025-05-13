FROM python:3.11-slim

# Set environment variables
#  Запрещает Python создавать .pyc (скомпилированный байт-код). экономит место и не нужно в контейнерах.
ENV PYTHONDONTWRITEBYTECODE 1
# Гарантирует, что выводы Python (например, print или логи) сразу отправляются в stdout/stderr, 
# а не буферизуются. Это важно для просмотра логов контейнера в реальном времени.
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

