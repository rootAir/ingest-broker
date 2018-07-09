import csv
from functools import reduce
from broker.common.submission_summary import SubmissionSummary
from broker.common.project_summary import ProjectSummary


class TSVSummaryUtil:

    @staticmethod
    def project_summary_to_tsv(project_summary: ProjectSummary):
        breakdowns = TSVSummaryUtil.breakdowns_from_project_summary(project_summary)
        entity_count_tuples = TSVSummaryUtil.entity_count_tuples_from_breakdowns(breakdowns)

        return TSVSummaryUtil.entity_count_tuples_to_tsv(entity_count_tuples)

    @staticmethod
    def submission_summary_to_tsv(submission_summary: SubmissionSummary):
        breakdowns = TSVSummaryUtil.breakdowns_from_submission_summary(submission_summary)
        entity_count_tuples = TSVSummaryUtil.entity_count_tuples_from_breakdowns(breakdowns)

        return TSVSummaryUtil.entity_count_tuples_to_tsv(entity_count_tuples)

    @staticmethod
    def breakdowns_from_project_summary(project_summary: ProjectSummary):
        return [project_summary.protocol_summary.breakdown,
                project_summary.process_summary.breakdown,
                project_summary.biomaterial_summary.breakdown,
                project_summary.file_summary.breakdown]

    @staticmethod
    def breakdowns_from_submission_summary(submission_summary: SubmissionSummary):
        return [submission_summary.protocol_summary.breakdown,
                submission_summary.process_summary.breakdown,
                submission_summary.biomaterial_summary.breakdown,
                submission_summary.file_summary.breakdown,
                submission_summary.project_summary.breakdown]

    @staticmethod
    def entity_count_tuples_from_breakdowns(breakdowns: list):
        return reduce(lambda xs, ys: xs + ys,
                      map(lambda breakdown: TSVSummaryUtil.breakdown_to_entity_count_tuple(breakdown), breakdowns))

    @staticmethod
    def breakdown_to_entity_count_tuple(breakdown: dict):
        return [(key, breakdown[key]["count"]) for key in breakdown.keys()]

    @staticmethod
    def entity_count_tuples_to_tsv(entity_count_tuples: list):
        with open('report.tsv', 'w') as tsvfile:
            headers = list([entity_count_tuple[0] for entity_count_tuple in entity_count_tuples])
            counts = list([entity_count_tuple[1] for entity_count_tuple in entity_count_tuples])

            writer = csv.writer(tsvfile,  delimiter='\t')
            writer.writerow(headers)
            writer.writerow(counts)
            return writer
