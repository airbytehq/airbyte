#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

from airbyte_protocol_dataclasses.models import ConfiguredAirbyteStream, DestinationSyncMode
from pytest import fixture
from source_exact import SourceExact
from source_exact.streams import (
    SyncProjectProjects, PayrollActiveEmployments, HRMDepartments, SyncPayrollEmployments, ProjectInvoiceTerms,
    SyncSalesInvoiceSalesInvoices
)

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


HERE = Path(__file__).parent


@fixture
def config():
    with open(HERE.parent / "secrets/config.json", "r") as file:
        return json.loads(file.read())


@fixture
def configured_catalog(config):
    crmac_stream = SyncProjectProjects(config).as_airbyte_stream()
    crmac_configured = ConfiguredAirbyteStream(
        stream=crmac_stream, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.overwrite
    )

    return ConfiguredAirbyteCatalog(streams=[crmac_configured])


def test_read_sync_project_projects(config, configured_catalog):
    source = SourceExact()
    output: EntrypointOutput = read(source, config, configured_catalog)

    assert len(output.records) > 0

def test_payroll_active_employments(config):
    stream = PayrollActiveEmployments(config).as_airbyte_stream()
    stream_configured = ConfiguredAirbyteStream(stream=stream, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.overwrite)
    configured_catalog = ConfiguredAirbyteCatalog(streams=[stream_configured])
    source = SourceExact()
    output: EntrypointOutput = read(source, config, configured_catalog)

    assert len(output.records) >= 0

def test_departments(config):
    stream = HRMDepartments(config).as_airbyte_stream()
    stream_configured = ConfiguredAirbyteStream(stream=stream, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.overwrite)
    configured_catalog = ConfiguredAirbyteCatalog(streams=[stream_configured])
    source = SourceExact()
    output: EntrypointOutput = read(source, config, configured_catalog)

    assert len(output.records) >= 0

def test_payroll_employments(config):
    stream = SyncPayrollEmployments(config).as_airbyte_stream()
    stream_configured = ConfiguredAirbyteStream(stream=stream,sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.overwrite)
    configured_catalog = ConfiguredAirbyteCatalog(streams=[stream_configured])
    source = SourceExact()
    output: EntrypointOutput = read(source, config, configured_catalog)

    assert len(output.records) >= 0

def test_invoice_terms(config):
    stream = ProjectInvoiceTerms(config).as_airbyte_stream()
    stream_configured = ConfiguredAirbyteStream(stream=stream, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.overwrite)
    configured_catalog = ConfiguredAirbyteCatalog(streams=[stream_configured])
    source = SourceExact()
    output: EntrypointOutput = read(source, config, configured_catalog)

    assert len(output.records) >= 0

def test_sales_invoice(config):
    stream = SyncSalesInvoiceSalesInvoices(config).as_airbyte_stream()
    stream_configured = ConfiguredAirbyteStream(stream=stream, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.overwrite)
    configured_catalog = ConfiguredAirbyteCatalog(streams=[stream_configured])
    source = SourceExact()
    output: EntrypointOutput = read(source, config, configured_catalog)

    assert len(output.records) >= 0
