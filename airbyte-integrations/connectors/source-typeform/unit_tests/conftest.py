#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture
def config():
    return {"start_date": "2020-01-01T00:00:00Z", "token": "7607999ef26581e81726777b7b79f20e70e75602", "form_ids": ["u6nXL7", "k9xNV4"]}


@pytest.fixture
def config_without_forms():
    return {"start_date": "2020-01-01T00:00:00Z", "token": "7607999ef26581e81726777b7b79f20e70e75602"}


@pytest.fixture
def form_response():
    return setup_response(
        200,
        {
            "id": "id",
            "title": "title",
            "language": "en",
            "fields": [{}],
            "hidden": ["string"],
            "variables": {"score": 0, "price": 0},
            "welcome_screens": [
                {
                    "ref": "nice-readable-welcome-ref",
                    "title": "Welcome Title",
                    "properties": {"description": "Cool description for the welcome", "show_button": True, "button_text": "start"},
                    "attachment": {
                        "type": "image",
                        "href": {
                            "image": {"value": "https://images.typeform.com/images/4bcd3"},
                            "Pexels": {"value": "https://www.pexels.com/video/people-traveling-in-the-desert-1739011"},
                            "Vimeo": {"value": "https://vimeo.com/245714980"},
                            "YouTube": {"value": "https://www.youtube.com/watch?v=cGk3tZIIpXE"},
                        },
                        "scale": 0,
                        "properties": {"description": "description"},
                    },
                    "layout": {
                        "type": "float",
                        "placement": "left",
                        "attachment": {
                            "type": "image",
                            "href": {
                                "image": {"value": "https://images.typeform.com/images/4bcd3"},
                                "Pexels": {"value": "https://www.pexels.com/video/people-traveling-in-the-desert-1739011"},
                                "Vimeo": {"value": "https://vimeo.com/245714980"},
                                "YouTube": {"value": "https://www.youtube.com/watch?v=cGk3tZIIpXE"},
                            },
                            "scale": 0,
                            "properties": {"brightness": 0, "description": "description", "focal_point": {"x": 0, "y": 0}},
                        },
                    },
                }
            ],
            "thankyou_screens": [
                {
                    "ref": "nice-readable-thank-you-ref",
                    "title": "Thank you Title",
                    "properties": {
                        "show_button": True,
                        "button_text": "start",
                        "button_mode": "redirect",
                        "redirect_url": "https://www.typeform.com",
                        "share_icons": True,
                    },
                    "attachment": {
                        "type": "image",
                        "href": {
                            "image": {"value": "https://images.typeform.com/images/4bcd3"},
                            "Pexels": {"value": "https://www.pexels.com/video/people-traveling-in-the-desert-1739011"},
                            "Vimeo": {"value": "https://vimeo.com/245714980"},
                            "YouTube": {"value": "https://www.youtube.com/watch?v=cGk3tZIIpXE"},
                        },
                        "scale": 0,
                        "properties": {"description": "description"},
                    },
                    "layout": {
                        "type": "float",
                        "placement": "left",
                        "attachment": {
                            "type": "image",
                            "href": {
                                "image": {"value": "https://images.typeform.com/images/4bcd3"},
                                "Pexels": {"value": "https://www.pexels.com/video/people-traveling-in-the-desert-1739011"},
                                "Vimeo": {"value": "https://vimeo.com/245714980"},
                                "YouTube": {"value": "https://www.youtube.com/watch?v=cGk3tZIIpXE"},
                            },
                            "scale": 0,
                            "properties": {"brightness": 0, "description": "description", "focal_point": {"x": 0, "y": 0}},
                        },
                    },
                }
            ],
            "logic": [
                {
                    "type": "type",
                    "ref": "ref",
                    "actions": [
                        {
                            "action": "action",
                            "details": {
                                "to": {"type": "type", "value": "value"},
                                "target": {"type": "type", "value": "value"},
                                "value": {"type": "type", "value": 0},
                            },
                            "condition": {"op": "op", "vars": [{"type": "type", "value": {}}]},
                        }
                    ],
                }
            ],
            "theme": {"href": "https://api.typeform.com/themes/Fs24as"},
            "workspace": {"href": "https://api.typeform.com/workspaces/Aw33bz"},
            "_links": {"display": "https://subdomain.typeform.com/to/abc123"},
            "settings": {
                "language": "language",
                "is_public": True,
                "progress_bar": "proportion",
                "show_progress_bar": True,
                "show_typeform_branding": True,
                "show_time_to_complete": True,
                "hide_navigation": True,
                "meta": {"title": "title", "allow_indexing": True, "description": "description", "image": {"href": "href"}},
                "redirect_after_submit_url": "redirect_after_submit_url",
                "google_analytics": "google_analytics",
                "facebook_pixel": "facebook_pixel",
                "google_tag_manager": "google_tag_manager",
            },
            "cui_settings": {
                "avatar": "https://images.typeform.com/images/4bcd3",
                "is_typing_emulation_disabled": True,
                "typing_emulation_speed": "fast",
            },
        },
    )


@pytest.fixture
def forms_response():
    return setup_response(200, {"total_items": 2, "page_count": 1, "items": [{"id": "u6nXL7"}, {"id": "k9xNV4"}]})


@pytest.fixture
def response_response():
    return setup_response(
        200,
        {
            "items": [
                {
                    "answers": [
                        {
                            "field": {"id": "hVONkQcnSNRj", "ref": "my_custom_dropdown_reference", "type": "dropdown"},
                            "text": "Job opportunities",
                            "type": "text",
                        },
                        {
                            "boolean": False,
                            "field": {"id": "RUqkXSeXBXSd", "ref": "my_custom_yes_no_reference", "type": "yes_no"},
                            "type": "boolean",
                        },
                        {
                            "boolean": True,
                            "field": {"id": "gFFf3xAkJKsr", "ref": "my_custom_legal_reference", "type": "legal"},
                            "type": "boolean",
                        },
                        {
                            "field": {"id": "JwWggjAKtOkA", "ref": "my_custom_short_text_reference", "type": "short_text"},
                            "text": "Lian",
                            "type": "text",
                        },
                        {
                            "email": "lian1078@other.com",
                            "field": {"id": "SMEUb7VJz92Q", "ref": "my_custom_email_reference", "type": "email"},
                            "type": "email",
                        },
                        {
                            "field": {"id": "pn48RmPazVdM", "ref": "my_custom_number_reference", "type": "number"},
                            "number": 1,
                            "type": "number",
                        },
                        {
                            "field": {"id": "Q7M2XAwY04dW", "ref": "my_custom_number2_reference", "type": "number"},
                            "number": 1,
                            "type": "number",
                        },
                        {
                            "field": {"id": "WOTdC00F8A3h", "ref": "my_custom_rating_reference", "type": "rating"},
                            "number": 3,
                            "type": "number",
                        },
                        {
                            "field": {"id": "DlXFaesGBpoF", "ref": "my_custom_long_text_reference", "type": "long_text"},
                            "text": "It's a big, busy city. I moved here for a job, but I like it, so I am planning to stay. I have made good friends here.",
                            "type": "text",
                        },
                        {
                            "field": {"id": "NRsxU591jIW9", "ref": "my_custom_opinion_scale_reference", "type": "opinion_scale"},
                            "number": 1,
                            "type": "number",
                        },
                        {
                            "choices": {"labels": ["New York", "Tokyo"]},
                            "field": {"id": "PNe8ZKBK8C2Q", "ref": "my_custom_picture_choice_reference", "type": "picture_choice"},
                            "type": "choices",
                        },
                        {
                            "date": "2012-03-20T00:00:00Z",
                            "field": {"id": "KoJxDM3c6x8h", "ref": "my_custom_date_reference", "type": "date"},
                            "type": "date",
                        },
                        {
                            "choice": {"label": "A friend's experience in Sydney"},
                            "field": {"id": "ceIXxpbP3t2q", "ref": "my_custom_multiple_choice_reference", "type": "multiple_choice"},
                            "type": "choice",
                        },
                        {
                            "choices": {"labels": ["New York", "Tokyo"]},
                            "field": {"id": "abISxvbD5t1p", "ref": "my_custom_ranking_reference", "type": "ranking"},
                            "type": "choices",
                        },
                        {
                            "choice": {"label": "Tokyo"},
                            "field": {"id": "k6TP9oLGgHjl", "ref": "my_custom_multiple_choice2_reference", "type": "multiple_choice"},
                            "type": "choice",
                        },
                    ],
                    "calculated": {"score": 2},
                    "hidden": {},
                    "landed_at": "2017-09-14T22:33:59Z",
                    "landing_id": "21085286190ffad1248d17c4135ee56f",
                    "metadata": {
                        "browser": "default",
                        "network_id": "responsdent_network_id",
                        "platform": "other",
                        "referer": "https://user_id.typeform.com/to/lR6F4j",
                        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
                    },
                    "response_id": "21085286190ffad1248d17c4135ee56f",
                    "submitted_at": "2017-09-14T22:38:22Z",
                    "token": "test21085286190ffad1248d17c4135ee56f",
                    "variables": [{"key": "score", "number": 2, "type": "number"}, {"key": "name", "text": "typeform", "type": "text"}],
                },
                {
                    "answers": [
                        {
                            "choice": {"label": "New York"},
                            "field": {"id": "k6TP9oLGgHjl", "ref": "my_custom_multiple_choice2_reference", "type": "multiple_choice"},
                            "type": "choice",
                        },
                        {
                            "field": {"id": "X4BgU2f1K6tG", "ref": "my_custom_file_upload_reference", "type": "file_upload"},
                            "file_url": "https://api.typeform.com/forms/lT9Z2j/responses/7f46165474d11ee5836777d85df2cdab/fields/X4BgU2f1K6tG/files/afd8258fd453-aerial_view_rural_city_latvia_valmiera_urban_district_48132860.jpg",
                            "type": "file_url",
                        },
                        {
                            "choice": {"label": "Other"},
                            "field": {"id": "ceIXxpbP3t2q", "ref": "my_custom_multiple_choice_reference", "type": "multiple_choice"},
                            "type": "choice",
                        },
                        {
                            "field": {"id": "hVONkQcnSNRj", "ref": "my_custom_dropdown_reference", "type": "dropdown"},
                            "text": "Cost of living",
                            "type": "text",
                        },
                        {
                            "field": {"id": "JwWggjAKtOkA", "ref": "my_custom_short_text_reference", "type": "short_text"},
                            "text": "Sarah",
                            "type": "text",
                        },
                        {
                            "boolean": True,
                            "field": {"id": "RUqkXSeXBXSd", "ref": "my_custom_yes_no_reference", "type": "yes_no"},
                            "type": "boolean",
                        },
                        {
                            "field": {"id": "Fep7sEoBsnvC", "ref": "my_custom_long_text_reference", "type": "long_text"},
                            "text": "I read a magazine article about traveling to Sydney",
                            "type": "text",
                        },
                        {
                            "boolean": True,
                            "field": {"id": "gFFf3xAkJKsr", "ref": "my_custom_legal_reference", "type": "legal"},
                            "type": "boolean",
                        },
                        {
                            "field": {"id": "BFcpoPU5yJPM", "ref": "my_custom_short_text_reference", "type": "short_text"},
                            "text": "San Francisco",
                            "type": "text",
                        },
                        {
                            "email": "sarahbsmith@example.com",
                            "field": {"id": "SMEUb7VJz92Q", "ref": "my_custom_rmail_reference", "type": "email"},
                            "type": "email",
                        },
                        {
                            "field": {"id": "pn48RmPazVdM", "ref": "my_custom_number_reference", "type": "number"},
                            "number": 1,
                            "type": "number",
                        },
                        {
                            "field": {"id": "WOTdC00F8A3h", "ref": "my_custom_rating_reference", "type": "rating"},
                            "number": 3,
                            "type": "number",
                        },
                        {
                            "field": {"id": "Q7M2XAwY04dW", "ref": "my_custom_number2_reference", "type": "number"},
                            "number": 3,
                            "type": "number",
                        },
                        {
                            "field": {"id": "DlXFaesGBpoF", "ref": "my_custom_long_text_reference", "type": "long_text"},
                            "text": "It's a rural area. Very quiet. There are a lot of farms...farming is the major industry here.",
                            "type": "text",
                        },
                        {
                            "field": {"id": "NRsxU591jIW9", "ref": "my_custom_opinion_scale_reference", "type": "opinion_scale"},
                            "number": 1,
                            "type": "number",
                        },
                        {
                            "date": "2016-05-13T00:00:00Z",
                            "field": {"id": "KoJxDM3c6x8h", "ref": "my_custom_date_reference", "type": "date"},
                            "type": "date",
                        },
                        {
                            "choices": {"labels": ["London", "New York"]},
                            "field": {"id": "PNe8ZKBK8C2Q", "ref": "my_custom_picture_choice_reference", "type": "picture_choice"},
                            "type": "choices",
                        },
                    ],
                    "calculated": {"score": 4},
                    "hidden": {},
                    "landed_at": "2017-09-14T22:27:38Z",
                    "landing_id": "610fc266478b41e4927945e20fe54ad2",
                    "metadata": {
                        "browser": "default",
                        "network_id": "responsdent_network_id",
                        "platform": "other",
                        "referer": "https://user_id.typeform.com/to/lR6F4j",
                        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
                    },
                    "submitted_at": "2017-09-14T22:33:56Z",
                    "token": "test610fc266478b41e4927945e20fe54ad2",
                },
                {
                    "answers": [
                        {
                            "boolean": False,
                            "field": {"id": "RUqkXSeXBXSd", "ref": "my_custom_yes_no_reference", "type": "yes_no"},
                            "type": "boolean",
                        },
                        {
                            "boolean": False,
                            "field": {"id": "gFFf3xAkJKsr", "ref": "my_custom_legal_reference", "type": "legal"},
                            "type": "boolean",
                        },
                        {
                            "field": {"id": "JwWggjAKtOkA", "ref": "my_custom_short_text_reference", "type": "short_text"},
                            "text": "Paolo",
                            "type": "text",
                        },
                        {
                            "field": {"id": "pn48RmPazVdM", "ref": "my_custom_number_reference", "type": "number"},
                            "number": 5,
                            "type": "number",
                        },
                        {
                            "field": {"id": "Q7M2XAwY04dW", "ref": "my_custom_number2_reference", "type": "number"},
                            "number": 5,
                            "type": "number",
                        },
                        {
                            "choices": {"labels": ["Barcelona", "Sydney"]},
                            "field": {"id": "PNe8ZKBK8C2Q", "ref": "my_custom_picture_choice_reference", "type": "picture_choice"},
                            "type": "choices",
                        },
                        {
                            "field": {"id": "WOTdC00F8A3h", "ref": "my_custom_rating_reference", "type": "rating"},
                            "number": 5,
                            "type": "number",
                        },
                        {
                            "field": {"id": "DlXFaesGBpoF", "ref": "my_custom_long_text_reference", "type": "long_text"},
                            "text": "I live in a medium-sized European city. It's not too crowded, and the people are nice. I like the weather. It's also easy to travel to many beautiful and interesting vacation destinations from where I live.",
                            "type": "text",
                        },
                        {
                            "field": {"id": "NRsxU591jIW9", "ref": "my_custom_opinion_scale_reference", "type": "opinion_scale"},
                            "number": 4,
                            "type": "number",
                        },
                        {
                            "date": "1999-08-01T00:00:00Z",
                            "field": {"id": "KoJxDM3c6x8h", "ref": "my_custom_date_reference", "type": "date"},
                            "type": "date",
                        },
                        {
                            "choice": {"label": "Barcelona"},
                            "field": {"id": "k6TP9oLGgHjl", "ref": "my_custom_multiple_choice_reference", "type": "multiple_choice"},
                            "type": "choice",
                        },
                    ],
                    "calculated": {"score": 10},
                    "hidden": {},
                    "landed_at": "2017-09-14T22:24:49Z",
                    "landing_id": "9ba5db11ec6c63d22f08aade805bd363",
                    "metadata": {
                        "browser": "default",
                        "network_id": "responsdent_network_id",
                        "platform": "other",
                        "referer": "https://user_id.typeform.com/to/lR6F4j",
                        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_2_1 like Mac OS X) AppleWebKit/602.4.6 (KHTML, like Gecko) Version/10.0 Mobile/14D27 Safari/602.1",
                    },
                    "submitted_at": "2017-09-14T22:27:34Z",
                    "token": "9ba5db11ec6c63d22f08aade805bd363",
                },
                {
                    "answers": [],
                    "calculated": {"score": 0},
                    "hidden": {},
                    "landed_at": "2017-09-15T09:09:30Z",
                    "landing_id": "5fcb3f9c162e1fcdaadff4405b741080",
                    "metadata": {
                        "browser": "default",
                        "network_id": "responsdent_network_id",
                        "platform": "other",
                        "referer": "https://user_id.typeform.com/to/lR6F4j",
                        "user_agent": "Mozilla/5.0 (Linux; Android 4.1.2; GT-N7000 Build/JZO54K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Mobile Safari/537.36",
                    },
                    "submitted_at": "0001-01-01T00:00:00Z",
                    "token": "test5fcb3f9c162e1fcdaadff4405b741080",
                },
            ],
            "page_count": 1,
            "total_items": 4,
        },
    )


@pytest.fixture
def webhooks_response():
    return setup_response(
        200,
        {
            "items": [
                {
                    "created_at": "2016-11-21T12:23:28Z",
                    "enabled": True,
                    "form_id": "abc123",
                    "id": "yRtagDm8AT",
                    "tag": "phoenix",
                    "updated_at": "2016-11-21T12:23:28Z",
                    "url": "https://test.com",
                    "verify_ssl": True,
                }
            ]
        },
    )


@pytest.fixture
def images_response():
    return setup_response(
        200, [{"file_name": "file_name1", "id": "id1", "src": "src1"}, {"file_name": "file_name2", "id": "id2", "src": "src2"}]
    )


@pytest.fixture
def workspaces_response():
    return setup_response(
        200,
        {
            "items": [
                {
                    "forms": [{"count": 12, "href": "https://api.typeform.com/workspaces/a1b2c3/forms"}],
                    "id": "a1b2c3",
                    "name": "My Workspace1",
                    "self": [{"href": "https://api.typeform.com/workspaces/a1b2c3"}],
                    "shared": False,
                },
                {
                    "forms": [{"count": 10, "href": "https://api.typeform.com/workspaces/a1b2c3/forms"}],
                    "id": "a1b2c3d4",
                    "name": "My Workspace2",
                    "self": [{"href": "https://api.typeform.com/workspaces/a1b2c3"}],
                    "shared": True,
                },
            ],
            "page_count": 1,
            "total_items": 2,
        },
    )


@pytest.fixture
def themes_response():
    return setup_response(
        200,
        {
            "items": [
                {
                    "background": [{"brightness": 12, "href": "https://api.typeform.com/workspaces/a1b2c3/forms", "layout": "fullscreen"}],
                    "colors": [{"answer": "answer1", "background": "background1", "button": "button1", "question": "question1"}],
                    "fields": [{"alignment": "left", "font_size": "medium"}],
                    "font": "Helvetica Neue",
                    "has_transparent_button": True,
                    "id": "a1b2c3",
                    "name": "name1",
                    "screens": [{"alignment": "left", "font_size": "medium"}],
                    "visibility": "public",
                },
                {
                    "background": [{"brightness": 13, "href": "https://api.typeform.com/workspaces/a1b2c3/forms", "layout": "fullscreen"}],
                    "colors": [{"answer": "answer2", "background": "background2", "button": "button2", "question": "question2"}],
                    "fields": [{"alignment": "left", "font_size": "medium"}],
                    "font": "Helvetica Neue",
                    "has_transparent_button": True,
                    "id": "a1b2c3",
                    "name": "name1",
                    "screens": [{"alignment": "left", "font_size": "medium"}],
                    "visibility": "public",
                },
            ],
            "page_count": 1,
            "total_items": 2,
        },
    )


@pytest.fixture
def empty_response_ok():
    return setup_response(200, {})


@pytest.fixture
def empty_response_bad():
    return setup_response(400, {})


def setup_response(status, body):
    return [{"json": body, "status_code": status}]
