/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
   * https://debezium.io/documentation/reference/1.4/connectors/mysql.html#mysql-create-events
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
   *        https://debezium.io/documentation/reference/1.4/connectors/mysql.html#mysql-create-events
   */
  String namespace(JsonNode source);

}
