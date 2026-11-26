# fastapi_project

# FastAPI Microservices: ToDo & Short URL

Два независимых микросервиса на базе **FastAPI** с хранением данных в **SQLite** и контейнеризацией через **Docker** с использованием именованных томов.

## Структура проекта

```text
.
├── ToDo/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── ShortURL/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
└── README.md
```

## Образы на Docker Hub

* **ToDo-сервис:** [berdmikhail/todo-service](https://hub.docker.com/r/berdmikhail/todo-service)
* **Сервис сокращения ссылок:** [berdmikhail/shorturl-service](https://hub.docker.com/r/berdmikhail/shorturl-service)

---

## Запуск через Docker

### 1. Создание именованных томов для сохранения баз данных
```bash
docker volume create todo_data
docker volume create shorturl_data
```

### 2. Запуск готовых образов из Docker Hub
```bash
docker run -d --name todo_service -p 8000:80 -v todo_data:/app/data berdmikhail/todo-service:latest
docker run -d --name shorturl_service -p 8001:80 -v shorturl_data:/app/data berdmikhail/shorturl-service:latest
```

### 3. Локальная сборка образов (не обязательно)
```bash
docker build -t berdmikhail/todo-service:latest todo_app/
docker build -t berdmikhail/shorturl-service:latest ShortURL/
```

### 4. Проверка статуса и просмотр логов

Проверить, что оба контейнера запущены и работают:
```bash
docker ps
```

Посмотреть логи сервисов (удобно для отладки запросов и проверки инициализации SQLite):
```bash
docker logs todo_service
docker logs shorturl_service
```

Просмотр логов в реальном времени (выход по `Ctrl+C`):
```bash
docker logs -f todo_service
```

### 5. Перезапуск и проверка сохранения данных

Перезапустить контейнеры без потери данных в SQLite:
```bash
docker restart todo_service shorturl_service
```

Проверить список подключённых именованных томов и их расположение:
```bash
docker volume ls
docker volume inspect todo_data shorturl_data
```

### 6. Обновление образов из Docker Hub

Если на Docker Hub загружена новая версия образов, скачайте её и пересоздайте контейнеры (данные в томах сохранятся):
```bash
docker pull berdmikhail/todo-service:latest
docker pull berdmikhail/shorturl-service:latest

docker rm -f todo_service shorturl_service

docker run -d --name todo_service -p 8000:80 -v todo_data:/app/data berdmikhail/todo-service:latest
docker run -d --name shorturl_service -p 8001:80 -v shorturl_data:/app/data berdmikhail/shorturl-service:latest
```

### 7. Остановка и очистка окружения

Временно остановить контейнеры (их можно снова запустить через `docker start todo_service shorturl_service`):
```bash
docker stop todo_service shorturl_service
```

Остановить и удалить контейнеры (базы данных в томах останутся):
```bash
docker rm -f todo_service shorturl_service
```

Полная очистка вместе с базами данных и локальными образами:
```bash
docker rm -f todo_service shorturl_service
docker volume rm todo_data shorturl_data
docker rmi berdmikhail/todo-service:latest berdmikhail/shorturl-service:latest
```
---

## Локальный запуск (без Docker)

Для запуска каждого сервиса откройте отдельный терминал, перейдите в директорию нужного приложения, установите зависимости и запустите Uvicorn.

### ToDo-сервис (порт 8000)
```bash
cd ToDo
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Сервис сокращения URL (порт 8001)
```bash
cd ShortURL
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001
```

---

## Документация API и эндпоинты

После запуска интерактивная документация Swagger UI доступна по адресам:
* **ToDo-сервис:** http://localhost:8000/docs
* **Short URL:** http://localhost:8001/docs

### ToDo-сервис
* `POST /items` — создание новой задачи
* `GET /items` — получение списка всех задач
* `GET /items/{item_id}` — получение задачи по ID
* `PUT /items/{item_id}` — обновление задачи по ID
* `DELETE /items/{item_id}` — удаление задачи по ID

### Сервис сокращения URL
* `POST /shorten` — создание короткой ссылки из полного URL
* `GET /{short_id}` — перенаправление на исходный URL
* `GET /stats/{short_id}` — получение информации о сокращённой ссылке
