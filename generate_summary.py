from broker.service.summary_service import SummaryService
from ingest.api.ingestapi import IngestApi

import uuid
import jsonpickle
import argparse


def generate_submission_summary(uuid, ingest_url):
    ingest_api = IngestApi(ingest_url)
    submission = ingest_api.getSubmissionByUuid(uuid)
    summary = SummaryService().summary_for_submission(submission)

    return jsonpickle.encode(summary, unpicklable=False)


def generate_project_summary(uuid, ingest_url):
    ingest_api = IngestApi(ingest_url)
    project = ingest_api.getProjectByUuid(uuid)
    summary = SummaryService().summary_for_project(project)

    return jsonpickle.encode(summary, unpicklable=False)


def check_uuid(uuid_str):
    try:
        uuid.UUID(uuid_str, version=4)
        return uuid_str
    except:
        raise argparse.ArgumentTypeError("%s is an invalid uuid value" % uuid_str)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('ingest_api', metavar='H', nargs=1, help='the url of the ingest API (e.g http://api.ingest.dev.data.humancellatlas.org)')
    parser.add_argument('summary_type', metavar='T', nargs=1, choices=['project', 'submission'], help='the type of summary (project or submission)')
    parser.add_argument('uuid', metavar='U', nargs=1, type=check_uuid,help='the uuid of the project/submission')

    args = parser.parse_args()

    uuid_str = args.uuid[0]
    summary_type = args.summary_type[0]
    ingest_url = args.ingest_api[0]

    summary = generate_project_summary(uuid_str, ingest_url) if summary_type == 'project' else generate_submission_summary(uuid_str, ingest_url)

    print(summary)


