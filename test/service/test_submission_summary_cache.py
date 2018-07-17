from unittest import TestCase
from time import sleep

from broker.service.submission_summary_cache import SubmissionSummaryCache
from broker.common.submission_summary import SubmissionSummary
from broker.service.exception.cache_miss_exception import CacheMissException

TWO_SECONDS = 2


class SubmissionSummaryCacheTest(TestCase):

    def test_cache_expiry(self):
        cache_size = 10
        cache_expiry = TWO_SECONDS

        summary_cache = SubmissionSummaryCache(cache_size, cache_expiry)

        mock_submission_uuid = 'mock-submission-uuid'
        mock_submission_summary = SubmissionSummary()

        summary_cache.insert(mock_submission_uuid, mock_submission_summary)

        try:
            assert summary_cache.get(mock_submission_uuid)
        except CacheMissException:
            assert False

        sleep(3)

        try:
            summary_cache.get(mock_submission_uuid)
            assert False
        except CacheMissException:
            pass
