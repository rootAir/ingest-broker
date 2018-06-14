from .entity_summary import EntitySummary


class ProjectSummary:

    def __init__(self):
        self.biomaterial_summary = EntitySummary()
        self.protocol_summary = EntitySummary()
        self.process_summary = EntitySummary()
        self.file_summary = EntitySummary()
        self.project_summary = EntitySummary()

        self.submission_status = None
        self.create_date = None
        self.last_updated_date = None

    def addSubmissionSummary(self, submission_summary) -> 'ProjectSummary':
        """
        Adds a submission summary to this project summary
        :param submission_summary: SubmissionSummary to add to self
        :return: self
        """
        return self
