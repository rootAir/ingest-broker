import unittest
import json
import mock

from broker.hcaxlsbroker import SpreadsheetSubmission

ENCODING = 'utf-8'


class TestHCAXLSBroker(unittest.TestCase):
    def setUp(self):
        self.spreadsheet_submitter = SpreadsheetSubmission(dry=True)
        self.xls_file_path = '../example-input/v4E-MTAB-50161-reduced-1file.xls'

        pass

    def test_createSubmission(self):
        submission_url = SpreadsheetSubmission()
        self.assertTrue(submission_url)

    def test_submit(self):
        submission_url = SpreadsheetSubmission()
        self.spreadsheet_submitter.submit(self.xls_file_path, submission_url)
        self.assertTrue(submission_url)

    def test_dumpJsonToFile(self):
        pass

