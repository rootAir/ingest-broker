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

    def test_generate_submission_summary(self):
        mock_ingest_api = patch('__main__.IngestApi')
        mock_envelope_uri = 'http://mock-ingest-api/envelopes/mock-envelope-id'
        mock_envelope_resource = {'_links': {'self': {'href': mock_envelope_uri}}}

        summary_service = SummaryService(mock_ingest_api)
        with patch('broker.service.summary_service.SummaryService.get_entities_in_submission') as mock_get_entities_in_submission:
            def get_entities_in_submission_mock(*args, **kwargs):
                envelope_uri = args[0]
                entity_type = args[1]

                type_to_mock_specific_type_map = {'processes': 'specific-process',
                                                  'biomaterials': 'specific-biomaterial',
                                                  'protocols': 'specific-protocol',
                                                  'files': 'specific-file',
                                                  'projects': 'specific-project'
                                                  }

                if envelope_uri == mock_envelope_uri:
                    yield from self.generate_mock_entities(10, type_to_mock_specific_type_map[entity_type])
                else:
                    yield

            mock_get_entities_in_submission.side_effect = get_entities_in_submission_mock
            submission_summary = summary_service.summary_for_submission(mock_envelope_resource)
            
            assert submission_summary.process_summary.count == 10
            assert 'specific-process' in submission_summary.process_summary.breakdown

            assert submission_summary.file_summary.count == 10
            assert 'specific-file' in submission_summary.file_summary.breakdown

            assert submission_summary.biomaterial_summary.count == 10
            assert 'specific-biomaterial' in submission_summary.biomaterial_summary.breakdown

            assert submission_summary.project_summary.count == 10
            assert 'specific-project' in submission_summary.project_summary.breakdown

            assert submission_summary.protocol_summary.count == 10
            assert 'specific-protocol' in submission_summary.protocol_summary.breakdown

    @staticmethod
    def generate_mock_entities(count, specific_type):
        for i in range(0, count):
            yield {'content': {'describedBy': 'http://mock-schema/something/{0}'.format(specific_type)}}
