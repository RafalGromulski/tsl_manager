# 🔐 TSL Manager

**TSL Manager** is a web application designed to manage the process of downloading Certificate Revocation Lists (CRLs) from qualified trust service providers across all EU countries. The application is tightly integrated with Trusted Service Lists (TSLs) and facilitates operators in tracking, validating, and organizing trust services in an efficient and scalable way.

> The process of downloading TSL files is handled by a separate component – `tsl_manager_downloader`. This application (TSL Manager) focuses on interpreting and managing the data extracted from TSLs

---

## 📚 Project Motivation

Managing trust services is complex due to:
- Constant changes in service providers (new entries, takeovers, deactivations)
- Missing CRL URLs in TSLs, requiring manual lookup
- Hundreds of active providers across the EU

**TSL Manager** provides a solution to track and manage these challenges in a structured, UI-driven way.

---

## ⚙️ Core Functionality

The application uses **two main data sources**:
1. **Internal Database** – maintains metadata about identified trust services from TSL files, including:
   - Service status: `Not served (new)`, `Not served (withdrawn)`, `Served`
   - CRL URL status: `CRL URL defined`, `CRL URL undefined`
2. **TSL Files** – downloaded and parsed on a regular basis to update trust services in the internal database.

### Main Views
- **All Services** – displays all known trust services from the internal database, regardless of status. This view allows operators to browse, filter, and search across all registered entries, facilitating audits, reviews, and batch actions.
- **New Services** – newly added or changed services that require operator input
- **Processed Services** – reviewed and annotated services
- **Service Details** – detailed information extracted from the TSL
- **TSL Status** – history and validity of imported TSL files


### Operator Actions
- View service details
- Edit/add CRL URLs
- Confirm removal of inactive services
- Filter and search by service name

---

## 🧱 Tech Stack

- **Docker + Docker Compose**
- **Python + Django** (backend & frontend)
- **PostgreSQL 15.5**
- **Redis 7**
- **Celery + Flower** (background task queue)
- **pgAdmin** (PostgreSQL UI)
- **Nginx**

---

## 🚀 Quick Start


### Environment Configuration

This project requires three `.env` files to manage runtime variables:

- `.env` in the root directory
- `.env` inside the `tsl_manager_database/` directory
- `.env` inside the `tsl_manager_project/` directory

Template files (`.env.example`) are provided in the locations. To prepare them:

```bash
cp .env.example .env
cp tsl_manager_database/.env.example tsl_manager_database/.env
cp tsl_manager_project/.env.example tsl_manager_project/.env  
```

Then fill in the required values before launching the application.

> ⚠️ **Important:**  
> Never commit `.env` files to version control – they may contain sensitive credentials.     
> Instead, use a `.env.example` file to document the required configuration variables.


### Build & Run

```bash
docker-compose up --build
```

---

## 📂 Docker Services Overview

| Service Name             | Description                                                           | Port(s)      |
|--------------------------|------------------------------------------------------------------------|--------------|
| `tsl_manager_project`    | Django web application (backend + built-in frontend)                   | 8000         |
| `tsl_manager_nginx`      | Reverse proxy for the Django app; serves static/media files            | 8080         |
| `postgres_database`      | PostgreSQL database used by the Django backend                         | 5432         |
| `tsl_manager_pgadmin`    | pgAdmin – web UI for PostgreSQL                                        | 5050         |
| `redis`                  | Redis server acting as Celery message broker                           | 6379         |
| `tsl_manager_downloader` | Celery worker for background task execution                            | —            |
| `tsl_manager_beat`       | Celery beat scheduler for periodic tasks                               | —            |
| `flower`                 | Web UI for monitoring Celery tasks                                     | 5555         |

---

### 🌐 Accessing Services

Once the stack is running, the following services will be accessible on your local machine:

- **Main application (via Nginx):** http://localhost:8080  
- **pgAdmin (PostgreSQL UI):** http://localhost:5050  
- **Flower (Celery dashboard):** http://localhost:5555

---

## ⚙️ Environment Variables

### Root `.env`

| Variable Name               | Description                              |
|-----------------------------|------------------------------------------|
| `PGADMIN_EMAIL`             | Email address for pgAdmin login          |
| `PGADMIN_PASSWORD`          | Password for pgAdmin user                |


### `tsl_manager_project/.env`

| Variable Name               | Description                              |
|-----------------------------|------------------------------------------|
| `SECRET_KEY`                | Django secret key                        |
| `DEBUG`                     | Django debug mode (`True` or `False`)    |
| `POSTGRES_DB`               | Database name                            |
| `POSTGRES_USER`             | Database user                            |
| `POSTGRES_PASSWORD`         | Database password                        |
| `POSTGRES_HOST`             | Hostname of the PostgreSQL container     |
| `POSTGRES_PORT`             | PostgreSQL port (default: 5432)          |
| `DJANGO_SUPERUSER_USERNAME` | Initial Django admin username            |
| `DJANGO_SUPERUSER_EMAIL`    | Initial Django admin email               |
| `DJANGO_SUPERUSER_PASSWORD` | Initial Django admin password            |

### `tsl_manager_database/.env`

| Variable Name               | Description                              |
|-----------------------------|------------------------------------------|
| `POSTGRES_PASSWORD`         | PostgreSQL user password                 |
| `POSTGRES_USER`             | PostgreSQL username                      |
| `POSTGRES_DB`               | PostgreSQL database name                 |

---

[//]: # (## 🧪 Running Tests)

[//]: # ()
[//]: # (To run tests:)

[//]: # ()
[//]: # (```bash)

[//]: # (docker-compose exec tsl_manager_project python manage.py test)

[//]: # (````)

[//]: # (---)

## 🛠️ Useful Commands

```bash
# Run migrations
docker-compose exec tsl_manager_project python manage.py migrate

# Create admin user
docker-compose exec tsl_manager_project python manage.py createsuperuser

# Django shell
docker-compose exec tsl_manager_project python manage.py shell
```
---

## 🚧 Project Status

![Project Status: In Progress](https://img.shields.io/badge/status-in--progress-yellow)

This project is currently in **active development**.  
Expect frequent updates, structural changes, and evolving functionality.  
Bug reports and feature suggestions are welcome during this phase.

---

## 🛣 Roadmap

[//]: # (- [x] TSL import and database sync  )

[//]: # (- [x] Basic UI for managing services  )

[//]: # (- [x] All Services View  )

[//]: # (- [ ] Configurable TSL sync interval  )

[//]: # (- [ ] Automated testing & CI pipeline  )

[//]: # (- [ ] Swagger/OpenAPI documentation  )

---

## 🤝 Contributing

[//]: # (Feel free to fork the project and submit pull requests.  )
[//]: # (Bug reports and feature suggestions are welcome via [GitHub Issues]&#40;https://github.com/your-repo/issues&#41;.)

---

[//]: # (## 📄 License)

[//]: # (This project is licensed under the **MIT License** – see the `LICENSE` file for details.)

[//]: # (---)

## 👤 Author

- https://github.com/RafalGromulski
