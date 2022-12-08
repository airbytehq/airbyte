/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

/**
 * This interface is used to add metadata to the records fetched from the database. For instance, in
 * Postgres we add the lsn to the records. In MySql we add the file name and position to the
 * records.
 */
public interface CdcMetadataInjector {

  /**
   * A debezium record contains multiple pieces. Ref :
   * https://debezium.io/documentation/reference/1.9/connectors/mysql.html#mysql-create-events
   *
   * @param event is the actual record which contains data and would be written to the destination
   * @param source contains the metadata about the record and we need to extract that metadata and add
   *        it to the event before writing it to destination
   */
  void addMetaData(ObjectNode event, JsonNode source);

  /**
   * As part of Airbyte record we need to add the namespace (schema name)
   *
   * @param source part of debezium record and contains the metadata about the record. We need to
   *        extract namespace out of this metadata and return Ref :
   *        https://debezium.io/documentation/reference/1.9/connectors/mysql.html#mysql-create-events
   */
  String namespace(JsonNode source);

}
