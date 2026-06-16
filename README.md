# Project Onion

An artificial intelligence-augmented semantic learning platform designed to transform educational study materials into an interactive knowledge universe.

Project Onion processes uploaded notes, extracts key concepts, generates semantic embeddings, and visualizes them within an explorable semantic space. The platform enables students to discover conceptual relationships between topics, navigate their knowledge base via an interactive interface, and identify potential knowledge gaps.

## Architecture Overview

The system utilizes a modular, full-stack architecture comprised of:

1. **Frontend:** Developed using React and Vite.
2. **Backend API:** Built with FastAPI.
3. **Semantic Processing Pipeline:** Manages content extraction and embedding logic.
4. **Database:** Powered by PostgreSQL for data persistence.

## Semantic Processing Pipeline

The semantic pipeline processes source documents through the following phases:

1. **Document Upload:** Students upload source materials in various formats.
2. **Text Extraction:** Parsing, extraction and chunking of raw textual content.
3. **Concept Extraction:** Identifying core academic concepts within the text segments.
4. **Embedding Generation:** Creating semantic vector representations.
5. **Dimension Reduction:** Formatting high-dimensional vectors for spatial visualization.
6. **Database Persistence:** Committing the processed data to the PostgreSQL database.

## Technology Stack

### Frontend
- **Framework:** React
- **Styling:** HTML / CSS
- **3D Function:** React 3 Fiber

### Backend
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Data Validation:** Pydantic
- **ASGI Server:** Uvicorn

### Database
- **Engine:** PostgreSQL

### AI / Natural Language Processing (NLP)
- **Embeddings:** SentenceTransformers
- **Dimensionality Reduction:** PCA

### Infrastructure
- **Containerization:** Docker
- **Orchestration:** Docker Compose

## Project Structure

```text
project-root/
  backend/
    app/
      configs/
      db/
      pipelines/
      routes/
      schemas/
      services/
      logging.py
      main.py
    backend_requirements.txt
    Dockerfile
  infrastructure/
    db/
  misc/
  universe-web/
    public/
    src/
    Dockerfile
    package-lock.josn
    package.json
  docker-compose.yml
  .env
  .gitignore
  README.md
```

## Running the Application

### Prerequisites

Ensure the following software is installed on the system:

* Docker
* Docker Compose

Verify the installation using:

```bash
docker --version
docker compose version
```

### Environment Configuration

Create a `.env` file in the project root directory and configure the required environment variables.

Example:

```env
POSTGRES_USER=<user>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<db_name>

DATABASE_URL=postgresql://<user>:<password>@postgres:5432/<db_name>
```

Adjust the values according to the local development environment.

### Building and Starting Services

From the project root directory, execute:

```bash
docker compose up --build
```

This command builds the required images and starts the frontend, backend, and database services.

To run the services in detached mode:

```bash
docker compose up -d --build
```

### Accessing the Application

After all containers have started successfully:

Frontend

```text
http://localhost:3001
```

Backend API

```text
http://localhost:8000
```

Backend API Documentation

```text
http://localhost:8000/docs
```

### Stopping Services

To stop all running containers:

```bash
docker compose down
```

### Resetting the Database

If database credentials or schema configurations have changed, remove the existing database volume before rebuilding:

```bash
docker compose down -v
docker compose up --build
```

This will recreate the PostgreSQL instance using the latest configuration.

### Development Notes

The application is configured using Docker Compose with separate containers for:

* Frontend
* Backend
* PostgreSQL Database

Within the Docker network, backend services connect to PostgreSQL using the hostname `postgres`. When running components outside Docker, local connections should use `localhost` instead.
