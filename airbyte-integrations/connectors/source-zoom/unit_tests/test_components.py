#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from components import parse_vtt_content


@pytest.mark.parametrize(
    "vtt_input, expected",
    [
        pytest.param(
            (
                "WEBVTT\n"
                "\n"
                "1\n"
                "00:00:05.000 --> 00:00:08.500\n"
                "Ryan Waskewich: Hello, this is a test recording.\n"
                "\n"
                "2\n"
                "00:00:09.000 --> 00:00:12.000\n"
                "John Doe: Thanks for joining.\n"
            ),
            [
                {
                    "sequence_number": 1,
                    "timestamp_start": "00:00:05.000",
                    "timestamp_end": "00:00:08.500",
                    "speaker": "Ryan Waskewich",
                    "text": "Hello, this is a test recording.",
                },
                {
                    "sequence_number": 2,
                    "timestamp_start": "00:00:09.000",
                    "timestamp_end": "00:00:12.000",
                    "speaker": "John Doe",
                    "text": "Thanks for joining.",
                },
            ],
            id="standard_with_speakers",
        ),
        pytest.param(
            ("WEBVTT\n\n1\n00:00:05.000 --> 00:00:08.500\nThis line has no speaker attribution.\n"),
            [
                {
                    "sequence_number": 1,
                    "timestamp_start": "00:00:05.000",
                    "timestamp_end": "00:00:08.500",
                    "speaker": None,
                    "text": "This line has no speaker attribution.",
                },
            ],
            id="no_speaker",
        ),
        pytest.param(
            ("WEBVTT\n\n1\n00:00:05.000 --> 00:00:08.500\nAlice: First line of text\ncontinues on the next line.\n"),
            [
                {
                    "sequence_number": 1,
                    "timestamp_start": "00:00:05.000",
                    "timestamp_end": "00:00:08.500",
                    "speaker": "Alice",
                    "text": "First line of text continues on the next line.",
                },
            ],
            id="multiline_cue_text",
        ),
        pytest.param(
            ("WEBVTT\r\n\r\n1\r\n00:00:01,500 --> 00:00:04,000\r\nBob: Windows line endings with comma timestamps.\r\n"),
            [
                {
                    "sequence_number": 1,
                    "timestamp_start": "00:00:01.500",
                    "timestamp_end": "00:00:04.000",
                    "speaker": "Bob",
                    "text": "Windows line endings with comma timestamps.",
                },
            ],
            id="windows_line_endings_comma_timestamps",
        ),
        pytest.param(
            "WEBVTT\n",
            [],
            id="header_only_empty",
        ),
        pytest.param(
            "",
            [],
            id="empty_string",
        ),
        pytest.param(
            (
                "WEBVTT\n"
                "\n"
                "1\n"
                "This block has no timestamp line\n"
                "so it should be skipped entirely.\n"
                "\n"
                "2\n"
                "00:00:01.000 --> 00:00:02.000\n"
                "Valid cue after malformed block.\n"
            ),
            [
                {
                    "sequence_number": 1,
                    "timestamp_start": "00:00:01.000",
                    "timestamp_end": "00:00:02.000",
                    "speaker": None,
                    "text": "Valid cue after malformed block.",
                },
            ],
            id="malformed_block_skipped",
        ),
        pytest.param(
            (
                "WEBVTT\n"
                "\n"
                "1\n"
                "00:00:01.000 --> 00:00:03.000\n"
                "First cue.\n"
                "\n"
                "2\n"
                "00:00:04.000 --> 00:00:06.000\n"
                "Second cue.\n"
                "\n"
                "3\n"
                "00:00:07.000 --> 00:00:09.000\n"
                "Third cue.\n"
            ),
            [
                {
                    "sequence_number": 1,
                    "timestamp_start": "00:00:01.000",
                    "timestamp_end": "00:00:03.000",
                    "speaker": None,
                    "text": "First cue.",
                },
                {
                    "sequence_number": 2,
                    "timestamp_start": "00:00:04.000",
                    "timestamp_end": "00:00:06.000",
                    "speaker": None,
                    "text": "Second cue.",
                },
                {
                    "sequence_number": 3,
                    "timestamp_start": "00:00:07.000",
                    "timestamp_end": "00:00:09.000",
                    "speaker": None,
                    "text": "Third cue.",
                },
            ],
            id="sequence_numbers_increment",
        ),
        pytest.param(
            ("WEBVTT\n\n1\n00:00:01.000 --> 00:00:03.000\nhttps://example.com: this looks like a speaker but the name is a URL\n"),
            [
                {
                    "sequence_number": 1,
                    "timestamp_start": "00:00:01.000",
                    "timestamp_end": "00:00:03.000",
                    "speaker": "https",
                    "text": "//example.com: this looks like a speaker but the name is a URL",
                },
            ],
            id="url_like_colon_splits_on_first_colon_known_limitation",
        ),
    ],
)
def test_parse_vtt_content(vtt_input, expected):
    result = parse_vtt_content(vtt_input)
    assert result == expected
