/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import java.util.UUID;
import javax.annotation.Nullable;

public record StreamResetRecord(UUID connectionId,
                                String streamName,
                                @Nullable String streamNamespace) {

}
