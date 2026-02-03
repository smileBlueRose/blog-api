# blog-api
### Entity Relation Diagram
![Blog API ERD](docs/images/blog-api-erd.png)

## Installation and Setup

### 1. Clone repository
```bash
git clone https://github.com/smileBlueRose/blog-api
cd blog-api
```

### 2. Rename secret files
```bash
cd secrets
mv django_secret_key.example django_secret_key
mv db_password.example db_password
cd ..
```

### 3. Install dependencies
```bash
cd blog_api
uv sync
```

### 4. Run server
```bash
uv run manage.py runserver
```

## PostgreSQL Setup (Optional)

By default, the project uses SQLite. To use PostgreSQL instead, complete steps 1-3 above, then:

### 4. Enable PostgreSQL engine
Add `BLOG_DB_ENGINE=postgresql` to `env_files/.env.dev`:
```bash
# It's considered you are at blog-api/
echo "BLOG_DB_ENGINE=postgresql" >> env_files/.env.dev
```

### 5. Start PostgreSQL container
```bash
sudo docker compose --env-file .env.template up -d
```

### 6. Run server
```bash
cd blog_api
uv run manage.py runserver
```