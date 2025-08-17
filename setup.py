from setuptools import setup, find_packages

setup(
    name="link-ingestor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.0.0",
        "httpx>=0.25.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "celery>=5.3.0",
        "redis>=5.0.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.12.0",
        "asyncpg>=0.29.0",
        "structlog>=23.2.0",
        "prometheus-client>=0.19.0",
        "python-multipart>=0.0.6",
    ],
    python_requires=">=3.9",
)