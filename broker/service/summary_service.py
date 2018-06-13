from ingest.api.ingestapi import IngestApi


class SummaryService:

    def __init__(self):
        self.ingestapi = IngestApi()

    '''
    Given a submission UUID, returns a detailed summary of the submission i.e the amount of each entity type in the
    submission(i.e biomaterial, file, protocol, ...), further broken down by entity type (e.g donor, tissue, cell 
    suspension)
    '''
    def summary_for_submission(self, submission_uuid):
        submission_summary = SubmissionSummary()

        submission_summary.biomaterial_summary = self.generate_biomaterial_summary(submission_uuid)


    def generate_biomaterial_summary(self, submission_uuid):
        return dict()

    def generate_project_summary(self, submission_uuid):
        return dict()

    def generate_protocol_summary(self, submission_uuid):
        return dict()

    def generate_file_summary(self, submission_uuid):
        return dict()

    def generate_project_summary(self, submission_uuid):
        return dict()


class SubmissionSummary:

    def __init__(self):
        self.biomaterial_summary = dict()
        self.protocol_summary = dict()
        self.process_summary = dict()
        self.file_summary = dict()
        self.project_summary = dict()
