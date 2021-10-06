#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import re
from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional
from urllib import parse

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class GreenhouseStream(HttpStream, ABC):
    url_base = "https://harvest.greenhouse.io/v1/"
    page_size = 100
    primary_key = "id"

    @property
    def data_field(self) -> str:
        """
        :return: Default field name to get data from response
        """

        return self.name

    def path(self, **kwargs) -> str:
        return self.name

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # parsing response header is the recommended pagination method https://developers.greenhouse.io/harvest.html#pagination
        next_page_search = re.search(f'<({re.escape(self.url_base)}.+)>; rel="next"', response.headers.get("link", ""))
        if next_page_search:
            parsed_link = parse.urlparse(next_page_search.group(1))
            query_params = dict(parse.parse_qsl(parsed_link.query))
            return query_params

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"per_page": self.page_size}
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """

        yield from response.json()


class GreenhouseSubStream(GreenhouseStream):
    @property
    @abstractmethod
    def path_template(self) -> str:
        """
        :return: sub stream path template
        """

    @property
    @abstractmethod
    def parent_stream(self) -> GreenhouseStream:
        """
        :return: parent stream class
        """

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        items = self.parent_stream(authenticator=self._session.auth)
        for item in items.read_records(sync_mode=SyncMode.full_refresh):
            yield {"parent_id": item["id"]}

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        return self.path_template.format(parent_id=stream_slice["parent_id"])


class Applications(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-applications
    """


class ApplicationsDemographicsAnswers(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-demographic-answers
    """

    name = "applications.demographics_answers"

    def path(self, **kwargs) -> str:
        return "demographics/answers"


class ApplicationsInterviews(GreenhouseSubStream, GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-scheduled-interviews-for-application
    """

    name = "applications.interviews"
    parent_stream = Applications
    path_template = "applications/{parent_id}/scheduled_interviews"


class Candidates(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-candidates
    """


class CloseReasons(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-close-reasons
    """


class CustomFields(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-custom-fields
    """


class Degrees(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-degrees
    """


class DemographicsAnswers(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-demographic-answers
    """

    def path(self, **kwargs) -> str:
        return "demographics/answers"


class DemographicsAnswerOptions(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-demographic-answer-options
    """

    def path(self, **kwargs) -> str:
        return "demographics/answer_options"


class DemographicsQuestions(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-demographic-questions
    """

    def path(self, **kwargs) -> str:
        return "demographics/questions"


class DemographicsAnswersAnswerOptions(GreenhouseSubStream, GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-demographic-answer-options-for-demographic-question
    """

    name = "demographics_answers.answer_options"
    parent_stream = DemographicsQuestions
    path_template = "demographics/questions/{parent_id}/answer_options"


class DemographicsQuestionSets(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-demographic-question-sets
    """

    def path(self, **kwargs) -> str:
        return "demographics/question_sets"


class DemographicsQuestionSetsQuestions(GreenhouseSubStream, GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-demographic-questions-for-demographic-question-set
    """

    name = "demographics_question_sets.questions"
    parent_stream = DemographicsQuestionSets
    path_template = "demographics/question_sets/{parent_id}/questions"


class Departments(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-departments
    """


class Interviews(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-scheduled-interviews
    """

    def path(self, **kwargs) -> str:
        return "scheduled_interviews"


class JobPosts(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-job-posts
    """


class JobStages(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-job-stages
    """


class Jobs(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-jobs
    """


class JobsOpenings(GreenhouseSubStream, GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-job-openings
    """

    name = "jobs.openings"
    parent_stream = DemographicsQuestionSets
    path_template = "jobs/{parent_id}/openings"


class JobsStages(GreenhouseSubStream, GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-job-stages-for-job
    """

    name = "jobs.stages"
    parent_stream = DemographicsQuestionSets
    path_template = "jobs/{parent_id}/stages"


class Offers(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-offers
    """


class RejectionReasons(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-rejection-reasons
    """


class Scorecards(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-scorecards
    """


class Sources(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-sources
    """


class Users(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-users
    """
