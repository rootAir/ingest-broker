from unittest import TestCase
from unittest.mock import patch

from broker.service.summary_service import SummaryService
from ingest.api.ingestapi import IngestApi


class SummaryServiceTest(TestCase):

    def test_generate_summary_for_entity(self):
        mock_ingest_api = patch('__main__.IngestApi')
        mock_envelope_uri = 'http://mock-ingest-api/envelopes/mock-envelope-id'
        mock_specific_type = 'reanimated_donor'

        summary_service = SummaryService(mock_ingest_api)
        with patch('broker.service.summary_service.SummaryService.get_entities_in_submission') as mock_get_entities_in_submission:
            mock_biomaterial_entities = self.generate_mock_entities(10, mock_specific_type)
            mock_get_entities_in_submission.return_value = mock_biomaterial_entities

            entity_summary = summary_service.generate_summary_for_entity(mock_envelope_uri, mock_specific_type)
            assert mock_specific_type in entity_summary.breakdown
            assert entity_summary.count == 10

    @staticmethod
    def generate_mock_entities(count, specific_type):
        return list(map(lambda indx: {'content': {'describedBy': 'http://mock-schema/something/{0}'.format(specific_type)}}, range(0, count)))
