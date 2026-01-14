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

*Assumptions: 1 Million new URLs/day (roughly 11 new URLs/second), RF=3. We assume ~50% compression ratio using Cassandra's default LZ4 algorithm.*

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

## Cost Estimation: Self-Hosted (IaaS)

This comparison estimates the cost (***officially registered on 14 January 2026***) of running the following infrastructure on **AWS, GCP, and Azure**:

* **3-node Cassandra cluster**
* **2 API servers**
* **1 Redis node**
* **1 Load Balancer**

### Workload Assumptions

* **Region:** US East (N. Virginia / East US)
* **Database:** 3 Nodes (Cassandra, RF = 3), ~8GB RAM each
* **Application:** 2 Nodes (Stateless API), ~4GB RAM each
* **Cache:** 1 Node (Redis), ~2GB RAM
* **Storage:**  
  * 100GB SSD per DB node (300GB total)  
  * Boot disks included
* **Network:** 1 TB outbound traffic per month

### Executive Summary

| Provider  | Daily Cost | Monthly Cost | Yearly Cost |
|-----------|------------|--------------|-------------|
| **AWS**   | ~$13.13    | ~$394        | ~$4,728     |
| **GCP**   | ~$13.33    | ~$400        | ~$4,800     |
| **Azure** | ~$16.20    | ~$486        | ~$5,832     |

#### Summary

* **AWS** is the most cost-effective option for this setup, mainly due to:
  * Aggressive **gp3 storage pricing**
  * Low-cost **t3 burstable instances**
* **GCP** is a close second:
  * **e2 instances** provide predictable, sustained performance
* **Azure** is more expensive:
  * Uses **D-series enterprise-grade VMs** for databases
  * Costs can be reduced with burstable B-series, but with performance tradeoffs

### Detailed Breakdown

#### AWS (Amazon Web Services)

**Region:** `us-east-1` (N. Virginia)

| Resource           | Type / Spec                 | Unit Price       | Monthly |
|--------------------|-----------------------------|------------------|---------|
| DB Compute (x3)    | t3.large (2 vCPU, 8GB RAM)  | $0.0832/hr       | $182.22 |
| App Compute (x2)   | t3.medium (2 vCPU, 4GB RAM) | $0.0416/hr       | $60.74  |
| Redis Compute (x1) | t3.small (2 vCPU, 2GB RAM)  | $0.0208/hr       | $15.19  |
| DB Storage         | EBS gp3 (300GB)             | $0.08/GB         | $24.00  |
| Boot Storage       | EBS gp3 (120GB)             | $0.08/GB         | $9.60   |
| Load Balancer      | Application Load Balancer   | $0.0225/hr + LCU | ~$21.43 |
| Network            | Data Transfer Out (1 TB)    | $0.09/GB         | $81.00  |

**Total:** **~$394.18 / month**

> **Note:**  
> t3 instances are burstable. If DB CPU usage is constantly high, you may incur unlimited-mode charges.  
> For consistent performance, upgrade DB nodes to `m6i.large` (~$0.096/hr).

---

#### GCP (Google Cloud Platform)

**Region:** `us-central1` (Iowa)

| Resource           | Type / Spec                        | Unit Price | Monthly |
|--------------------|------------------------------------|------------|---------|
| DB Compute (x3)    | e2-standard-2 (2 vCPU, 8GB RAM)    | $0.067/hr  | $146.76 |
| App Compute (x2)   | e2-medium (2 vCPU, 4GB RAM)        | $0.0335/hr | $50.00  |
| Redis Compute (x1) | e2-small (2 vCPU, 2GB RAM)         | $0.019/hr  | $14.00  |
| DB Storage         | Balanced Persistent Disk (300GB)   | $0.10/GB   | $30.00  |
| Boot Storage       | Balanced Persistent Disk (120GB)   | $0.10/GB   | $12.00  |
| Load Balancer      | Cloud Load Balancing               | $0.025/hr  | ~$26.25 |
| Network            | Premium Tier Egress (1 TB)         | $0.12/GB   | $120.00 |

**Total:** **~$399.01 / month**

> **Note:**  
> GCP e2 instances offer predictable performance without CPU credit models, making cost behavior easier to reason about.

---

#### Microsoft Azure

**Region:** `east-us`

| Resource           | Type / Spec                     | Unit Price        | Monthly |
|--------------------|---------------------------------|-------------------|---------|
| DB Compute (x3)    | D2s v5 (2 vCPU, 8GB RAM)        | $0.096/hr         | $210.24 |
| App Compute (x2)   | B2s (2 vCPU, 4GB RAM)           | $0.0496/hr        | $72.42  |
| Redis Compute (x1) | B1ms (1 vCPU, 2GB RAM)          | $0.0207/hr        | $15.11  |
| DB Storage         | Managed Disk P10 (128GB × 3)    | $17.92/disk       | $53.76  |
| Boot Storage       | Standard SSD E4 (32GB × 6)      | ~$2.40/disk       | $14.40  |
| Load Balancer      | Standard Load Balancer          | $0.025/hr         | ~$28.00 |
| Network            | Data Transfer Out (1 TB)        | $0.0875/GB        | $87.50  |

**Total:** **~$481.43 / month**

> **Note:**  
> D2s v5 was selected for database stability.  
> Switching DB nodes to `B2ms` could save ~$60/month but risks latency spikes during heavy writes.

---

### Savings Opportunities (All Clouds)

#### Reserved Instances (1-Year / 3-Year)

* 1-year commitment: **30–40% savings**
* Example:
  * AWS `t3.large`: ~$60/mo → ~$36/mo per node

#### Spot Instances

* **Do NOT use for databases**
* Safe for:
  * API servers
  * Cleanup workers
* Savings: **60–80%**
* Requires interruption handling

#### Managed Services

Instead of self-hosting:

* Cassandra → **Amazon Keyspaces**
* Redis → **AWS ElastiCache / GCP Memorystore**

While unit pricing is higher, you often save significantly on:

* Maintenance
* Upgrades
* On-call engineering time

> **Operational cost is usually higher than infrastructure cost in production systems.**

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
