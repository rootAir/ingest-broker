from unittest import TestCase
from unittest.mock import patch

from brokerapi import broker_app
from brokerapi.broker_app import app

class BrokerAppTest(TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_authorization_failed(self):
        # when:
        response = self.client.post('/api_upload')

        # then:
        self.assertEqual(401, response.status_code)

    def test_failed_save(self):
        with patch.object(broker_app, '_save_file') as save_file:
            # given:
            assert save_file is broker_app._save_file
            save_file.side_effect = Exception("I/O error")

            # when:
            response = self.client.post('/api_upload', headers={'Authorization': 'auth'})

            # then:
            self.assertEqual(500, response.status_code)
