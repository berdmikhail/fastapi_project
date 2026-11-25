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