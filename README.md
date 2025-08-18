# Link Ingestor

An autonomous system for ingesting web pages and extracting all critical links with their backlinks. The system is designed to efficiently gather connected and important URLs related to any input page while maintaining performance through intelligent backlink limiting.

## Features

- **Autonomous Link Extraction**: Automatically fetches web pages and extracts all links
- **Backlink Discovery**: Finds pages linking to each extracted link (limited to 10 per link)
- **Multiple Search Providers**: Bing Search API + in-domain crawling fallback
- **Performance Optimized**: Configurable limits and intelligent deduplication
- **Async Processing**: FastAPI with background task support
- **Monitoring**: Prometheus metrics and structured logging
- **Containerized**: Docker Compose setup with PostgreSQL, Redis, and monitoring
1
## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Celery Worker  │    │   PostgreSQL    │
│                 │    │                 │    │                 │
│ • HTTP Endpoints│    │ • Background    │    │ • Links         │
│ • Link Parsing  │    │   Processing    │    │ • Backlinks     │
│ • Backlink      │    │ • Queue Jobs    │    │ • Jobs          │
│   Discovery     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Redis       │    │   Prometheus    │    │     Grafana     │
│                 │    │                 │    │                 │
│ • Cache         │    │ • Metrics       │    │ • Dashboards    │
│ • Task Queue    │    │ • Monitoring    │    │ • Visualization │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
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

## Usage Examples

### Basic Link Ingestion

```bash
curl -X POST "http://localhost:8000/v1/ingest/" \
  -H "Content-Type: application/json" \
  -d '{
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
curl -X POST "http://localhost:8000/v1/ingest/async" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.amazon.com/dp/B08N5WRWNW"
  }'
```

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

## Performance Considerations

- **Backlink Limiting**: Default limit of 10 backlinks per link prevents overwhelming
- **Deduplication**: Automatic removal of duplicate links and backlinks
- **Async Processing**: Background task support for long-running operations
- **Caching**: Redis-based caching for frequently accessed data
- **Rate Limiting**: Configurable rate limiting to respect target sites

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for debugging information



