from ingest.api.ingestapi import IngestApi


class SummaryService:

    def __init__(self):
        self.ingestapi = IngestApi()

    def summary_for_submission(self, submission_uri):
        """
        Given a submission URI, returns a detailed summary of the submission i.e the amount of each entity type in the
        submission(i.e biomaterial, file, protocol, ...), further broken down by entity type (e.g donor, tissue, cell
        suspension)

        :param submission_uri: URI string for the submission
        :return: A SubmissionSummary for this submission
        """
        submission_summary = SubmissionSummary()

        submission_summary.biomaterial_summary = self.generate_biomaterial_summary(submission_uri)


    def generate_biomaterial_summary(self, submission_uri):
        return dict()

    def generate_project_summary(self, submission_uri):
        return dict()

    def generate_protocol_summary(self, submission_uri):
        return dict()

    def generate_file_summary(self, submission_uri):
        return dict()

    def generate_process_summary(self, submission_uri):
        return dict()

    def get_entities_in_submission(self, submission_uri, entity_type):
        return self.ingestapi.getEntities(submission_uri, entity_type)

    def generate_summary_for_entity(self, submission_uri, entity_type):
        """
        given a core entity type of the ingest API (i.e biomaterial, protocol, process, ...), and a submission,
        returns a detailed summary i.e each of the entity type in the envelope broken down by specific type

        :param submission_uri: URI string for the submission
        :param entity_type: the type of the entity (e.g biomaterial, protocol, process, ...)
        :return: a summary with a count of each entity type, further broken down by count of each specific entity type
        """
        entity_summary = dict()
        entity_summary['count'] = 0
        entity_summary['breakdown'] = dict()

        entity_specific_types = dict()
        entities = self.get_entities_in_submission(submission_uri, entity_type)
        for entity in entities:
            specific_type = self.parse_specific_entity_type(entity)
            if specific_type not in entity_specific_types:
                entity_specific_types[specific_type] = {'count': 0}

            entity_specific_types[specific_type]['count'] += 1
            entity_summary['count'] += 1

        entity_summary['breakdown'] = entity_specific_types

    @staticmethod
    def parse_specific_entity_type(entity):
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


class SubmissionSummary:

    def __init__(self):
        self.biomaterial_summary = dict()
        self.protocol_summary = dict()
        self.process_summary = dict()
        self.file_summary = dict()
        self.project_summary = dict()
