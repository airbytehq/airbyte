/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.xmin;

import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.NAMESPACE;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.PAIR1;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.PAIR2;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.STREAM_NAME1;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.XMIN_STATE_MESSAGE_1;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.XMIN_STATE_MESSAGE_2;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.XMIN_STATUS1;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.XMIN_STATUS2;
import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.assertj.core.api.AssertionsForClassTypes.catchThrowable;

import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.List;
import org.junit.jupiter.api.Test;

public class XminStateManagerTest {

  @Test
  void testCreationFromInvalidState() {
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState()
            .withStreamDescriptor(new StreamDescriptor().withName(STREAM_NAME1).withNamespace(NAMESPACE))
            .withStreamState(Jsons.jsonNode("Not a state object")));

    final Throwable throwable = catchThrowable(() -> new XminStateManager(List.of(airbyteStateMessage)));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class)
        .hasMessageContaining(
            "Invalid per-stream state. If this connection was migrated to a Xmin incremental mode from a cursor-based or CDC incremental "
                + "mode, please reset your connection and re-sync.");
  }

  @Test
  void testGetXminStates() {
    final XminStateManager xminStateManager = new XminStateManager(List.of(XMIN_STATE_MESSAGE_1.getState(), XMIN_STATE_MESSAGE_2.getState()));
    assertThat(xminStateManager.getXminStatus(PAIR1)).isEqualTo(XMIN_STATUS1);
    assertThat(xminStateManager.getXminStatus(PAIR2)).isEqualTo(XMIN_STATUS2);
  }

  @Test
  void testCreateStateMessage() {
    assertThat(XminStateManager.createStateMessage(PAIR1, XMIN_STATUS1)).isEqualTo(XMIN_STATE_MESSAGE_1);
    assertThat(XminStateManager.createStateMessage(PAIR2, XMIN_STATUS2)).isEqualTo(XMIN_STATE_MESSAGE_2);
  }

}
