import os
import logging
import json
import sys
import boto3
import argparse
from snyk import SnykClient

FORMAT = '%(message)s'
logging.basicConfig(format=FORMAT, stream=sys.stdout, level=logging.INFO)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("boto3").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

projects = ["myproject", "myproject2"]

"""
Adds SNYK monitoring
:param repo_name:
:param env:
:return Bool:
"""
def snyk_monitor(repo_name, bb_workspace, snyk_token, snyk_org, snyk_intid):
    try:
        snyk_client = SnykClient(snyk_token, tries=4, delay=1, backoff=2)
        org = snyk_client.organizations.get(snyk_org)
    except Exception as e:
        logging.error(f'Error montioring repo in SNYK: {e}')
        return False

    project_name = bb_workspace + "/" + repo_name

    for proj in org.projects.all():
        logger.debug(f"Project: {proj.name}")
        if project_name in proj.name:
            logger.info(f"Project {project_name} already exists in SNYK")
            return False

    logger.info(f"Project {project_name} does not exist, adding to SNYK")
    try:
        integration = org.integrations.get(snyk_intid)
        logger.debug(f"intergration: {integration} ")
    except Exception as e:
        logging.error(f'Error trying to retrieve integration: {e}')
        return False
    try:
        job = integration.import_git(dev_org, repo_name)
        logger.debug(f"Result from SNYK: {job}")
    except Exception as e:
        logging.error(f'Error montioring repo in SNYK: {e}')
        return False

    return job

def lambda_handler(event, context):
    """
    Handles lambda events
    :param event:
    :param context:
    :return int:
    """
    if 'DEBUG' in os.environ:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    if 'BB_WORKSPACE' in os.environ:
        bb_workspace = os.environ['BB_WORKSPACE']
    else:
        logger.error(f"No bitbucket org set")
        return 1
    if 'BB_PROJECTS' in os.environ:
        snyk_int_id = os.environ['SNYK_INT_ID']
    else:
        logger.error(f"No SNYK Intergration ID set")
        return 1
    if 'SNYK_TOKEN' in os.environ:
        snyk_token = os.environ['SNYK_TOKEN']
    else:
        logger.error(f"No SNYK token set")
        return 1
    if 'SNYK_ORG' in os.environ:
        snyk_org = os.environ['SNYK_ORG']
    else:
        logger.error(f"No SNYK org set")
        return 1
    if 'SNYK_INT_ID' in os.environ:
        snyk_int_id = os.environ['SNYK_INT_ID']
    else:
        logger.error(f"No SNYK Intergration ID set")
        return 1

    try:
        body = json.loads(event['body'])
        new_project = body['repository']['project']['name']
        new_repo = body['repository']['full_name'].split('/')[1]
    except Exception as e:
        logger.error(f"Could not read event body: {str(e)}")
        return 1

    logger.debug(f"Project: {new_project} Repo: {new_repo}")

    if new_project in projects:
        logger.info(f"Bitbucket Repo is in monitored project: {new_project} ")
        if snyk_monitor(new_repo, bb_workspace):
            logger.info (f"Monitoring {bb_org}/{new_repo}")
            return 0
        else:
            logger.info (f"Could not monitor {bb_org}/{new_repo}")
            return 0
    logger.info(f"{new_repo} is not in a project to be monitored by SNYK")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='bb-snyk-peac')
    parser.add_argument("--verbose", help="Turn on DEBUG logging", action='store_true', required=False)
    parser.add_argument("--bb_workspace", help="Turn on DEBUG logging", action='store_true', required=False)
    parser.add_argument("--snyk_org", help="Turn on DEBUG logging", action='store_true', required=False)
    parser.add_argument("--snyk_token", help="Turn on DEBUG logging", action='store_true', required=False)
    parser.add_argument("--snyk_int_id", help="Turn on DEBUG logging", action='store_true', required=False)
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.DEBUG)

    if args.bb_workspace:
        bb_workspace = args.verbose
    else:
        logger.error(f"No bitbucket org set")
        sys.exit(1)
    if args.snyk_token:
        snyk_token = os.environ['SNYK_TOKEN']
    else:
        logger.error(f"No SNYK token set")
        sys.exit(1)
    if args.snyk_org:
        snyk_org = os.environ['SNYK_ORG']
    else:
        logger.error(f"No SNYK org set")
        sys.exit(1)
    if args.snyk_int_id:
        snyk_int_id = os.environ['SNYK_INT_ID']
    else:
        logger.error(f"No SNYK Intergration ID set")
        sys.exit(1)

    with open('test.json') as json_file:
        data = json.load(json_file)

    logger.debug(f"Body: {data['body']}")
    new_repo = str(data["body"]["repository"]["full_name"].split('/')[1])
    for project in projects:
        if data["body"]["repository"]['project']["name"] == project:
            logger.info(f"Bitbucket Repo is in monitored project: {project} ")
            if snyk_monitor(new_repo,"dev"):
                logger.info (f"Monitoring {dev_org}/{new_repo}")
            else:
                logger.info (f"Could not monitor {dev_org}/{new_repo}")