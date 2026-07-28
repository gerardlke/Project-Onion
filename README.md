# Project Onion

An artificial intelligence-augmented semantic learning platform designed to transform educational study materials into an interactive knowledge universe.

Project Onion processes uploaded notes, extracts key concepts, generates semantic embeddings, and visualizes them within an explorable semantic space. The platform enables students to discover conceptual relationships between topics, navigate their knowledge base via an interactive interface, and identify potential knowledge gaps.

## User Flow

1. Register an account and sign in.
2. Create one or more topics to organise your study materials.
3. Upload documents to a topic. The platform extracts concepts, generates embeddings, and maps relationships automatically in the background.
4. Navigate to the universe to explore your concepts as an interactive 3D star map, where proximity reflects semantic similarity and edges represent classified relationships between concepts.
5. Click any concept node or relationship edge to inspect its detail.
6. Use the AI chat assistant to ask questions about your uploaded concepts and receive answers grounded in your own study materials.

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
3. **Concept Extraction:** Identifying idea-level academic concepts within semantic chunks using an LLM prompt, extracting concepts rather than surface-level entity nouns.
4. **Embedding Generation:** Creating semantic vector representations.
5. **Dimension Reduction:** Formatting high-dimensional vectors for spatial visualization.
6. **Database Persistence:** Committing the processed data to the PostgreSQL database.

## Technology Stack

### Frontend
- **Framework:** React (Create React App)
- **Routing:** React Router v6
- **Styling:** HTML / CSS (component-scoped stylesheets)
- **3D Rendering:** React Three Fiber with `@react-three/drei` and `@react-spring/three`
- **Authentication:** JWT stored in localStorage, attached as Bearer token on all authenticated API calls
- **Icons:** FontAwesome (`@fortawesome/react-fontawesome`)
- **HTTP Client:** Native Fetch API via centralised `apiFetch` utility with automatic Bearer token injection

### Backend
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Data Validation:** Pydantic
- **ASGI Server:** Uvicorn

### Database
- **Engine:** PostgreSQL with pgvector extension

### AI / Natural Language Processing (NLP)
- **Embeddings**: SentenceTransformers (local) or HuggingFace Inference API (cloud)
- **Concept Extraction**: Configurable LLM — local HuggingFace, Groq, or OpenAI via provider abstraction
- **Relationship Classification**: LLM-based classification via structured JSON prompt
- **Relationship Similarity Search**: pgvector cosine distance
- **Dimensionality Reduction**: numpy-only PCA
- **RAG Chatbot**: Retrieval-augmented generation using pgvector similarity search and LLM response generation

### Infrastructure
- **Containerization:** Docker
- **Orchestration:** Docker Compose

- The application runs as three containers orchestrated by Docker Compose:

  | Container | Image | Responsibility |
  |---|---|---|
  | project_onion_frontend | Node | Serves the React application |
  | project_onion_backend | Python 3.12 slim | Runs the FastAPI application via Uvicorn |
  | project_onion_db | pgvector/pgvector:pg16 | PostgreSQL with pgvector extension pre-compiled |

  The `pgvector/pgvector:pg16` image is used instead of the official PostgreSQL image because pgvector is a C extension that must be compiled against the specific PostgreSQL binary and cannot be installed at runtime without building from source.

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
        AiChatBot.js
        AiChatBot.css
        CursorGlow.js
        NetworkEdge.js
        NetworkNodes.js
        NetworkScene.js
        Sidebar.js
        Sidebar.css
        UserIconButton.js
        UserIconButton.css
      Data/
        network.js
      Images/
        backgroundimage.jpg
        Star.png
      Login/
        Login.js
        Login.css
        Register.js
      Pages/
        Universe.js
        Universe.css
        Upload.js
        Upload.css
      App.js
      App.css
      Api.js
      index.js
      index.css
    vercel.json
    Dockerfile
    package.json
    package-lock.json
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

# LLM provider
GROQ_API_KEY=<your_groq_key>
OPENAI_API_KEY=<your_openai_key>
ENCODER=sentence-transformers/all-MiniLM-L6-v2

# Set to true to use local models instead of external APIs
LOCAL_DEPLOYMENT=false

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

#### Local Deployment

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

#### Cloud Deployment

The application can also be deployed with the frontend and backend hosted separately. Note that using a backend cloud deployment requires a separate database cloud deployment too. 

An instance has already been deployed for reference.

Frontend (Vercel)

```text
https://project-onion-six.vercel.app
```

Backend (Microsoft Azure Container Instance)

```text
http://project-onion.gkbmdwg9dkdbcedm.malaysiawest.azurecontainer.io:8000
```

Database (Supabase)

```text
https://supabase.com/dashboard/project/avecaybyplxugvvfooyq
```

When deploying to separate hosts, ensure the following:

- The frontend `vercel.json` rewrite rules point to the backend's public URL
- The backend FastAPI application has CORS configured to allow requests from the Vercel domain
- All required environment variables are configured in the respective platform's settings rather than a local `.env` file

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

When deploying to cloud separately, remove the proxy field and configure `vercel.json` rewrite rules to forward API requests to the hosted backend URL instead.

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

**API proxying**

When running locally with `npm start`, API requests are proxied to the backend via the `proxy` field in `package.json`. This means all relative API calls such as `/user/login` and `/upload/get_topics` are forwarded automatically without any changes to the frontend code.

When running on Vercel, the `proxy` field is ignored. API forwarding is instead handled by `vercel.json` rewrite rules, which map each API route prefix to the deployed backend URL. The frontend code itself does not change between environments since all calls use relative paths.
