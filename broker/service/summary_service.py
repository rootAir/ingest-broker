from ingest.api.ingestapi import IngestApi
from broker.common.submission_summary import SubmissionSummary
from broker.common.project_summary import ProjectSummary
from broker.common.entity_summary import EntitySummary
from .submission_summary_cache import SubmissionSummaryCache
from .exception.cache_miss_exception import CacheMissException


from typing import Generator
from typing import Iterable
from typing import Callable
from functools import reduce

import json


class SummaryService:

    def __init__(self, ingest_api=None, submission_summary_cache=None):
        self.ingestapi = IngestApi() if not ingest_api else ingest_api
        self.submission_summary_cache = SubmissionSummaryCache() if not submission_summary_cache else submission_summary_cache

    # TODO: consider storing generators here and generating the complete summary in one pass
    class SubmissionEntities:
        def __init__(self, biomaterials=None, projects=None, processes=None, protocols=None, files=None):
            self.biomaterials = biomaterials if biomaterials else []
            self.projects = projects if projects else []
            self.processes = processes if processes else []
            self.protocols = protocols if protocols else []
            self.files = files if files else []


    def summary_for_project(self, project_resource) -> ProjectSummary:
        project_summary = ProjectSummary()

        project_submissions = self.get_submissions_in_project(project_resource)
        submission_summaries = [self.summary_for_submission(submission) for submission in project_submissions]

        for summary in submission_summaries:
            project_summary.addSubmissionSummary(summary)

        return project_summary

    def summary_for_submission(self, submission_resource) -> SubmissionSummary:
        """
        Given a submission URI, returns a detailed summary of the submission.

        The summary will specify the amount of each entity type in the submission(i.e biomaterial, file, protocol, ...),
        further broken down by entity type (e.g donor, tissue, cell suspension), ...

        In addition, an attempt will be made to parse specific information from the submission such as the project
        title, # of cells, organ, donor, ...

        :param submission_uri: URI string for the submission
        :return: A SubmissionSummary for this submission
        """
        submission_uuid = self.uuid_from_submission(submission_resource)

        try:
            submission_summary = self.submission_summary_cache.get(submission_uuid)
            return submission_summary
        except CacheMissException:
            submission_summary = SubmissionSummary()
            submission_uri = submission_resource['_links']['self']['href']

            submissions_entities = self.get_all_entities_in_submission(submission_uri)
            submission_summary = self.add_entity_count_breakdown(submission_summary, submissions_entities)
            self.add_specific_submission_information(submission_summary, submissions_entities, None) # TODO: pass a scrape-config

            submission_summary.create_date = submission_resource['submissionDate']
            submission_summary.last_updated_date = submission_resource['updateDate']
            submission_summary.submission_status = submission_resource['submissionState']

            self.submission_summary_cache.insert(submission_uuid, submission_summary)
            return submission_summary

    def add_entity_count_breakdown(self, submission_summary, submission_entities):
        submission_summary.biomaterial_summary = self.generate_summary_for_entity(submission_entities.biomaterials)
        submission_summary.project_summary = self.generate_summary_for_entity(submission_entities.projects)
        submission_summary.protocol_summary = self.generate_summary_for_entity(submission_entities.protocols)
        submission_summary.file_summary = self.generate_summary_for_entity(submission_entities.files)
        submission_summary.process_summary = self.generate_summary_for_entity(submission_entities.processes)
        return submission_summary


    def add_specific_submission_information(self, submission_summary, submission_entities, information_map):
        """
        With instructions from the information_map, this will attempt to find specific submission info and add
        it to the summary
        :param submission_summary:
        :param submission_entities:
        :param information_map:
        :return:
        """

        pass # TODO



    def get_entities_in_submission(self, submission_uri, entity_type) -> Generator[dict, None, None]:
        yield from self.ingestapi.getEntities(submission_uri, entity_type, 1000)

    def get_all_entities_in_submission(self, submission_uri):
        return self.SubmissionEntities(list(self.get_entities_in_submission(submission_uri, 'biomaterials')),
                                       list(self.get_entities_in_submission(submission_uri, 'projects')),
                                       list(self.get_entities_in_submission(submission_uri, 'processes')),
                                       list(self.get_entities_in_submission(submission_uri, 'protocols')),
                                       list(self.get_entities_in_submission(submission_uri, 'files')))

    def get_submissions_in_project(self, project_resource) -> Generator[dict, None, None]:
        yield from self.ingestapi.getRelatedEntities('submissionEnvelopes', project_resource, 'submissionEnvelopes')

    def generate_summary_for_entity(self, entities) -> EntitySummary:
        """
        given a collection of entities (i.e biomaterials, protocols, processes, ...) a submission,
        returns a summary of the entities i.e specific entity types with releated counts

        :param entities: entities from which to generate an entity summary
        :param entity_type: the type of the entity (e.g biomaterial, protocol, process, ...)
        :return: a summary with a count of each entity type, further broken down by count of each specific entity type
        """
        entity_summary = EntitySummary()

        entity_specific_types = dict()
        for entity in entities:
            specific_type = self.parse_specific_entity_type(entity)
            if specific_type not in entity_specific_types:
                entity_specific_types[specific_type] = {'count': 0}

            entity_specific_types[specific_type]['count'] += 1
            entity_summary.count += 1

        entity_summary.breakdown = entity_specific_types
        return entity_summary

    @staticmethod
    def parse_specific_entity_type(entity) -> str:
        """
        given a metadata entity in ingest, returns the 'specific' entity type (e.g donor, cell_suspension,
        analysis_file, etc.)
        :param entity: a metadata entity
        :return: the specific type of the entity as specified in the entity's 'describedBy', or 'unknown' if the
        'describedBy' field is not present
        """
        if 'content' not in entity and 'describedBy' not in entity['content']:
            return 'unknown'
        else:
            entity_described_by = entity['content']['describedBy']
            return entity_described_by.split('/')[-1]

    @staticmethod
    def uuid_from_submission(submission_resource) -> str:
        return submission_resource['uuid']['uuid']

class ScrapeConfig:
    """
    Represents a configuration file used to configure a SubmissionScraper
    """

    def __init__(self, placeholder_name, entity_type, path, post_process):
        self.placeholder_name = placeholder_name
        self.entity_type = entity_type
        self.path = path
        self.post_process = post_process

class SubmissionScraper:


    @staticmethod
    def scrape_configs_from_dict(config: dict) -> Generator[ScrapeConfig, None, None]:
        yield from map(lambda conf: ScrapeConfig(conf['placeholder'],
                                                 conf['entity_type'],
                                                 conf['path'],
                                                 conf['post_process']),
                       config.items())

    @staticmethod
    def scrape_configs_from_file(file) -> Generator[ScrapeConfig, None, None]:
        with open(file, 'rb') as config_file:
            config = json.load(config_file)
            yield from SubmissionScraper.scrape_configs_from_dict(config)

    class Directive:
        """
        A directive will instruct the scraper on where and how to find info to be scraped. Can be constructed
        with an optional reducer function to combine matching scraped data. The reducer function should take a
        collection of matching field-values as param and return a single value
        """

        def __init__(self, placeholder=None, entity_type=None, field_path=None, reducer=None):
            self.placeholder = placeholder
            self.entity_type = entity_type
            self.field_path = field_path
            self.reducer = reducer

    def __init__(self, directives=None):
        self.directives = directives if directives else []

    @staticmethod
    def from_scrape_configs(scrape_configs: Generator[ScrapeConfig, None, None]) -> Iterable[Directive]:
        """
        returns directives given scrap configs
        :param scrape_configs:
        :return:
        """
        return map(lambda scrape_config: SubmissionScraper.Directive(scrape_config.placeholder,
                                                                     scrape_config.entity_type,
                                                                     scrape_config.path,
                                                                     SubmissionScraper.reducer_for(scrape_config.post_process)), scrape_configs)

    @staticmethod
    def reducer_for(post_process_func: str):
        if post_process_func == "sum":
            return lambda collection: reduce((lambda x,y: x + y), collection)
        elif post_process_func == "count":
            return lambda collection: reduce((lambda x,y: x + 1), collection, 0)
        else:
            return lambda collection: collection # just return the collection

