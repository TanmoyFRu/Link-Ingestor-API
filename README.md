<!-- Improved compatibility of back to top link -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/TanmoyFRu/Link-Ingestor-API">
    <img src="https://img.icons8.com/ios-filled/100/000000/link.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Link Ingestor</h3>

  <p align="center">
    An autonomous system for ingesting web pages and extracting all critical links with their backlinks.
    <br />
    <a href="https://github.com/TanmoyFRu/Link-Ingestor-API"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/TanmoyFRu/Link-Ingestor-API">View Demo</a>
    &middot;
    <a href="https://github.com/TanmoyFRu/Link-Ingestor-API/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/TanmoyFRu/Link-Ingestor-API/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#features">Features</a></li>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#quick-start">Quick Start</a></li>
    <li><a href="#usage-examples">Usage Examples</a></li>
    <li><a href="#configuration">Configuration</a></li>
    <li><a href="#api-endpoints">API Endpoints</a></li>
    <li><a href="#data-models">Data Models</a></li>
    <li><a href="#performance-considerations">Performance Considerations</a></li>
    <li><a href="#monitoring">Monitoring</a></li>
    <li><a href="#development">Development</a></li>
    <li><a href="#deployment">Deployment</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#support">Support</a></li>
  </ol>
</details>

## About The Project

**Link Ingestor** is designed to efficiently gather connected and important URLs related to any input page while maintaining performance through intelligent backlink limiting.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Features

- **Autonomous Link Extraction**: Automatically fetches web pages and extracts all links  
- **Backlink Discovery**: Finds pages linking to each extracted link (limited to 10 per link)  
- **Multiple Search Providers**: Bing Search API + in-domain crawling fallback  
- **Performance Optimized**: Configurable limits and intelligent deduplication  
- **Async Processing**: FastAPI with background task support  
- **Monitoring**: Prometheus metrics and structured logging  
- **Containerized**: Docker Compose setup with PostgreSQL, Redis, and monitoring  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Architecture

```mermaid
flowchart LR
    A[FastAPI App] --> B[Redis]
    A --> C[PostgreSQL]
    A --> D[Celery Worker]
    D --> B
    D --> C
    A --> E[Prometheus]
    E --> F[Grafana]

    subgraph FastAPI App
        A1[HTTP Endpoints]
        A2[Link Parsing]
        A3[Backlink Discovery]
    end

    subgraph Celery Worker
        D1[Background Processing]
        D2[Queue Jobs]
    end

    subgraph PostgreSQL
        C1[Links]
        C2[Backlinks]
        C3[Jobs]
    end

    subgraph Redis
        B1[Cache]
        B2[Task Queue]
    end

    subgraph Prometheus
        E1[Metrics]
        E2[Monitoring]
    end

    subgraph Grafana
        F1[Dashboards]
        F2[Visualization]
    end
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/TanmoyFRu/Link-Ingestor-API.git
cd link-ingestor
cp env.example .env
# Edit .env with your configuration
```

### 2. Start with Docker Compose

```bash
docker-compose up -d
```

This will start:
- FastAPI app on http://localhost:8000  
- PostgreSQL on port 5432  
- Redis on port 6379  
- Prometheus on port 9090  
- Grafana on port 3000 (admin/admin)

### 3. API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage Examples

### Basic Link Ingestion

```bash
curl -X POST "http://localhost:8000/v1/ingest/"   -H "Content-Type: application/json"   -d '{
    "url": "https://www.amazon.com/dp/B08N5WRWNW",
    "include_backlinks": true,
    "max_backlinks_per_link": 10
  }'
```

### Get Ingestion Summary

```bash
curl "http://localhost:8000/v1/ingest/summary?url=https://www.amazon.com/dp/B08N5WRWNW"
```

### Async Ingestion

```bash
curl -X POST "http://localhost:8000/v1/ingest/async"   -H "Content-Type: application/json"   -d '{
    "url": "https://www.amazon.com/dp/B08N5WRWNW"
  }'
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost/link_ingestor` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `BING_API_KEY` | Bing Search API key | `None` |
| `MAX_BACKLINKS_PER_LINK` | Maximum backlinks per link | `10` |
| `HTTP_TIMEOUT` | HTTP request timeout (seconds) | `30` |

### Backlink Providers

1. **Bing Search API**: Primary provider using Microsoft's search API  
2. **In-Domain Crawler**: Fallback provider that crawls the same domain  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## API Endpoints

### POST /v1/ingest/
Ingest a web page and extract all links with backlinks.

**Request Body:**
```json
{
  "url": "https://example.com",
  "include_backlinks": true,
  "max_backlinks_per_link": 10
}
```

**Response:**
```json
{
  "job_id": "job_123",
  "source_url": "https://example.com",
  "status": "completed",
  "total_links_found": 25,
  "total_backlinks_found": 150,
  "links": [...],
  "backlinks": [...]
}
```

### GET /v1/ingest/summary  
Get a summary of what would be ingested without full processing.  

### POST /v1/ingest/async  
Start an asynchronous ingestion job.  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Data Models

### Link
- `url`: The extracted link URL  
- `title`: Page title (if available)  
- `description`: Page description (if available)  
- `source_url`: URL where this link was found  
- `domain`: Domain of the link  
- `is_external`: Whether the link is external to the source domain  
- `link_text`: Anchor text or link description  

### Backlink
- `backlink_url`: URL of the page linking to the target  
- `backlink_title`: Title of the backlinking page  
- `backlink_domain`: Domain of the backlinking page  
- `anchor_text`: Text used in the link  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Performance Considerations

- **Backlink Limiting**: Default limit of 10 backlinks per link prevents overwhelming  
- **Deduplication**: Automatic removal of duplicate links and backlinks  
- **Async Processing**: Background task support for long-running operations  
- **Caching**: Redis-based caching for frequently accessed data  
- **Rate Limiting**: Configurable rate limiting to respect target sites  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Monitoring

### Prometheus Metrics
- HTTP request counts and durations  
- Link extraction success/failure rates  
- Backlink discovery metrics  
- Database query performance  

### Grafana Dashboards
- Real-time system health  
- Link ingestion throughput  
- Error rates and trends  
- Resource utilization  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Development

### Local Development

```bash
# Install dependencies
pip install -e .

# Run FastAPI app
uvicorn app.main:app --reload

# Run Celery worker
celery -A app.worker.tasks worker --loglevel=info
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/unit/test_ingest_service.py
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy app/
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Deployment

### Production Considerations

1. **Environment Variables**: Secure all sensitive configuration  
2. **Database**: Use managed PostgreSQL service  
3. **Redis**: Use managed Redis service  
4. **Monitoring**: Set up alerting for critical metrics  
5. **Rate Limiting**: Configure appropriate limits for your use case  
6. **SSL/TLS**: Enable HTTPS in production  

### Scaling

- **Horizontal Scaling**: Multiple API instances behind a load balancer  
- **Worker Scaling**: Multiple Celery workers for background processing  
- **Database**: Read replicas for read-heavy workloads  
- **Caching**: Redis clustering for high availability  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

Contributions are what make the open source community an amazing place to learn, inspire, and create.  
Any contributions you make are **greatly appreciated**.

1. Fork the Project  
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)  
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)  
4. Push to the Branch (`git push origin feature/AmazingFeature`)  
5. Open a Pull Request  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Support

For questions and support:  
- Create an issue in the repository  
- Check the API documentation at `/docs`  
- Review the logs for debugging information  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/TanmoyFRu/Link-Ingestor-API.svg?style=for-the-badge
[contributors-url]: https://github.com/TanmoyFRu/Link-Ingestor-API/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/TanmoyFRu/Link-Ingestor-API.svg?style=for-the-badge
[forks-url]: https://github.com/TanmoyFRu/Link-Ingestor-API/network/members
[stars-shield]: https://img.shields.io/github/stars/TanmoyFRu/Link-Ingestor-API.svg?style=for-the-badge
[stars-url]: https://github.com/TanmoyFRu/Link-Ingestor-API/stargazers
[issues-shield]: https://img.shields.io/github/issues/TanmoyFRu/Link-Ingestor-API.svg?style=for-the-badge
[issues-url]: https://github.com/TanmoyFRu/Link-Ingestor-API/issues
[license-shield]: https://img.shields.io/github/license/TanmoyFRu/Link-Ingestor-API.svg?style=for-the-badge
[license-url]: https://github.com/TanmoyFRu/Link-Ingestor-API/blob/master/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/
