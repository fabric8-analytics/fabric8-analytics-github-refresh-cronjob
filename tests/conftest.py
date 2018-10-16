"""Test fixtures."""

import pytest
from f8a_worker.models import Package, Ecosystem, Upstream


@pytest.fixture
def db_results():
    """Mimic SQLAlchemy query result."""
    ecosystem = Ecosystem()
    ecosystem.name = 'maven'
    package = Package()
    package.ecosystem = ecosystem
    package.name = 'net.iharder:base64'
    upstream = Upstream()
    upstream.url = 'https://github.com/omalley/base64'
    upstream.package = package

    return [upstream]
