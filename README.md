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
- **Framework:** React (Create React App)
- **Routing:** React Router v6
- **Styling:** HTML / CSS (component-scoped stylesheets)
- **3D Rendering:** React Three Fiber with `@react-three/drei`
- **Authentication:** JWT stored in localStorage, attached as Bearer token on all authenticated API calls

### Backend
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Data Validation:** Pydantic
- **ASGI Server:** Uvicorn

### Database
- **Engine:** PostgreSQL with pgvector extension

### AI / Natural Language Processing (NLP)
- **Embeddings:** SentenceTransformers
- **Concept Extraction:** Configurable LLM (local HuggingFace)
- **Relationship Classification:** NLI (cross-encoder/nli-deberta-v3-small)
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
      Components/
      Data/
      Images/
      Login/
      Pages/
    Dockerfile
    package-lock.json
    package.json
  docker-compose.yml
  .env
  .gitignore
  README.md
```

## Running the Application

### Prerequisites

Ensure the following software is installed on the system:

- Docker
- Docker Compose

Verify the installation using:

```bash
docker --version
docker compose version
```

### Environment Configuration

Create a `.env` file in the project root directory and configure the required environment variables.

Example:

```env
# Database
POSTGRES_USER=<user>
POSTGRES_PASSWORD=<password>
POSTGRES_DB=<db_name>
DATABASE_URL=postgresql://<user>:<password>@postgres:5432/<db_name>

# Set to true to wipe and recreate the database schema on startup
RESET_DB=false

# JWT secret for user authentication — minimum 32 characters
JWT_SECRET_KEY=<super-secret-key>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
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
http://localhost:3000
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

To wipe and recreate the schema without removing the Docker volume, set the following in `.env`:

```env
RESET_DB=true
```

Then restart the backend. Set it back to `false` after the first successful start to avoid wiping data on every restart.

To fully remove the database volume (e.g. if credentials or schema configurations have changed):

```bash
docker compose down -v
docker compose up --build
```

This will recreate the PostgreSQL instance using the latest configuration.

### Development Notes

**Running the frontend locally**

The frontend can be run outside Docker for faster development iteration:

```bash
cd universe-web
npm install
npm start
```

The app will be available at `http://localhost:3000`. When running locally, the frontend proxies API requests to the backend. Ensure the backend is running and accessible — either locally at `http://localhost:8000` or via Docker — and that the proxy is configured accordingly in `package.json`:

```json
"proxy": "http://localhost:8000"
```

When running the full stack via Docker Compose, the proxy should point to the Docker backend service name instead.

**Running the backend locally**

The backend can be run outside Docker for faster development iteration:

```bash
cd backend
pip install -r backend_requirements.txt
uvicorn app.main:app --reload
```

When running locally, ensure:

- A PostgreSQL instance is running and accessible at `localhost:5432`
- The `pgvector` extension is installed on that PostgreSQL binary (`brew install pgvector` on macOS, `apt install postgresql-16-pgvector` on Linux)
- `DATABASE_URL` in `.env` uses `localhost` rather than the Docker service name `postgres`
- `TOKENIZERS_PARALLELISM=false` is set in your environment to prevent tokenizer thread conflicts with the async server

The database schema and seed data are created automatically on backend startup — no manual migration step is required.

**Docker networking**

The application is configured using Docker Compose with separate containers for:

* Frontend
* Backend
* PostgreSQL Database

Within the Docker network, the backend connects to PostgreSQL using the hostname `postgres`. When running components outside Docker, local connections should use `localhost` instead.
