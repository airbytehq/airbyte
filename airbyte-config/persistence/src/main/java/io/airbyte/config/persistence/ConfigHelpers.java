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

package io.airbyte.config.persistence;

import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import java.util.UUID;

public class ConfigHelpers {

  public static StandardSourceDefinition getSourceDefinitionFromSource(ConfigRepository configRepository, UUID sourceId) {
    final SourceConnection source;
    try {
      source = configRepository.getSourceConnection(sourceId);
      return configRepository.getStandardSourceDefinition(source.getSourceDefinitionId());
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  public static StandardDestinationDefinition getDestinationDefinitionFromDestination(ConfigRepository configRepository, UUID destinationId) {
    try {
      final DestinationConnection destination = configRepository.getDestinationConnection(destinationId);
      return configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  public static StandardSourceDefinition getSourceDefinitionFromConnection(ConfigRepository configRepository, UUID connectionId) {
    try {
      final StandardSync sync = configRepository.getStandardSync(connectionId);
      return getSourceDefinitionFromSource(configRepository, sync.getSourceId());
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  public static StandardDestinationDefinition getDestinationDefinitionFromConnection(ConfigRepository configRepository, UUID connectionId) {
    try {
      final StandardSync sync = configRepository.getStandardSync(connectionId);
      return getDestinationDefinitionFromDestination(configRepository, sync.getDestinationId());
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

}
