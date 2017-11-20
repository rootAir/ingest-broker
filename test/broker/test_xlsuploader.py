import unittest
import json
import os

from broker.xlsuploader import SpreadsheetUploader

ENCODING = 'utf-8'


class TestSpreadsheetConverter(unittest.TestCase):
    def setUp(self):
        self.uploader = SpreadsheetUploader()
        self.input_dir = './input/'
        self.expected_dir = './expected/'

    def test_submit(self):
        test_filename = 'v4_E-MTAB-5061-test'

        spreadsheet = self.input_dir + test_filename + '.xlsx'

        submission_url = self.uploader.submit(spreadsheet)

        self.assertTrue(submission_url)
