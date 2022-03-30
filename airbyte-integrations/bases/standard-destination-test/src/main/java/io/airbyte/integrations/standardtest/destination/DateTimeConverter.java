/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

public interface DateTimeConverter {

  /**
   * Search dateTimeFieldNames inside data from @messages and converts to connector-specific date or
   * date-time format
   *
   * @param messages list with AirbyteMessage
   * @param dateTimeFieldNames map where key - path to the date/date-time field (e.g.
   *        /parentField/field), value - "date" or "date-time" depends on the format from catalog.
   */
  default void convertDateTimeFields(List<AirbyteMessage> messages, Map<String, String> dateTimeFieldNames) {
    for (AirbyteMessage message : messages) {
      if (message.getType() == Type.RECORD) {
        convertDateTime((ObjectNode) message.getRecord().getData(), dateTimeFieldNames);
      }
    }
  }

  /**
   * Search dateTimeFieldNames inside @data and converts to connector-specific date or date-time
   * format
   *
   * @param data from message record
   * @param dateTimeFieldNames map where key - path to the date/date-time field (e.g.
   *        /parentField/field), value - "date" or "date-time" depends on the format from catalog.
   */
  default void convertDateTime(ObjectNode data, Map<String, String> dateTimeFieldNames) {}

  /**
   * Override this method and return 'true' if destination connector requires conversion for
   * date/date-time fields for testSyncWithNormalization() method. Then override convertDateTime(..)
   * method to convert data to specific date-time format
   *
   * @return true - if destination connector requires conversion for date/date-time fields, false - in
   *         the other case.
   */
  default boolean requiresDateTimeConversionForNormalizedSync() {
    return false;
  }

  /**
   * Override this method and return 'true' if destination connector requires conversion for
   * date/date-time fields for testSync() method. Then override convertDateTime(..) method to convert
   * data to specific date-time format
   *
   * @return true - if destination connector requires conversion for date/date-time fields, false - in
   *         the other case.
   */
  default boolean requiresDateTimeConversionForSync() {
    return false;
  }

  /**
   *
   * @param path path to field e.g /field1/field2
   * @param key e.g field key
   * @return true if the path consists of only one @key
   */
  default boolean isKeyInPath(String path, String key) {
    var pathFields = new ArrayList<>(Arrays.asList(path.split("/")));
    pathFields.remove(0); // first element always empty string
    return pathFields.size() == 1 && pathFields.contains(key);
  }

}
