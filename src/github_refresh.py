#!/usr/bin/env python3

"""Script for refreshing GitHub data of ingested packages."""

import os
import logging
from selinon import run_flow_selective
from datetime import datetime, timedelta
from f8a_worker.setup_celery import init_celery, init_selinon

import botocore
import boto3
import json


_REGION = os.environ.get('AWS_S3_REGION', 'us-east-1')
_ACCESS_KEY_ID = os.environ.get('AWS_S3_ACCESS_KEY_ID', None)
_ACCESS_KEY = os.environ.get('AWS_S3_SECRET_ACCESS_KEY', None)
_PREFIX = os.environ.get('DEPLOYMENT_PREFIX', 'dev')
_BUCKET = os.environ.get('REPORT_BUCKET_NAME', None)

TASK_NAMES = [
    'github_details',
    'PackageFinalizeTask',
    'PackageResultCollector',
    'PackageGraphImporterTask'
]

session = boto3.session.Session(
    aws_access_key_id=_ACCESS_KEY_ID,
    aws_secret_access_key=_ACCESS_KEY,
    region_name=_REGION)
s3_resource = session.resource('s3', config=botocore.client.Config(signature_version='s3v4'))
eco_list = ['npm', 'maven', 'pypi']
logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def retrieve_dict(object_key):
    """Retrieve a dictionary stored as JSON from S3."""
    return json.loads(retrieve_blob(object_key).decode())


def retrieve_blob(object_key):
    """Retrieve remote object content."""
    return s3_resource.Object(_BUCKET, object_key).get()['Body'].read()


def get_epv_list():
    """Fetch the epvs from the daily stack report."""
    epv_list = []
    if not all([_ACCESS_KEY_ID, _ACCESS_KEY, _REGION, _PREFIX, _BUCKET]):
        logger.info("AWS credentials or S3 configuration was "
                    "not provided correctly. Please set the AWS_S3_REGION, "
                    "AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY, REPORT_BUCKET_NAME "
                    "and DEPLOYMENT_PREFIX correctly.")
        return epv_list
    cur_date = datetime.today()
    yest_date = (cur_date - timedelta(days=1)).strftime("%Y-%m-%d")
    stack_json = retrieve_dict(yest_date + ".json")
    for eco in eco_list:
        dep_list = stack_json.get('stacks_summary', {}).get(eco, {}) \
            .get('unique_dependencies_with_frequency', {})
        if bool(dep_list):
            for k in dep_list:
                name = k.split(" ")[0]
                epv_list.append({
                    "ecosystem": eco,
                    "name": name
                })
        else:
            logger.info("No deps found in the report for the ecosystem {}".format(eco))
    logger.info("The EPVs for GH refresh --> {}".format(epv_list))
    logger.info("Total number of EPVs {}".format(len(epv_list)))
    return epv_list


def schedule_gh_refresh(epv_list):
    """Schedule GH refresh job to update stats."""
    for node in epv_list:
        node['force'] = True
        logger.info("Starting bayesianPackageFlow for {e} {n}".format(e=node['ecosystem'], n=node['name']))
        refresh(node)
    return True


def refresh(node_args):
    """Schedule refresh of GitHub data for given package."""
    run_flow_selective('bayesianPackageFlow', TASK_NAMES, node_args, True, False)


def run():
    """Run different methods for GH refresh job."""
    init_celery()
    init_selinon()
    epvs = get_epv_list()
    schedule_gh_refresh(epvs)
    return "success"


if __name__ == '__main__':
    run()
