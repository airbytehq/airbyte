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
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.server.helpers.DestinationDefinitionHelpers;
import io.airbyte.server.helpers.SourceDefinitionHelpers;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DebugInfoHandlerTest {

  private ConfigRepository configRepository;

  @BeforeEach
  public void init() {
    configRepository = mock(ConfigRepository.class);
  }

  @Test
  public void testNoFailures() throws ConfigNotFoundException, IOException, JsonValidationException {
    when(configRepository.listStandardSources()).thenReturn(Lists.newArrayList(SourceDefinitionHelpers.generateSource()));
    when(configRepository.listStandardDestinationDefinitions()).thenReturn(Lists.newArrayList(DestinationDefinitionHelpers.generateDestination()));
    new DebugInfoHandler(configRepository).getInfo();
  }

  @Test
  public void testRunAndGetOutput() throws IOException, InterruptedException {
    final String expected = "hi" + System.lineSeparator();
    final String actual = DebugInfoHandler.runAndGetOutput("echo", "hi");
    assertEquals(expected, actual);
  }

  @Test
  public void testShortHash() {
    final String expected = "1326d8641577";
    final String actual = DebugInfoHandler.getShortHash("sha256:1326d864157731c10724e5a407cf227e14e147a11dc4ba64157ebe8689a28d84");
    assertEquals(expected, actual);
  }

}
