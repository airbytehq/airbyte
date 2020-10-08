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

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnectionSpecification;
import io.airbyte.config.SourceConnectionSpecification;
import java.io.IOException;
import java.util.ArrayList;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class ConfigRepositoryTest {

  private ConfigPersistence configPersistence = mock(ConfigPersistence.class);
  private ConfigRepository repository = new ConfigRepository(configPersistence);

  @Test
  void getSourceConnectionSpecificationFromSourceId() throws JsonValidationException, IOException, ConfigNotFoundException {
    UUID id1 = UUID.randomUUID();
    UUID id2 = UUID.randomUUID();

    SourceConnectionSpecification spec1 = new SourceConnectionSpecification().withSourceId(id1);
    SourceConnectionSpecification spec2 = new SourceConnectionSpecification().withSourceId(id2);

    ArrayList<SourceConnectionSpecification> specs = Lists.newArrayList(spec1, spec2);
    when(configPersistence.listConfigs(ConfigSchema.SOURCE_CONNECTION_SPECIFICATION, SourceConnectionSpecification.class))
        .thenReturn(specs);

    SourceConnectionSpecification actual = repository.getSourceConnectionSpecificationFromSourceId(id1);

    assertEquals(spec1, actual);
  }

  @Test
  void getDestinationConnectionSpecificationFromDestinationId() throws JsonValidationException, IOException, ConfigNotFoundException {
    UUID id1 = UUID.randomUUID();
    UUID id2 = UUID.randomUUID();

    DestinationConnectionSpecification spec1 = new DestinationConnectionSpecification().withDestinationId(id1);
    DestinationConnectionSpecification spec2 = new DestinationConnectionSpecification().withDestinationId(id2);

    ArrayList<DestinationConnectionSpecification> specs = Lists.newArrayList(spec1, spec2);
    when(configPersistence.listConfigs(ConfigSchema.DESTINATION_CONNECTION_SPECIFICATION, DestinationConnectionSpecification.class))
        .thenReturn(specs);

    DestinationConnectionSpecification actual = repository.getDestinationConnectionSpecificationFromDestinationId(id1);

    assertEquals(spec1, actual);
  }

}
