import json
import logging

from ingestapi import IngestApi
from xlsconverter import SpreadsheetConverter


class SpreadsheetUploader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ingest_api = IngestApi()
        self.converter = SpreadsheetConverter()

    def submit(self, path_to_spreadsheet, output_file=None):
        converter_output = self.converter.convert(path_to_spreadsheet, output_file)

        submission_url = self.ingest_api.createSubmission()

        project_ingest = self.ingest_api.createProject(submission_url, json.dumps(converter_output.project))

        protocol_map = {}

        for protocol in converter_output.protocols:
            protocol_ingest = self.ingest_api.createProtocol(submission_url, json.dumps(protocol))
            protocol_map[protocol["protocol_id"]] = protocol_ingest

        sample_map = {}

        for index, sample in enumerate(converter_output.samples):
            sample_protocols = []
            if "protocol_ids" in sample:
                sample_protocols = sample["protocol_ids"]
                del sample["protocol_ids"]

            sample_ingest = self.ingest_api.createSample(submission_url, json.dumps(sample))

            self.ingest_api.linkEntity(sample_ingest, project_ingest, "projects")

            sample_id = sample['sample_id']
            sample_map[sample_id] = sample_ingest

            # if "derived_from" in sample:
                # TODO bug in v4 changes, not working because derived_from is not in ingest json document sample created
                # TODO check if this is being done in v3, do we need to link the samples to its donor>
                # TODO if we want to link it, we must make sure that donors are being added first in the ingest database
                # self.ingest_api.linkEntity(sample_ingest, sample_map[sample["derived_from"]], "derivedFromSamples")

            if sample_protocols:
                for sampleProtocolId in sample_protocols:
                    self.ingest_api.linkEntity(sample_ingest, protocol_map[sampleProtocolId], "protocols")

        files_map = {}

        for file in converter_output.files:
            sample = file["sample_id"]
            del file["assay_id"]
            del file["seq"]
            del file["sample_id"]

            file["core"] = {"type": "file"}

            file_ingest = self.ingest_api.createFile(submission_url, file["filename"], json.dumps(file))
            files_map[file["filename"]] = file_ingest

        for assay in converter_output.assays:
            assay_sample = assay["sample_id"]
            assay_files = assay["files"]

            del assay["sample_id"]
            del assay["files"]

            assay_ingest = self.ingest_api.createAssay(submission_url, json.dumps(assay))
            self.ingest_api.linkEntity(assay_ingest, project_ingest, "projects")

            if assay_sample in sample_map:
                self.ingest_api.linkEntity(assay_ingest, sample_map[assay_sample], "samples")

            for assay_file in assay_files:
                self.ingest_api.linkEntity(assay_ingest, files_map[assay_file], "files")

        self.logger.info("All done!")

        return True
