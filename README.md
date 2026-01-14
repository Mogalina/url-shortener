# URL Shortener Service

A high-performance, scalable URL shortening API built with Python and FastAPI. This service uses Apache Cassandra for persistent storage of URL mappings and Redis for caching and rate limiting. It is designed to be cloud-native, with full support for Docker and Kubernetes deployments.

## Features

* **URL Shortening**: Generate unique, short aliases for long URLs.
* **Custom TTL**: Set a time-to-live (expiration) for short links (default: 30 days).
* **Redirection**: Fast redirection to original URLs using HTTP 307.
* **Caching**: High-speed lookups using Redis to minimize database hits.
* **Rate Limiting**: Built-in protection against abuse (limit: 10 requests per minute per IP).
* **Cleanup Service**: Background worker that automatically removes expired URLs.
* **End-to-End Load Balancing**: Implements load balancing at the reverse proxy, cache, and database layers.
* **Scalable Architecture**: Stateless API design suitable for horizontal scaling.
* **Containerization**: Fully Dockerized with Docker Compose support.
* **Kubernetes Ready**: Includes manifests for deployment to K8s clusters.

## Technology Stack

* **Language**: Python 3.12
* **Framework**: FastAPI
* **Database**: Apache Cassandra (4.1)
* **Cache**: Redis (7.0)
* **Load Balancer**: Nginx
* **Server**: Uvicorn
* **Containerization**: Docker, Docker Compose

## Load Balancing Strategy

The service implements a three-tier load balancing strategy to ensure high availability and performance:

1. **Client to Application (Nginx)**: An Nginx reverse proxy sits in front of the application, distributing incoming HTTP requests across multiple stateless API containers using a round-robin approach.
2. **Application to Cache (Redis Cluster)**: The application automatically detects if multiple Redis hosts are configured and switches to a Redis Cluster client, distributing cache keys across nodes to prevent hot spots.
3. **Application to Database (Cassandra)**: The Cassandra driver utilizes `TokenAwarePolicy`, allowing the application to send queries directly to the specific database nodes responsible for the data, reducing latency and coordinator overhead.

## Resource Estimation

Estimations are based on the 8-character Base62 encoding, the schema defined in `app/db/cassandra.py`, and a **Replication Factor (RF) of 3**.

### **Row Size Breakdown**

To calculate the storage per URL, we estimate the raw data plus the overhead Cassandra adds for metadata (timestamps, column mapping) and the secondary index on `expires_at`.

* **Partition Key (`short_code`)**: 8 bytes
* **Long URL (`long_url`)**: ~500 bytes (Average estimate)
* **Timestamps (`created_at`, `expires_at`)**: 16 bytes (8 bytes each)
* **Cassandra Metadata & Overhead**: ~126 bytes
  * *Includes: Per-column timestamps (writetime), column length markers, and the `idx_expires_at` secondary index entry.*
* **Total Size per Row**: **~650 bytes**

### **Storage Capacity Planning**

*Assumptions: 1 Million new URLs/day, RF=3. We assume ~50% compression ratio using Cassandra's default LZ4 algorithm.*

| Time Period | New URLs    | Raw Data Size (1 Node) | Total Disk Usage (RF=3, Uncompressed) | **Total Disk (RF=3, LZ4 Compressed)** |
| :---------- | :---------- | :--------------------- | :------------------------------------ | :------------------------------------ |
| **1 Day**   | 1 Million   | 650 MB                 | 1.95 GB                               | **~0.98 GB**                          |
| **1 Month** | 30 Million  | 19.5 GB                | 58.5 GB                               | **~29.3 GB**                          |
| **1 Year**  | 365 Million | 237 GB                 | 711 GB                                | **~355.5 GB**                         |
| **5 Years** | 1.8 Billion | 1.18 TB                | 3.54 TB                               | **~1.77 TB**                          |

### **ID Namespace Capacity**

* **Unique Short Codes**: 62^8 ≈ **218 Trillion** (2.18 × 10^14) combinations.
* **Lifespan**: At a rate of 1 million new URLs/day, the 8-character namespace will last effectively forever (hundreds of thousands of years) without collisions.

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

| Variable          | Description                          | Default (Docker)        |
| :---------------- | :----------------------------------- | :---------------------- |
| `CASSANDRA_HOSTS` | Hostname(s) of the Cassandra service | `cassandra`             |
| `REDIS_HOST`      | Hostname(s) of the Redis service     | `redis`                 |
| `REDIS_PORT`      | Port for Redis                       | `6379`                  |
| `BASE_URL`        | Public base URL for generated links  | `http://localhost:8000` |
| `KEYSPACE`        | Cassandra keyspace name              | `url_shortener`         |

## Project Structure

* `app/`: Application source code.
  * `api/`: API route definitions and endpoints.
  * `core/`: Configuration, logging, and security (rate limiting).
  * `db/`: Database connection modules (Redis, Cassandra).
  * `services/`: Business logic (shortener, resolver, cleanup).
  * `utils/`: Utility functions (ID generation, time).
* `deploy/`: Deployment configurations.
  * `docker/`: Dockerfile, docker-compose.yml, and nginx.conf.
  * `k8s/`: Kubernetes manifests (ConfigMap, Deployments, Services).
* `docs/`: Design documents and diagrams.
* `scripts/`: Helper running and deployment scripts.
  * `run.sh`: Helper script for Docker Compose execution.
  * `k8s_deploy.sh`: Helper script for Kubernetes deployment.
