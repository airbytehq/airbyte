import pytest
from faker import Faker


def simulate_input_stream(num_records, num_streams):
    """
    Simulate an input stream with Faker-generated data.
    """
    fake = Faker()
    for _ in range(num_records):
        for stream in range(num_streams):
            yield orjson.dumps(
                {
                    "stream_name": f"stream_{stream}",
                    "name": fake.name(),
                    "address": fake.address(),
                }
            ).decode() + "\n"


# @pytest.mark.parametrize(
#     "num_records, num_streams, expected_batches",
#     [
#         (1000, 2, 2),  # 1000 records, 2 streams, expecting 2 batches (500 each)
#         (1500, 3, 3),  # 1500 records, 3 streams, expecting 3 batches
#     ],
# )
# def test_parse_input_stream(num_records, num_streams, expected_batches):
#     input_stream = simulate_input_stream(num_records, num_streams)
#     summaries = parse_input_stream(input_stream)

#     assert len(summaries) == expected_batches
#     for summary in summaries:
#         assert summary["num_records"] <= 500  # Batch size limit
#         assert summary["stream_name"].startswith("stream_")
