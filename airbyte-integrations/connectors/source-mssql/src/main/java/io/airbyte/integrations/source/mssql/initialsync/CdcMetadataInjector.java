/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.initialsync;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.source.mssql.MssqlCdcConnectorMetadataInjector;
import io.airbyte.integrations.source.mssql.cdc.MssqlDebeziumStateUtil.MssqlDebeziumStateAttributes;

public class CdcMetadataInjector {

  private final String transactionTimestamp;
  private final MssqlDebeziumStateAttributes stateAttributes;
  private final MssqlCdcConnectorMetadataInjector metadataInjector;

  public CdcMetadataInjector(final String transactionTimestamp,
                             final MssqlDebeziumStateAttributes stateAttributes,
                             final MssqlCdcConnectorMetadataInjector metadataInjector) {
    this.transactionTimestamp = transactionTimestamp;
    this.stateAttributes = stateAttributes;
    this.metadataInjector = metadataInjector;
  }

  public void inject(final ObjectNode record) {
    metadataInjector.addMetaDataToRowsFetchedOutsideDebezium(record, transactionTimestamp, stateAttributes);
  }

}
