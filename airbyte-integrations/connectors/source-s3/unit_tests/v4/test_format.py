from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat

def test_csv_format_tab_delimited():
    assert CsvFormat(delimiter=r"\t").delimiter == '\\t'
