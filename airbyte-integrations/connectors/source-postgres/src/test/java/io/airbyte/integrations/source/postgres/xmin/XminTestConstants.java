/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.xmin;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.internal.models.XminStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStateStats;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;

public class XminTestConstants {

  public static final String NAMESPACE = "public";
  public static final String STREAM_NAME1 = "cars";
  public static final AirbyteStreamNameNamespacePair PAIR1 = new AirbyteStreamNameNamespacePair(STREAM_NAME1, NAMESPACE);

  public static final String STREAM_NAME2 = "motorcycles";
  public static final AirbyteStreamNameNamespacePair PAIR2 = new AirbyteStreamNameNamespacePair(STREAM_NAME2, NAMESPACE);

  public static final long XID1 = 123123;
  public static final XminStatus XMIN_STATUS1 = new XminStatus().withNumWraparound(0L).withXminRawValue(XID1).withXminXidValue(XID1);
  public static final AirbyteMessage XMIN_STATE_MESSAGE_1 =
      new AirbyteMessage()
          .withType(Type.STATE)
          .withState(new AirbyteStateMessage()
              .withType(AirbyteStateType.STREAM)
              .withStream(new AirbyteStreamState()
                  .withStreamDescriptor(
                      new StreamDescriptor()
                          .withName(PAIR1.getName())
                          .withNamespace(PAIR1.getNamespace()))
                  .withStreamState(new ObjectMapper().valueToTree(XMIN_STATUS1))));

  public static final long XID2 = 3145555;
  public static final XminStatus XMIN_STATUS2 = new XminStatus().withNumWraparound(0L).withXminRawValue(XID2).withXminXidValue(XID2);
  public static final AirbyteMessage XMIN_STATE_MESSAGE_2 =
      new AirbyteMessage()
          .withType(Type.STATE)
          .withState(new AirbyteStateMessage()
              .withType(AirbyteStateType.STREAM)
              .withStream(new AirbyteStreamState()
                  .withStreamDescriptor(
                      new StreamDescriptor()
                          .withName(PAIR2.getName())
                          .withNamespace(PAIR2.getNamespace()))
                  .withStreamState(new ObjectMapper().valueToTree(XMIN_STATUS2))));

  public static final String UUID_FIELD_NAME = "ascending_inventory_uuid";

  public static final String RECORD_VALUE_1 = "abc";
  public static final AirbyteMessage RECORD_MESSAGE_1 = createRecordMessage(RECORD_VALUE_1);

  public static final String RECORD_VALUE_2 = "def";
  public static final AirbyteMessage RECORD_MESSAGE_2 = createRecordMessage(RECORD_VALUE_2);

  public static final String RECORD_VALUE_3 = "ghi";
  public static final AirbyteMessage RECORD_MESSAGE_3 = createRecordMessage(RECORD_VALUE_3);

  public static AirbyteMessage createRecordMessage(final String recordValue) {
    return new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withData(Jsons.jsonNode(ImmutableMap.of(UUID_FIELD_NAME, recordValue))));
  }

  public static AirbyteMessage createStateMessage1WithCount(final double count) {
    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withType(AirbyteStateType.STREAM)
            .withStream(new AirbyteStreamState()
                .withStreamDescriptor(
                    new StreamDescriptor()
                        .withName(PAIR1.getName())
                        .withNamespace(PAIR1.getNamespace()))
                .withStreamState(new ObjectMapper().valueToTree(XMIN_STATUS1)))
            .withSourceStats(new AirbyteStateStats().withRecordCount(count)));
  }

}
