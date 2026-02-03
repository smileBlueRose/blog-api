# blog-api

### Entity Relation Diagram
![Blog API ERD](docs/images/blog-api-erd.png)

## Installation and Setup
### 1. Clone and navigate to project
```bash
git clone https://github.com/smileBlueRose/blog-api
cd blog-api
```
### 2. Rename secrets
```bash
cd secrets
mv django_secret_key.example django_secret_key
cd ..
```

### 3. Install dependencies and run server
```bash
cd blog_api
uv sync
uv run manage.py runserver
```

## PostgreSQL Setup (Optional)
If you want to use PostgreSQL instead of SQLite:

### 1. Configure secrets
```bash
cd secrets
mv db_password.example db_password
cd ..
```
### 2. Add PostgreSQL engine variable
Add `BLOG_DB_ENGINE=postgresql` to `env_files/.env.dev`

### 3. Start database
```bash
sudo docker compose --env-file .env.template up -d
```
### 4. Install dependencies and run server
```bash
cd blog_api
uv sync
uv run manage.py runserver