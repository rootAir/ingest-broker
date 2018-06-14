from .entity_summary import EntitySummary


class SubmissionSummary:
    
    def __init__(self):
        self.biomaterial_summary = EntitySummary()
        self.protocol_summary = EntitySummary()
        self.process_summary = EntitySummary()
        self.file_summary = EntitySummary()
        self.project_summary = EntitySummary()

        self.submission_status = None
        self.create_date = None
        self.last_updated_date = None
