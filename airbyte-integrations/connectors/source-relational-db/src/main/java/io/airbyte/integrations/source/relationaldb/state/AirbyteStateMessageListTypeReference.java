/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import com.fasterxml.jackson.core.type.TypeReference;
import io.airbyte.protocol.models.AirbyteStateMessage;
import java.util.List;

public class AirbyteStateMessageListTypeReference extends TypeReference<List<AirbyteStateMessage>> {

}
