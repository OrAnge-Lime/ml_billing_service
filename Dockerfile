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

# Copy
COPY . .

# Create the directory for models if it doesn't exist inside the container
# The actual models should be mounted via a volume in docker-compose
RUN mkdir -p /app/models

# Информирует Docker, что приложение внутри контейнера будет слушать порт 8000. 
# Это чисто информативная инструкция, она не публикует порт наружу. 
# Публикация настраивается в docker-compose.yml.
EXPOSE 8000

# Define the command to run the application using uvicorn
# Use 0.0.0.0 to make it accessible from outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]