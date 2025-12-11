"""Crawlers module"""
from .crawler_pool import crawler_pool, CrawlerPool
from .wipo_crawler import WIPOCrawler
from .google_patents import google_patents_client, GooglePatentsClient
from .inpi_client import inpi_client, INPIClient

__all__ = [
    "crawler_pool",
    "CrawlerPool",
    "WIPOCrawler",
    "google_patents_client",
    "GooglePatentsClient",
    "inpi_client",
    "INPIClient",
]
