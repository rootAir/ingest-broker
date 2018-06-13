class SubmissionSummary:

    class EntitySummary:
        def __init__(self):
            self.count = 0
            self.breakdown = dict()

    def __init__(self):
        self.biomaterial_summary = SubmissionSummary.EntitySummary()
        self.protocol_summary = SubmissionSummary.EntitySummary()
        self.process_summary = SubmissionSummary.EntitySummary()
        self.file_summary = SubmissionSummary.EntitySummary()
        self.project_summary = SubmissionSummary.EntitySummary()

        self.submission_status = None
        self.create_date = None
        self.last_updated_date = None
