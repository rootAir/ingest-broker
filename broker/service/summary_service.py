from ingest.api.ingestapi import IngestApi
from broker.common.submission_summary import SubmissionSummary
from broker.common.project_summary import ProjectSummary
from broker.common.entity_summary import EntitySummary
from .submission_summary_cache import SubmissionSummaryCache


from typing import Generator


class SummaryService:

    def __init__(self, ingest_api=None, submission_summary_cache=None):
        self.ingestapi = IngestApi() if not ingest_api else ingest_api
        self.submission_summary_cache = SubmissionSummaryCache() if not submission_summary_cache else submission_summary_cache

    def summary_for_project(self, project_resource) -> ProjectSummary:
        project_summary = ProjectSummary()

        project_submissions = self.get_submissions_in_project(project_resource)
        submission_summaries = [self.summary_for_submission(submission) for submission in project_submissions]

        for summary in submission_summaries:
            project_summary.addSubmissionSummary(summary)

        return project_summary

    def summary_for_submission(self, submission_resource) -> SubmissionSummary:
        """
        Given a submission URI, returns a detailed summary of the submission i.e the amount of each entity type in the
        submission(i.e biomaterial, file, protocol, ...), further broken down by entity type (e.g donor, tissue, cell
        suspension)

        :param submission_uri: URI string for the submission
        :return: A SubmissionSummary for this submission
        """
        submission_summary = SubmissionSummary()
        submission_uri = submission_resource['_links']['self']['href']

        submission_summary.biomaterial_summary = self.generate_biomaterial_summary(submission_uri)
        submission_summary.project_summary = self.generate_project_summary(submission_uri)
        submission_summary.protocol_summary = self.generate_protocol_summary(submission_uri)
        submission_summary.file_summary = self.generate_file_summary(submission_uri)
        submission_summary.process_summary = self.generate_process_summary(submission_uri)

        submission_summary.create_date = submission_resource['submissionDate']
        submission_summary.last_updated_date = submission_resource['updateDate']
        submission_summary.submission_status = submission_resource['submissionState']

        return submission_summary

    def generate_biomaterial_summary(self, submission_uri) -> EntitySummary:
        return self.generate_summary_for_entity(submission_uri, 'biomaterials')

    def generate_project_summary(self, submission_uri) -> EntitySummary:
        return self.generate_summary_for_entity(submission_uri, 'projects')

    def generate_protocol_summary(self, submission_uri) -> EntitySummary:
        return self.generate_summary_for_entity(submission_uri, 'protocols')

    def generate_file_summary(self, submission_uri) -> EntitySummary:
        return self.generate_summary_for_entity(submission_uri, 'files')

    def generate_process_summary(self, submission_uri) -> EntitySummary:
        return self.generate_summary_for_entity(submission_uri, 'processes')

    def get_entities_in_submission(self, submission_uri, entity_type) -> Generator[dict, None, None]:
        yield from self.ingestapi.getEntities(submission_uri, entity_type, 1000)

    def get_submissions_in_project(self, project_resource) -> Generator[dict, None, None]:
        yield from self.ingestapi.getRelatedEntities('submissionEnvelopes', project_resource, 'submissionEnvelopes')

    def generate_summary_for_entity(self, submission_uri, entity_type) -> EntitySummary:
        """
        given a core entity type of the ingest API (i.e biomaterial, protocol, process, ...), and a submission,
        returns a detailed summary i.e each of the entity type in the envelope broken down by specific type

        :param submission_uri: URI string for the submission
        :param entity_type: the type of the entity (e.g biomaterial, protocol, process, ...)
        :return: a summary with a count of each entity type, further broken down by count of each specific entity type
        """
        entity_summary = EntitySummary()

        entity_specific_types = dict()
        entities = self.get_entities_in_submission(submission_uri, entity_type)
        for entity in entities:
            specific_type = self.parse_specific_entity_type(entity)
            if specific_type not in entity_specific_types:
                entity_specific_types[specific_type] = {'count': 0}

            entity_specific_types[specific_type]['count'] += 1
            entity_summary.count += 1

        entity_summary.breakdown = entity_specific_types
        return entity_summary

    @staticmethod
    def parse_specific_entity_type(entity) -> str:
        """
        given a metadata entity in ingest, returns the 'specific' entity type (e.g donor, cell_suspension,
        analysis_file, etc.)
        :param entity: a metadata entity
        :return: the specific type of the entity as specified in the entity's 'describedBy', or 'unknown' if the
        'describedBy' field is not present
        """
        if 'content' not in entity and 'describedBy' not in entity['content']:
            return 'unknown'
        else:
            entity_described_by = entity['content']['describedBy']
            return entity_described_by.split('/')[-1]
