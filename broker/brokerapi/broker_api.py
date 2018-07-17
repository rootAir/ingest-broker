#!/usr/bin/env python
from ingest.importer.spreadsheetUploadError import SpreadsheetUploadError

__author__ = "jupp"
__license__ = "Apache 2.0"

from flask import Flask, flash, request, render_template, redirect, url_for
from flask_cors import CORS, cross_origin
from flask import json
from ingest.api.ingestapi import IngestApi
from ingest.importer.importer import XlsImporter
from broker.service.summary_service import SummaryService

from werkzeug.utils import secure_filename
import os
import tempfile
import threading
import logging
import traceback
import jsonpickle

STATUS_LABEL = {
    'Valid': 'label-success',
    'Validating': 'label-info',
    'Invalid': 'label-danger',
    'Submitted': 'label-default',
    'Complete': 'label-default'
}

DEFAULT_STATUS_LABEL = 'label-warning'

HTML_HELPER = {
    'status_label': STATUS_LABEL,
    'default_status_label': DEFAULT_STATUS_LABEL
}

app = Flask(__name__, static_folder='static')
app.secret_key = 'cells'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
logger = logging.getLogger(__name__)


@app.route('/api_upload', methods=['POST'])
@cross_origin()
def upload_spreadsheet():
    try:
        logger.info("Uploading spreadsheet")
        token = _check_token()
        path = _save_spreadsheet()
        ingest_api = IngestApi()
        ingest_api.set_token(token)
        importer = XlsImporter(ingest_api)

        project = _check_for_project(ingest_api)

        project_uuid = None
        if project and project.get('uuid'):
            project_uuid = project.get('uuid').get('uuid')

        _attempt_dry_run(importer, path, project_uuid)

        submission_url = ingest_api.createSubmission(token)

        _submit_spreadsheet_data(importer, path, submission_url, project_uuid)

        return create_upload_success_response(submission_url)
    except SpreadsheetUploadError as spreadsheetUploadError:
        return create_upload_failure_response(spreadsheetUploadError.http_code, spreadsheetUploadError.message,
                                              spreadsheetUploadError.details)
    except Exception as err:
        logger.error(traceback.format_exc())
        return create_upload_failure_response(500, "We experienced a problem while uploading your spreadsheet",
                                              str(err))


@app.route('/submissions/<submission_uuid>/summary', methods=['GET'])
def submission_summary(submission_uuid):
    submission = IngestApi().getSubmissionByUuid(submission_uuid)
    summary = SummaryService().summary_for_submission(submission)

    return app.response_class(
        response=jsonpickle.encode(summary, unpicklable=False),
        status=200,
        mimetype='application/json'
    )


@app.route('/projects/<project_uuid>/summary', methods=['GET'])
def project_summary(project_uuid):
    project = IngestApi().getProjectByUuid(project_uuid)
    summary = SummaryService().summary_for_project(project)

    return app.response_class(
        response=jsonpickle.encode(summary, unpicklable=False),
        status=200,
        mimetype='application/json'
    )


def _submit_spreadsheet_data(importer, path, submission_url, project_uuid):

    logger.info("Attempting submission")
    thread = threading.Thread(target=importer.import_file, args=(path, submission_url, project_uuid))
    thread.start()
    logger.info("Spreadsheet upload completed")
    return submission_url


def _attempt_dry_run(importer, path, project_uuid=None):
    logger.info("Attempting dry run to validate spreadsheet")
    try:
        importer.dry_run_import_file(path, project_uuid=project_uuid)
    except Exception as err:
        logger.error(traceback.format_exc())
        message = "There was a problem validating your spreadsheet"
        raise SpreadsheetUploadError(400, message, str(err))


def _check_for_project(ingest_api):
    logger.info("Checking for project_id")
    project = None
    if 'project_id' in request.form:
        project_id = request.form['project_id']
        logger.info("Found project_id: " + project_id)

        project = ingest_api.getProjectById(project_id)

    else:
        logger.info("No existing project_id found")

    return project



def _save_spreadsheet():
    logger.info("Saving file")
    try:
        path = _save_file()
    except Exception as err:
        logger.error(traceback.format_exc())
        message = "We experienced a problem when saving your spreadsheet"
        raise SpreadsheetUploadError(500, message, str(err))
    return path


def _check_token():
    logger.info("Checking token")
    token = request.headers.get('Authorization')
    if token is None:
        raise SpreadsheetUploadError(401, "An authentication token must be supplied when uploading a spreadsheet",
                                     "")
    return token


def _save_file():
    f = request.files['file']
    filename = secure_filename(f.filename)
    path = os.path.join(tempfile.gettempdir(), filename)
    logger.info("Saved file to: " + path)
    f.save(path)
    return path


def create_upload_success_response(submission_url):
    ingest_api = IngestApi()
    submission_uuid = ingest_api.getObjectUuid(submission_url)
    display_id = submission_uuid or '<UUID not generated yet>'
    submission_id = submission_url.rsplit('/', 1)[-1]

    data = {
        "message": "Your spreadsheet was uploaded and processed successfully",
        "details": {
            "submission_url": submission_url,
            "submission_uuid": submission_uuid,
            "display_uuid": display_id,
            "submission_id": submission_id
        }
    }

    success_response = app.response_class(
        response=json.dumps(data),
        status=201,
        mimetype='application/json'
    )
    return success_response


def create_upload_failure_response(status_code, message, details):
    data = {
        "message": message,
        "details": details,
    }
    failure_response = app.response_class(
        response=json.dumps(data),
        status=status_code,
        mimetype='application/json'
    )
    print(failure_response)
    return failure_response


@app.route('/')
def index():
    submissions = []
    try:
        submissions = IngestApi().getSubmissions()
    except Exception as e:
        flash("Can't connect to Ingest API!!", "alert-danger")
    return render_template('index.html', submissions=submissions, helper=HTML_HELPER)


@app.route('/submissions/<submission_id>')
def get_submission_view(submission_id):
    ingest_api = IngestApi()
    submission = ingest_api.getSubmissionIfModifiedSince(submission_id, None)

    if submission:
        response = ingest_api.getProjects(submission_id)

        projects = []

        if '_embedded' in response and 'projects' in response['_embedded']:
            projects = response['_embedded']['projects']

        project = projects[0] if projects else None  # there should always 1 project

        files = []

        response = ingest_api.getFiles(submission_id)
        if '_embedded' in response and 'files' in response['_embedded']:
            files = response['_embedded']['files']

        file_page = None
        if 'page' in response:
            file_page = response['page']
            file_page['len'] = len(files)

        bundle_manifests = []
        bundle_manifest_obj = {}

        response = ingest_api.getBundleManifests(submission_id)
        if '_embedded' in response and 'bundleManifests' in response['_embedded']:
            bundle_manifests = response['_embedded']['bundleManifests']

        bundle_manifest_obj['list'] = bundle_manifests
        bundle_manifest_obj['page'] = None

        if 'page' in response:
            bundle_manifest_obj['page'] = response['page']
            bundle_manifest_obj['page']['len'] = len(bundle_manifests)

        return render_template('submission.html',
                               sub=submission,
                               helper=HTML_HELPER,
                               project=project,
                               files=files,
                               filePage=file_page,
                               bundleManifestObj=bundle_manifest_obj)
    else:
        flash("Submission doesn't exist!", "alert-danger")
        return redirect(url_for('index'))


@app.route('/submissions/<submission_id>/files')
def get_submission_files(submission_id):
    ingest_api = IngestApi()
    response = ingest_api.getFiles(submission_id)
    files = []
    if '_embedded' in response and 'files' in response['_embedded']:
        files = response['_embedded']['files']
    file_page = None
    if 'page' in response:
        file_page = response['page']
        file_page['len'] = len(files)
    return render_template('submission-files-table.html',
                           files=files,
                           filePage=file_page,
                           helper=HTML_HELPER)


@app.route('/submit', methods=['POST'])
def submit_envelope():
    sub_url = request.form.get("submissionUrl")
    ingest_api = IngestApi()
    if sub_url:
        ingest_api.finishSubmission(sub_url)
    return redirect(url_for('index'))
