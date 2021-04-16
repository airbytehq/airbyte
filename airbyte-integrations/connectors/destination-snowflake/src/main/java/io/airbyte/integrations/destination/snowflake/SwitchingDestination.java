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

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;

public abstract class SwitchingDestination<T extends Enum<T>> implements Destination {

  private final Function<JsonNode, T> configToType;
  private final Map<T, Destination> typeToDestination;

  public SwitchingDestination(Class<T> enumClass, Function<JsonNode, T> configToType, Map<T, Destination> typeToDestination) {
    final Set<T> allEnumConstants = new HashSet<>(Arrays.asList(enumClass.getEnumConstants()));
    final Set<T> supportedEnumConstants = typeToDestination.keySet();

    // check that it isn't possible for configToType to produce something we can't handle
    Preconditions.checkArgument(allEnumConstants.equals(supportedEnumConstants));

    this.configToType = configToType;
    this.typeToDestination = typeToDestination;
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) throws Exception {
    final T destinationType = configToType.apply(config);
    return typeToDestination.get(destinationType).check(config);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception {
    final T destinationType = configToType.apply(config);
    return typeToDestination.get(destinationType).getConsumer(config, catalog);
  }

}
