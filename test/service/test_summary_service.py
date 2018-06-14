from unittest import TestCase
from unittest.mock import patch

from broker.service.summary_service import SummaryService

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
        mock_envelope_submission_date = '2018-03-22T10:01:48.290Z'
        mock_envelope_update_date = '2018-03-22T10:02:45.224Z'
        mock_envelope_status = "PROCESSING"

        mock_envelope_resource = dict()
        mock_envelope_resource['_links'] = {'self': {'href': mock_envelope_uri}}
        mock_envelope_resource['submissionDate'] = mock_envelope_submission_date
        mock_envelope_resource['updateDate'] = mock_envelope_update_date
        mock_envelope_resource['submissionState'] = mock_envelope_status
        mock_envelope_resource['uuid'] = {'uuid': 'mock-envelope-uuid'}

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

            assert submission_summary.submission_status == mock_envelope_status
            assert submission_summary.create_date == mock_envelope_submission_date
            assert submission_summary.last_updated_date == mock_envelope_update_date

    def test_generate_project_summary(self):
        summary_service = SummaryService(patch('__main__.IngestApi'))
        mock_project_id = 'mock-project-id'
        mock_project_resource = dict()
        mock_project_resource['_links'] = dict()
        mock_project_resource['_links']['envelopes'] = {'href': 'http://mock-ingest-api/projects/{0}/envelopes'.format(mock_project_id)}

        with patch('broker.service.summary_service.SummaryService.get_submissions_in_project') as mock_get_project_submissions:
            def get_submissions_in_project_mock(*args, **kwargs):
                if args[0] == mock_project_resource:
                    yield from self.generate_mock_submissions_in_project(10)
                else:
                    yield

            mock_get_project_submissions.side_effect = get_submissions_in_project_mock

            with patch('broker.service.summary_service.SummaryService.get_entities_in_submission') as mock_get_entities_in_submission:
                def get_entities_in_submission_mock(*args, **kwargs):
                    entity_type = args[1]

                    type_to_mock_specific_type_map = {'processes': 'specific-process',
                                                      'biomaterials': 'specific-biomaterial',
                                                      'protocols': 'specific-protocol',
                                                      'files': 'specific-file',
                                                      'projects': 'specific-project'
                                                      }

                    yield from self.generate_mock_entities(10, type_to_mock_specific_type_map[entity_type])

                mock_get_entities_in_submission.side_effect = get_entities_in_submission_mock

                project_summary = summary_service.summary_for_project(mock_project_resource)

                assert project_summary.file_summary.count == 100  # 10 envelopes within, each with 10 files
                assert project_summary.process_summary.count == 100  # ...
                assert project_summary.protocol_summary.count == 100  # ...
                assert project_summary.biomaterial_summary.count == 100  # ...



    @staticmethod
    def generate_mock_submissions_in_project(count):
        if not (1 <= count <= 10):
            raise Exception("count must be between 1 and 10")
        else:
            for i in range(0, count):
                mock_envelope_id = 'mock-envelope-id-{0}'.format(str(i))
                mock_envelope_uuid = 'ffffffff-ffff-ffff-ffff-fffffffffff{0}'.format(str(i))
                submission = dict()
                submission['_links'] = dict()

                submission['_links']['biomaterials'] = {'href': 'http://mock-ingest-api/envelopes/{0}/biomaterials'.format(mock_envelope_id)}
                submission['_links']['files'] = {'href': 'http://mock-ingest-api/envelopes/{0}/files'.format(mock_envelope_id)}
                submission['_links']['processes'] = {'href': 'http://mock-ingest-api/envelopes/{0}/processes'.format(mock_envelope_id)}
                submission['_links']['protocols'] = {'href': 'http://mock-ingest-api/envelopes/{0}/protocols'.format(mock_envelope_id)}
                submission['_links']['projects'] = {'href': 'http://mock-ingest-api/envelopes/{0}/projects'.format(mock_envelope_id)}
                submission['_links']['self'] = {'href': mock_envelope_id}

                submission['uuid'] = {'uuid': mock_envelope_uuid}
                submission['submissionDate'] = 'mock-submission-date'
                submission['updateDate'] = 'mock-update-date'
                submission['submissionState'] = 'mock-submission-state'

                yield submission



    @staticmethod
    def generate_mock_entities(count, specific_type):
        for i in range(0, count):
            yield {'content': {'describedBy': 'http://mock-schema/something/{0}'.format(specific_type)}}
