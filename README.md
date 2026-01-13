# URL Shortener Service

A high-performance, scalable URL shortening API built with Python and FastAPI. This service uses Apache Cassandra for persistent storage of URL mappings and Redis for caching and rate limiting. It is designed to be cloud-native, with full support for Docker and Kubernetes deployments.

## Features

* **URL Shortening**: Generate unique, short aliases for long URLs.
* **Custom TTL**: Set a time-to-live (expiration) for short links (default: 30 days).
* **Redirection**: Fast redirection to original URLs using HTTP 307.
* **Caching**: High-speed lookups using Redis to minimize database hits.
* **Rate Limiting**: Built-in protection against abuse (limit: 10 requests per minute per IP).
* **Cleanup Service**: Background worker that automatically removes expired URLs.
* **Scalable Architecture**: Stateless API design suitable for horizontal scaling.
* **Containerization**: Fully Dockerized with Docker Compose support.
* **Kubernetes Ready**: Includes manifests for deployment to K8s clusters.

## Technology Stack

* **Language**: Python 3.12
* **Framework**: FastAPI
* **Database**: Apache Cassandra (4.1)
* **Cache**: Redis (7.0)
* **Server**: Uvicorn
* **Containerization**: Docker, Docker Compose

## Prerequisites

* Docker and Docker Compose
* (Optional) Kubernetes cluster (Minikube, Kind, or cloud provider) and kubectl

## Quick Start (Docker Compose)

The easiest way to run the application locally is using the provided helper script.

1. **Run the application**:
    This script will handle environment configuration, build the containers, and start the services.

    ```bash
    ./run.sh
    ```

2. **Access the Service**:
    * **API Root**: `http://localhost:8000`
    * **Interactive Documentation (Swagger)**: `http://localhost:8000/docs`
    * **Health Check**: `http://localhost:8000/docs#/default/root_url_get`

3. **Stop the application**:

    ```bash
    docker compose -f deploy/docker/docker-compose.yml down
    ```

## Deployment (Kubernetes)

To deploy the application to a Kubernetes cluster, use the deployment script.

1. **Deploy to Cluster**:

    ```bash
    ./k8s_deploy.sh
    ```

    This script performs the following:
    * Builds the Docker image locally.
    * Loads the image into your cluster (Minikube/Kind).
    * Applies all configuration manifests (ConfigMap, Redis, Cassandra, API, Cleanup).
    * Sets up port forwarding to `localhost:8000`.

## API Usage

### Create a Short URL

**Endpoint**: `POST /api/v1/shorten`

**Parameters**:

* `long_url` (string, required): The URL to shorten.
* `ttl_days` (integer, optional): Expiration time in days (default: 30).

**Example Request**:

```bash
curl -X POST "http://localhost:8000/api/v1/shorten?long_url=[https://www.google.com](https://www.google.com)&ttl_days=7"
```

**Response**:

```json
{
  "short_url": "/aBcD1234"
}
```

### Redirect to Original URL

**Endpoint**: `GET /api/v1/{code}`

**Example Request**:

```bash
curl -v http://localhost:8000/api/v1/aBcD1234
```

**Response**:

```bash
HTTP 307 Temporary Redirect to the original URL.
```

## Configuration

The application is configured using environment variables. A `.env` file is automatically created from `.env.example` when using `run.sh`.

| Variable          | Description                         | Default (Docker)        |
| :---------------- | :---------------------------------- | :---------------------- |
| `CASSANDRA_HOSTS` | Hostname of the Cassandra service   | `cassandra`             |
| `REDIS_HOST`      | Hostname of the Redis service       | `redis`                 |
| `REDIS_PORT`      | Port for Redis                      | `6379`                  |
| `BASE_URL`        | Public base URL for generated links | `http://localhost:8000` |
| `KEYSPACE`        | Cassandra keyspace name             | `url_shortener`         |

## Project Structure

* `app/`: Application source code.
  * `api/`: API route definitions and endpoints.
  * `core/`: Configuration, logging, and security (rate limiting).
  * `db/`: Database connection modules (Redis, Cassandra).
  * `services/`: Business logic (shortener, resolver, cleanup).
  * `utils/`: Utility functions (ID generation, time).
* `deploy/`: Deployment configurations.
  * `docker/`: Dockerfile and docker-compose.yml.
  * `k8s/`: Kubernetes manifests (ConfigMap, Deployments, Services).
* `docs/`: Design documents and diagrams.
* `scripts/`: Helper running scripts
  * `run.sh`: Helper script for Docker Compose execution.
  * `k8s_deploy.sh`: Helper script for Kubernetes deployment.
