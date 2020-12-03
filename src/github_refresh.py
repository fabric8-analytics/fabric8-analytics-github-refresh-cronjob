#!/usr/bin/env python3

"""Script for refreshing GitHub data of ingested packages."""

import os
import logging
from datetime import datetime, timedelta
import botocore
import boto3
import json
from requests_futures.sessions import FuturesSession

_REGION = os.environ.get('AWS_S3_REGION', 'us-east-1')
_ACCESS_KEY_ID = os.environ.get('AWS_S3_ACCESS_KEY_ID', None)
_ACCESS_KEY = os.environ.get('AWS_S3_SECRET_ACCESS_KEY', None)
_PREFIX = os.environ.get('DEPLOYMENT_PREFIX', 'dev')
_BUCKET = os.environ.get('REPORT_BUCKET_NAME', None)
_TIME_DELTA = int(os.environ.get('REPORT_TIME_DELTA', 0))
_DRY_RUN = int(os.environ.get('DRY_RUN', 0))
_APP_SECRET_KEY = os.getenv('APP_SECRET_KEY', 'not-set')

_INGESTION_API_URL = "http://{host}:{port}/{endpoint}".format(
    host=os.environ.get("INGESTION_SERVICE_HOST", "bayesian-jobs"),
    port=os.environ.get("INGESTION_SERVICE_PORT", "34000"),
    endpoint='ingestions/epv-selective')

TASK_NAMES = [
    'github_details',
    'PackageFinalizeTask',
    'PackageResultCollector',
    'PackageGraphImporterTask'
]

GO_TASK_NAMES = [
    "NewGithubDetails",
    "NewPackageAnalysisGraphImporterTask"
]

session = boto3.session.Session(
    aws_access_key_id=_ACCESS_KEY_ID,
    aws_secret_access_key=_ACCESS_KEY,
    region_name=_REGION)
s3_resource = session.resource('s3', config=botocore.client.Config(signature_version='s3v4'))
eco_list = ['npm', 'maven', 'pypi', 'golang']
logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)
_session = FuturesSession()


def retrieve_dict(object_key):
    """Retrieve a dictionary stored as JSON from S3."""
    logger.info("Reading the data from S3 bucket for {}".format(object_key))
    data = retrieve_blob(object_key)
    if data:
        return json.loads(data.decode())
    else:
        return None


def retrieve_blob(object_key):
    """Retrieve remote object content."""
    try:
        data = s3_resource.Object(_BUCKET, object_key).get()['Body'].read()
    except Exception as e:
        logger.error("Exception while trying to fetch from s3 {}".format(str(e)))
        return None
    return data


def get_epv_list():
    """Fetch the epvs from the daily stack report."""
    epv_list = {
        "maven": [],
        "pypi": [],
        "npm": [],
        "golang": []
    }
    if not all([_ACCESS_KEY_ID, _ACCESS_KEY, _REGION, _PREFIX, _BUCKET]):
        logger.info("AWS credentials or S3 configuration was "
                    "not provided correctly. Please set the AWS_S3_REGION, "
                    "AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY, REPORT_BUCKET_NAME "
                    "and DEPLOYMENT_PREFIX correctly.")
        return epv_list
    cur_date = datetime.today()
    yest_date = (cur_date - timedelta(days=_TIME_DELTA)).strftime("%Y-%m-%d")

    logger.info("Fetching venus V2 stack report for the date {}".format(yest_date))
    v2_stack_json = retrieve_dict("v2/daily/" + yest_date + ".json")
    if v2_stack_json:
        for eco in eco_list:
            dep_list = v2_stack_json.get('stacks_summary', {}).get(eco, {}) \
                .get('unique_dependencies_with_frequency', {})
            if bool(dep_list):
                for k in dep_list:
                    name = k.split(" ")[0]
                    epv_list[eco].append(name)
            else:
                logger.info("No deps found in the report for the ecosystem {}".format(eco))
    logger.info("The EPVs for GH refresh --> {}".format(epv_list))
    return epv_list


def schedule_gh_refresh(epv_list):
    """Schedule GH refresh job to update stats."""
    for eco in eco_list:
        # Prepare payload for Ingestion API
        payload = {
            "ecosystem": eco,
            "packages": [],
            "flow_name": "bayesianPackageFlow",
            "task_names": TASK_NAMES,
            "follow_subflows": True
        }

        # Update flow name and task names for Golang.
        if eco == 'golang':
            payload["flow_name"] = "newPackageAnalysisFlow"
            payload["task_names"] = GO_TASK_NAMES

        for pkg in epv_list[eco]:
            payload['packages'].append({'package': pkg})

        if not _DRY_RUN and payload['packages']:
            _session.post(url=_INGESTION_API_URL,
                          json=payload,
                          headers={'auth_token': _APP_SECRET_KEY})
            logger.info("Flow is initiated for payload: {}".format(payload))
        else:
            logger.info("DRY RUN MODE ON..Flow not initiated.")
    return True


def run():
    """Run different methods for GH refresh job."""
    logger.info("-------------------------------------------------------------------------")
    logger.info("Starting GH refresh Cron Job on {}".format(datetime.today()))
    epvs = get_epv_list()
    schedule_gh_refresh(epvs)
    logger.info("Finished GH refresh Cron Job on {}".format(datetime.today()))
    logger.info("-------------------------------------------------------------------------")
    return "success"


if __name__ == '__main__':
    run()
