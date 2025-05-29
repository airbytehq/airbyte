/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.initialsync;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.source.mysql.cdc.MySqlCdcConnectorMetadataInjector;
import io.airbyte.integrations.source.mysql.cdc.MySqlDebeziumStateUtil.MysqlDebeziumStateAttributes;

public class CdcMetadataInjector {

  private final String transactionTimestamp;
  private final MysqlDebeziumStateAttributes stateAttributes;
  private final MySqlCdcConnectorMetadataInjector metadataInjector;

  public CdcMetadataInjector(final String transactionTimestamp,
                             final MysqlDebeziumStateAttributes stateAttributes,
                             final MySqlCdcConnectorMetadataInjector metadataInjector) {
    this.transactionTimestamp = transactionTimestamp;
    this.stateAttributes = stateAttributes;
    this.metadataInjector = metadataInjector;
  }

  public void inject(final ObjectNode record) {
    metadataInjector.addMetaDataToRowsFetchedOutsideDebezium(record, transactionTimestamp, stateAttributes);
  }

}
