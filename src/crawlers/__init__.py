"""Crawlers module"""
from .crawler_pool import crawler_pool, CrawlerPool
from .wipo_crawler import WIPOCrawler
from .google_patents import google_patents_client, GooglePatentsClient
from .google_patents_pool import google_patents_pool, GooglePatentsCrawlerPool
from .inpi_client import inpi_client, INPIClient

__all__ = [
    "crawler_pool",
    "CrawlerPool",
    "WIPOCrawler",
    "google_patents_client",
    "GooglePatentsClient",
    "google_patents_pool",
    "GooglePatentsCrawlerPool",
    "inpi_client",
    "INPIClient",
]
