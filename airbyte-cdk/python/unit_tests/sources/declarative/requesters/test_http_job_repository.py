from typing import Mapping
from unittest import TestCase
from unittest.mock import Mock

from airbyte_cdk import DpathExtractor, HttpRequester, BearerAuthenticator, JsonDecoder, HttpMethod
from airbyte_cdk.sources.declarative.async_job.job import AsyncJobStatus
from airbyte_cdk.sources.declarative.auth.token_provider import InterpolatedStringTokenProvider
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.http_job_repository import AsyncHttpJobRepository


class SendgridHttpJobRepositoryTest(TestCase):
    def setUp(self) -> None:
        url_base = "https://api.sendgrid.com/v3/"
        config = {"api_key": <put API key here>, "start_date": "2019-05-20T13:43:57Z"}
        authenticator = BearerAuthenticator(
            token_provider=InterpolatedStringTokenProvider(
                config=config,
                api_token="{{ config['api_key'] }}",
                parameters={},
            ),
            config=config,
            parameters={},
        )
        message_repository = Mock()
        error_handler = DefaultErrorHandler(config=config, parameters={})
        request_options_provider = None

        self._create_job_requester = HttpRequester(
            name="sendgrid contacts export: create_job",
            url_base=url_base,
            path="marketing/contacts/exports",
            authenticator=authenticator,
            error_handler=error_handler,
            http_method=HttpMethod.POST,
            request_options_provider=request_options_provider,
            config=config,
            disable_retries=False,
            parameters={},
            message_repository=message_repository,
            use_cache=False,
            stream_response=False,
        )

        self._polling_job_requester = HttpRequester(
            name="sendgrid contacts export: polling",
            url_base=url_base,
            path="marketing/contacts/exports/{{stream_slice['create_job_response'].json()['id'] }}",
            authenticator=authenticator,
            error_handler=error_handler,
            http_method=HttpMethod.GET,
            request_options_provider=request_options_provider,
            config=config,
            disable_retries=False,
            parameters={},
            message_repository=message_repository,
            use_cache=False,
            stream_response=False,
        )

        self._download_job_requester = HttpRequester(
            name="sendgrid contacts export: fetch_result",
            url_base="",
            path="{{stream_slice['url']}}",
            authenticator=None,
            error_handler=error_handler,
            http_method=HttpMethod.GET,
            request_options_provider=request_options_provider,
            config=config,
            disable_retries=False,
            parameters={},
            message_repository=message_repository,
            use_cache=False,
            stream_response=True,
        )


        self._status_extractor = DpathExtractor(decoder=JsonDecoder(parameters={}), field_path=["status"], config={}, parameters={} or {})
        self._urls_extractor = DpathExtractor(decoder=JsonDecoder(parameters={}), field_path=["urls"], config={}, parameters={} or {})

    def test_sendgrid(self) -> None:
        repository = AsyncHttpJobRepository(
            create_job_requester=self._create_job_requester,
            polling_job_requester=self._polling_job_requester,
            download_job_requester=self._download_job_requester,
            status_extractor=self._status_extractor,
            status_mapping={
                "ready": AsyncJobStatus.COMPLETED,
                "failure": AsyncJobStatus.FAILED,
                "pending": AsyncJobStatus.RUNNING,
            },
            urls_extractor=self._urls_extractor,
        )

        job = repository.start({})
        while job.status() != AsyncJobStatus.COMPLETED:
            repository.update_jobs_status([job])
        records = list(repository.fetch_records(job))
        print("yay!!")
        print(records)


