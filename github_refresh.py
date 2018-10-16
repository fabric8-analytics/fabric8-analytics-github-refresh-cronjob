#!/usr/bin/env python3

"""Script for refreshing GitHub data of ingested packages."""

import os
import math
import logging
from selinon import run_flow_selective
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from f8a_worker.models import Upstream, Package, Ecosystem
from f8a_worker.setup_celery import init_selinon


logger = logging.getLogger('github_refresh')


CONN_STR = "postgresql://{user}:{password}@{host}:{port}/{db}".format(
    host=os.environ.get('POSTGRESQL_HOST', 'localhost'),
    port=os.environ.get('POSTGRESQL_PORT', '6432'),
    db=os.environ.get('POSTGRESQL_DATABASE', 'coreapi'),
    user=os.environ.get('POSTGRESQL_USER', 'coreapi'),
    password=os.environ.get('POSTGRESQL_PASSWORD', 'coreapi')
)

REFRESH_INTERVAL = int(os.environ.get('REFRESH_INTERVAL', 14))

TASK_NAMES = [
        'github_details',
        'PackageFinalizeTask',
        'PackageResultCollector',
        'PackageGraphImporterTask'
    ]


def refresh(ecosystem, package, url):
    """Schedule refresh of GitHub data for given package."""
    logger.info('Refreshing GitHub data for {e}/{p}: {u}'.format(
        e=ecosystem, p=package, u=url)
    )

    node_args = {
        'ecosystem': ecosystem,
        'package': package,
        'force': True
    }

    if not is_dry_run():
        run_flow_selective('bayesianPackageFlow', TASK_NAMES, node_args, False, False)


def run(db):
    """Run the script."""
    limit = get_limit(db)
    if limit:
        results = _get_outdated(db, limit)
        logger.info('Refreshing GitHub data for {n} projects'.format(n=len(results)))
        for result in results:
            refresh(result.package.ecosystem.name, result.package.name, result.url)


def get_expiration_date():
    """Get expiration date after which GitHub data are considered outdated."""
    interval = REFRESH_INTERVAL
    return datetime.utcnow() - timedelta(days=interval)


def get_limit(db):
    """Get limit how many GitHub statistics can be updated at once."""
    return math.ceil(_get_count(db) / REFRESH_INTERVAL / 2)


def is_dry_run():
    """Return True if this is a dry run."""
    return os.environ.get('DRY_RUN', 'false').lower() in ('1', 'yes', 'true')


def _get_count(db):
    """Count how many GitHub data are outdated."""
    return db.query(Upstream).filter(Upstream.updated_at < get_expiration_date())\
        .filter(Upstream.url.like('%github.com%'), Upstream.deactivated_at == None).count()


def _get_outdated(db, limit):
    """Get EPs with outdated GitHub data."""
    return db.query(Upstream).join(Package).join(Ecosystem).filter(
        Upstream.url.like('%github.com%'), Upstream.deactivated_at == None).limit(limit).all()


if __name__ == '__main__':
    init_selinon()
    run(sessionmaker(bind=create_engine(CONN_STR))())
