/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.protocols.Source;

public interface AirbyteSource extends Source<AirbyteMessage> {

}
