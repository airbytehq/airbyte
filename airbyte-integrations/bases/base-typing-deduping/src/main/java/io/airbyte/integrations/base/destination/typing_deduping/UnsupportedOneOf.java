/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.List;

/**
 * Represents a {oneOf: [...]} schema.
 * <p>
 * This is purely a legacy type that we should eventually delete. See also {@link Union}.
 */
public record UnsupportedOneOf(List<AirbyteType> options) implements AirbyteType {

}
