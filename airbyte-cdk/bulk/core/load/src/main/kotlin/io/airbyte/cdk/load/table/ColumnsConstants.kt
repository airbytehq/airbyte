/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.table

/**
 * CDC meta column names.
 *
 * Note: These CDC column names are brittle as they are separate yet coupled to the logic sources
 * use to generate these column names. See
 * [io.airbyte.integrations.source.mssql.MsSqlSourceOperations.MsSqlServerCdcMetaFields] for an
 * example.
 */
const val CDC_DELETED_AT_COLUMN = "_ab_cdc_deleted_at"
const val CDC_CURSOR_COLUMN = "_ab_cdc_cursor"
