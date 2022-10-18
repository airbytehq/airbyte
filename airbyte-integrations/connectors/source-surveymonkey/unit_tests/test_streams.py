#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pendulum
import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_surveymonkey.streams import SurveyIds, SurveyPages, SurveyQuestions, SurveyResponses, Surveys

args_mock = {"authenticator": NoAuth(), "start_date": pendulum.parse("2000-01-01"), "survey_ids": []}

records_survey_ids = [
    {
        "id": "307785415",
        "title": "b9jo5h23l7pa",
        "nickname": "qhs5vg2qi0o4arsjiwy2ay00n82n",
        "href": "https://api.surveymonkey.com/v3/surveys/307785415",
    },
    {
        "id": "307785388",
        "title": "igpfp2yfsw90df6nxbsb49v",
        "nickname": "h23gl22ulmfsyt4q7xt",
        "href": "https://api.surveymonkey.com/v3/surveys/307785388",
    },
]

response_survey_ids = {
    "data": records_survey_ids,
    "per_page": 50,
    "page": 1,
    "total": 2,
    "links": {"self": "https://api.surveymonkey.com/v3/surveys?per_page=50&page=1"},
}


def test_survey_ids(requests_mock):
    requests_mock.get("https://api.surveymonkey.com/v3/surveys", json=response_survey_ids)
    stream = SurveyIds(**args_mock)
    records = stream.read_records(sync_mode=SyncMode.full_refresh)
    assert list(records) == records_survey_ids


def test_user_defined_retry(requests_mock):
    requests_mock.get(
        "https://api.surveymonkey.com/v3/surveys",
        [
            {
                "status_code": 429,
                "headers": {"X-Ratelimit-App-Global-Minute-Remaining": "0"},
                "json": {
                    "error": {
                        "id": 1040,
                        "name": "Rate limit reached",
                        "docs": "https://developer.surveymonkey.com/api/v3/#error-codes",
                        "message": "Too many requests were made, try again later.",
                        "http_status_code": 429,
                    }
                },
            },
            {"status_code": 200, "headers": {"X-Ratelimit-App-Global-Minute-Remaining": "100"}, "json": response_survey_ids},
        ],
    )

    stream = SurveyIds(**args_mock)
    stream.default_backoff_time = 3
    records = stream.read_records(sync_mode=SyncMode.full_refresh)
    assert list(records) == records_survey_ids


def test_slices_from_survey_ids(requests_mock):
    requests_mock.get("https://api.surveymonkey.com/v3/surveys", json=response_survey_ids)
    stream_slices = Surveys(**args_mock).stream_slices()
    assert list(stream_slices) == [{"survey_id": "307785415"}, {"survey_id": "307785388"}]


def test_slices_from_config(requests_mock):
    args = {**args_mock, **{"survey_ids": ["307785415"]}}
    stream_slices = Surveys(**args).stream_slices()
    assert list(stream_slices) == [{"survey_id": "307785415"}]


response_survey_details = {
    "title": "b9jo5h23l7pa",
    "nickname": "qhs5vg2qi0o4arsjiwy2ay00n82n",
    "language": "ru",
    "folder_id": "0",
    "category": "",
    "question_count": 10,
    "page_count": 3,
    "response_count": 20,
    "date_created": "2021-06-09T21:20:00",
    "date_modified": "2021-06-10T11:07:00",
    "id": "307785415",
    "buttons_text": {"next_button": "Nex >>>>>", "prev_button": "Nix <<<<<", "done_button": "Nax_Don_Gon!", "exit_button": ""},
    "is_owner": True,
    "footer": True,
    "theme_id": "4510354",
    "custom_variables": {},
    "href": "https://api.surveymonkey.com/v3/surveys/307785415",
    "analyze_url": "https://www.surveymonkey.com/analyze/BPAkhAawaMN8C17tmmNFxjZ0KOiJJ3FCQU4krShVQhg_3D",
    "edit_url": "https://www.surveymonkey.com/create/?sm=BPAkhAawaMN8C17tmmNFxjZ0KOiJJ3FCQU4krShVQhg_3D",
    "collect_url": "https://www.surveymonkey.com/collect/list?sm=BPAkhAawaMN8C17tmmNFxjZ0KOiJJ3FCQU4krShVQhg_3D",
    "summary_url": "https://www.surveymonkey.com/summary/BPAkhAawaMN8C17tmmNFxjZ0KOiJJ3FCQU4krShVQhg_3D",
    "preview": "https://www.surveymonkey.com/r/Preview/?sm=YVdtL_2BP5oiGTrfksyofvENkBr7v87Xfh8hbcJr8rbqgesWvwJjz5N1F7pCSRcDoy",
    "pages": [
        {
            "title": "",
            "description": "",
            "position": 1,
            "question_count": 0,
            "id": "168831392",
            "href": "https://api.surveymonkey.com/v3/surveys/307785415/pages/168831392",
            "questions": [],
        },
        {
            "title": "p71uerk2uh7k5",
            "description": "92cb9d98j15jmfo",
            "position": 2,
            "question_count": 2,
            "id": "168831393",
            "href": "https://api.surveymonkey.com/v3/surveys/307785415/pages/168831393",
            "questions": [
                {
                    "id": "667461690",
                    "position": 1,
                    "visible": True,
                    "family": "single_choice",
                    "subtype": "vertical",
                    "layout": None,
                    "sorting": None,
                    "required": None,
                    "validation": None,
                    "forced_ranking": False,
                    "headings": [{"heading": "53o3ibly at73qjs4e4 y9dug7jxfmpmr 8esacb5"}],
                    "href": "https://api.surveymonkey.com/v3/surveys/307785415/pages/168831393/questions/667461690",
                    "answers": {
                        "choices": [
                            {
                                "position": 1,
                                "visible": True,
                                "text": "lg2mcft4e64 ywiatkmeo ci3rr4l2v0 ot6un49a 4b28sq4g8qv7tj 4ihpko73bp0k6lf swaeo3o4mg2jf5g rnh225wj520w1ps p9emk1wg64vwl",
                                "quiz_options": {"score": 0},
                                "id": "4385174700",
                            },
                            {
                                "position": 2,
                                "visible": True,
                                "text": "ywg8bovna adsahna5kd1jg vdism1 w045ovutkx9 oubne2u vd0x7lh3 y3npa4kfb5",
                                "quiz_options": {"score": 0},
                                "id": "4385174701",
                            },
                        ]
                    },
                },
                {
                    "id": "667461777",
                    "position": 2,
                    "visible": True,
                    "family": "single_choice",
                    "subtype": "menu",
                    "layout": None,
                    "sorting": None,
                    "required": None,
                    "validation": None,
                    "forced_ranking": False,
                    "headings": [{"heading": "kjqdk eo7hfnu or7bmd1iwqxxp sguqta4f8141iy"}],
                    "href": "https://api.surveymonkey.com/v3/surveys/307785415/pages/168831393/questions/667461777",
                    "answers": {
                        "choices": [
                            {
                                "position": 1,
                                "visible": True,
                                "text": "11bp1ll11nu0 ool67 tkbke01j3mtq 22f4r54u073p h6kt4puolum4",
                                "quiz_options": {"score": 0},
                                "id": "4385174970",
                            },
                            {
                                "position": 2,
                                "visible": True,
                                "text": "8q53omsxw8 08yyjvj3ns9j yu7yap87 d2tgjv55j5d5o3y dbd69m94qav1wma 8upqf7cliu hb26pytfkwyt rfo2ac4",
                                "quiz_options": {"score": 0},
                                "id": "4385174971",
                            },
                        ]
                    },
                },
            ],
        },
    ],
}


def test_surveys(requests_mock):
    requests_mock.get("https://api.surveymonkey.com/v3/surveys/307785415/details", json=response_survey_details)
    args = {**args_mock, **{"survey_ids": ["307785415"]}}
    records = Surveys(**args).read_records(sync_mode=SyncMode.full_refresh, stream_slice={"survey_id": "307785415"})
    assert list(records) == [
        {
            "analyze_url": "https://www.surveymonkey.com/analyze/BPAkhAawaMN8C17tmmNFxjZ0KOiJJ3FCQU4krShVQhg_3D",
            "buttons_text": {"done_button": "Nax_Don_Gon!", "exit_button": "", "next_button": "Nex >>>>>", "prev_button": "Nix <<<<<"},
            "category": "",
            "collect_url": "https://www.surveymonkey.com/collect/list?sm=BPAkhAawaMN8C17tmmNFxjZ0KOiJJ3FCQU4krShVQhg_3D",
            "custom_variables": {},
            "date_created": "2021-06-09T21:20:00",
            "date_modified": "2021-06-10T11:07:00",
            "edit_url": "https://www.surveymonkey.com/create/?sm=BPAkhAawaMN8C17tmmNFxjZ0KOiJJ3FCQU4krShVQhg_3D",
            "folder_id": "0",
            "footer": True,
            "href": "https://api.surveymonkey.com/v3/surveys/307785415",
            "id": "307785415",
            "is_owner": True,
            "language": "ru",
            "nickname": "qhs5vg2qi0o4arsjiwy2ay00n82n",
            "page_count": 3,
            "preview": "https://www.surveymonkey.com/r/Preview/?sm=YVdtL_2BP5oiGTrfksyofvENkBr7v87Xfh8hbcJr8rbqgesWvwJjz5N1F7pCSRcDoy",
            "question_count": 10,
            "response_count": 20,
            "summary_url": "https://www.surveymonkey.com/summary/BPAkhAawaMN8C17tmmNFxjZ0KOiJJ3FCQU4krShVQhg_3D",
            "theme_id": "4510354",
            "title": "b9jo5h23l7pa",
        }
    ]


def test_survey_pages(requests_mock):
    requests_mock.get("https://api.surveymonkey.com/v3/surveys/307785415/details", json=response_survey_details)
    args = {**args_mock, **{"survey_ids": ["307785415"]}}
    records = SurveyPages(**args).read_records(sync_mode=SyncMode.full_refresh, stream_slice={"survey_id": "307785415"})
    assert list(records) == [
        {
            "description": "",
            "href": "https://api.surveymonkey.com/v3/surveys/307785415/pages/168831392",
            "id": "168831392",
            "position": 1,
            "question_count": 0,
            "title": "",
        },
        {
            "description": "92cb9d98j15jmfo",
            "href": "https://api.surveymonkey.com/v3/surveys/307785415/pages/168831393",
            "id": "168831393",
            "position": 2,
            "question_count": 2,
            "title": "p71uerk2uh7k5",
        },
    ]


def test_survey_questions(requests_mock):
    requests_mock.get("https://api.surveymonkey.com/v3/surveys/307785415/details", json=response_survey_details)
    args = {**args_mock, **{"survey_ids": ["307785415"]}}
    records = SurveyQuestions(**args).read_records(sync_mode=SyncMode.full_refresh, stream_slice={"survey_id": "307785415"})
    assert list(records) == [
        {
            "answers": {
                "choices": [
                    {
                        "id": "4385174700",
                        "position": 1,
                        "quiz_options": {"score": 0},
                        "text": "lg2mcft4e64 ywiatkmeo ci3rr4l2v0 ot6un49a "
                        "4b28sq4g8qv7tj 4ihpko73bp0k6lf "
                        "swaeo3o4mg2jf5g rnh225wj520w1ps "
                        "p9emk1wg64vwl",
                        "visible": True,
                    },
                    {
                        "id": "4385174701",
                        "position": 2,
                        "quiz_options": {"score": 0},
                        "text": "ywg8bovna adsahna5kd1jg vdism1 w045ovutkx9 " "oubne2u vd0x7lh3 y3npa4kfb5",
                        "visible": True,
                    },
                ]
            },
            "family": "single_choice",
            "forced_ranking": False,
            "headings": [{"heading": "53o3ibly at73qjs4e4 y9dug7jxfmpmr 8esacb5"}],
            "href": "https://api.surveymonkey.com/v3/surveys/307785415/pages/168831393/questions/667461690",
            "id": "667461690",
            "layout": None,
            "page_id": "168831393",
            "position": 1,
            "required": None,
            "sorting": None,
            "subtype": "vertical",
            "validation": None,
            "visible": True,
        },
        {
            "answers": {
                "choices": [
                    {
                        "id": "4385174970",
                        "position": 1,
                        "quiz_options": {"score": 0},
                        "text": "11bp1ll11nu0 ool67 tkbke01j3mtq " "22f4r54u073p h6kt4puolum4",
                        "visible": True,
                    },
                    {
                        "id": "4385174971",
                        "position": 2,
                        "quiz_options": {"score": 0},
                        "text": "8q53omsxw8 08yyjvj3ns9j yu7yap87 " "d2tgjv55j5d5o3y dbd69m94qav1wma 8upqf7cliu " "hb26pytfkwyt rfo2ac4",
                        "visible": True,
                    },
                ]
            },
            "family": "single_choice",
            "forced_ranking": False,
            "headings": [{"heading": "kjqdk eo7hfnu or7bmd1iwqxxp sguqta4f8141iy"}],
            "href": "https://api.surveymonkey.com/v3/surveys/307785415/pages/168831393/questions/667461777",
            "id": "667461777",
            "layout": None,
            "page_id": "168831393",
            "position": 2,
            "required": None,
            "sorting": None,
            "subtype": "menu",
            "validation": None,
            "visible": True,
        },
    ]


def test_surveys_next_page_token():
    args = {**args_mock, **{"survey_ids": ["307785415"]}}
    stream = SurveyIds(**args)

    mockresponse = Mock()
    mockresponse.json.return_value = {
        "links": {
            "self": "https://api.surveymonkey.com/v3/surveys?page=1&per_page=50",
            "next": "https://api.surveymonkey.com/v3/surveys?page=2&per_page=50",
            "last": "https://api.surveymonkey.com/v3/surveys?page=5&per_page=50",
        }
    }

    params = stream.next_page_token(mockresponse)
    assert params == {"page": "2", "per_page": "50"}


@pytest.mark.parametrize(
    "current_stream_state,latest_record,state",
    [
        (
            {"307785415": {"date_modified": "2021-01-01T00:00:00+00:00"}},
            {"survey_id": "307785415", "date_modified": "2021-12-01T00:00:00+00:00"},
            {"307785415": {"date_modified": "2021-12-01T00:00:01+00:00"}},
        ),
        (
            {},
            {"survey_id": "307785415", "date_modified": "2021-12-01T00:00:00+00:00"},
            {"307785415": {"date_modified": "2021-12-01T00:00:01+00:00"}},
        ),
        (
            {"307785415": {"date_modified": "2021-01-01T00:00:00+00:00"}},
            {"survey_id": "307785415"},
            {"307785415": {"date_modified": "2021-01-01T00:00:00+00:00"}},
        ),
    ],
)
def test_surveys_responses_get_updated_state(current_stream_state, latest_record, state):
    args = {**args_mock, **{"survey_ids": ["307785415"]}}
    stream = SurveyResponses(**args)
    actual_state = stream.get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record)
    assert actual_state == state


@pytest.mark.parametrize(
    "stream_state,params",
    [
        (
            {"307785415": {"date_modified": "2021-01-01T00:00:00+00:00"}},
            {"start_modified_at": "2021-01-01T00:00:00"},
        ),
        (
            {},
            {"start_modified_at": "2000-01-01T00:00:00"},  # return start_date
        ),
    ],
)
def test_surveys_responses_request_params(stream_state, params):
    args = {**args_mock, **{"survey_ids": ["307785415"]}}
    stream = SurveyResponses(**args)
    actual_params = stream.request_params(stream_state=stream_state, stream_slice={"survey_id": "307785415"})
    assert actual_params == params
