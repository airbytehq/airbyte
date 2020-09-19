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

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceSpecificationRead;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.SourceConnectionSpecification;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.server.helpers.SourceSpecificationHelpers;
import java.io.IOException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SourceSpecificationsHandlerTest {

  private ConfigRepository configRepository;
  private SourceConnectionSpecification sourceConnectionSpecification;
  private SourceSpecificationsHandler sourceSpecificationHandler;

  @BeforeEach
  void setUp() throws IOException {
    configRepository = mock(ConfigRepository.class);
    sourceConnectionSpecification = SourceSpecificationHelpers.generateSourceSpecification();
    sourceSpecificationHandler = new SourceSpecificationsHandler(configRepository);
  }

  @Test
  void testGetSourceSpecification() throws JsonValidationException, IOException, ConfigNotFoundException {
    when(configRepository.listSourceConnectionSpecifications())
        .thenReturn(Lists.newArrayList(sourceConnectionSpecification));

    SourceSpecificationRead expectedSourceSpecificationRead = new SourceSpecificationRead()
        .sourceId(sourceConnectionSpecification.getSourceId())
        .sourceSpecificationId(sourceConnectionSpecification.getSourceSpecificationId())
        .connectionSpecification(sourceConnectionSpecification.getSpecification());

    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(expectedSourceSpecificationRead.getSourceId());

    final SourceSpecificationRead actualSourceSpecificationRead = sourceSpecificationHandler.getSourceSpecification(sourceIdRequestBody);

    assertEquals(expectedSourceSpecificationRead, actualSourceSpecificationRead);
  }

}
