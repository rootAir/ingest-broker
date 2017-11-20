import unittest
import json
import os

from broker.xlsconverter import SpreadsheetConverter

ENCODING = 'utf-8'


class TestSpreadsheetConverter(unittest.TestCase):
    def setUp(self):
        self.converter = SpreadsheetConverter()
        self.input_dir = './input/'
        self.expected_dir = './expected/'

    def test_convert(self):
        test_filename = 'v4_E-MTAB-5061-test'

        spreadsheet = self.input_dir + test_filename + '.xlsx'

        actual_json = vars(self.converter.convert(spreadsheet))

        expected_file = self.expected_dir + test_filename + '.json'
        expected_json = json.load(open(expected_file))

        self.assertEqual(actual_json, expected_json, 'Spreadsheet is not converted correctly.')

    def test_convert_to_output_file(self):
        test_filename = 'v4_E-MTAB-5061-test'

        spreadsheet = self.input_dir + test_filename + '.xlsx'

        output_file = './actual/' + test_filename + '.json'

        if os.path.exists(output_file):
            os.remove(output_file)

        self.converter.convert(spreadsheet, output_file)

        expected_file = self.expected_dir + test_filename + '.json'
        expected_json = json.load(open(expected_file))

        self.assertTrue(os.path.exists(output_file), 'Output file not created.')

        actual_json = json.load(open(output_file))

        self.assertEqual(actual_json, expected_json, 'Spreadsheet is not converted correctly.')
