class ProjectSummary:

    class EntitySummary:
        def __init__(self):
            self.count = 0
            self.breakdown = dict()

    def __init__(self):
        self.biomaterial_summary = ProjectSummary.EntitySummary()
        self.protocol_summary = ProjectSummary.EntitySummary()
        self.process_summary = ProjectSummary.EntitySummary()
        self.file_summary = ProjectSummary.EntitySummary()
        self.project_summary = ProjectSummary.EntitySummary()

        self.submission_status = None
        self.create_date = None
        self.last_updated_date = None
