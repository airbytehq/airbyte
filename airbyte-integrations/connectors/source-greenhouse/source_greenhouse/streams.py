#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Type
from urllib import parse

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class GreenhouseStream(HttpStream, ABC):
    url_base = "https://harvest.greenhouse.io/v1/"
    page_size = 100
    primary_key = "id"

    def path(self, **kwargs) -> str:
        # wrap with str() to pass mypy pre-commit validation
        return str(self.name)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # parsing response header links is the recommended pagination method https://developers.greenhouse.io/harvest.html#pagination
        parsed_link = parse.urlparse(response.links.get("next", {}).get("url", ""))
        if parsed_link:
            query_params = dict(parse.parse_qsl(parsed_link.query))
            return query_params
        return None

    def request_params(self, next_page_token: Optional[Mapping[str, Any]] = None, **kwargs) -> MutableMapping[str, Any]:
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
    def parent_stream(self) -> Type[GreenhouseStream]:
        """
        :return: parent stream class
        """

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        items = self.parent_stream(authenticator=self._session.auth)
        for item in items.read_records(sync_mode=SyncMode.full_refresh):
            yield {"parent_id": item["id"]}

    def path(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> str:
        stream_slice = stream_slice or {}
        return self.path_template.format(parent_id=stream_slice["parent_id"])


class Applications(GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-applications
    """


class ApplicationsDemographicsAnswers(GreenhouseSubStream, GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-demographic-answers
    """

    parent_stream = Applications
    path_template = "applications/{parent_id}/demographics/answers"


class ApplicationsInterviews(GreenhouseSubStream, GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-scheduled-interviews-for-application
    """

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

    parent_stream = Jobs
    path_template = "jobs/{parent_id}/openings"


class JobsStages(GreenhouseSubStream, GreenhouseStream):
    """
    Docs: https://developers.greenhouse.io/harvest.html#get-list-job-stages-for-job
    """

    parent_stream = Jobs
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
