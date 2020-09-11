/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.dataline.api.model.SourceIdRequestBody;
import io.dataline.api.model.SourceRead;
import io.dataline.api.model.SourceReadList;
import io.dataline.config.StandardSource;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigRepository;
import io.dataline.commons.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SourcesHandlerTest {

  private ConfigRepository configRepository;
  private StandardSource source;
  private SourcesHandler sourceHandler;

  @BeforeEach
  void setUp() {
    configRepository = mock(ConfigRepository.class);
    source = generateSource();
    sourceHandler = new SourcesHandler(configRepository);
  }

  private StandardSource generateSource() {
    final UUID sourceId = UUID.randomUUID();

    return new StandardSource()
        .withSourceId(sourceId)
        .withName("presto");
  }

  @Test
  void testListSources() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardSource source2 = generateSource();

    when(configRepository.listStandardSources()).thenReturn(Lists.newArrayList(source, source2));

    SourceRead expectedSourceRead1 = new SourceRead()
        .sourceId(source.getSourceId())
        .name(source.getName());

    SourceRead expectedSourceRead2 = new SourceRead()
        .sourceId(source2.getSourceId())
        .name(source2.getName());

    final SourceReadList actualSourceReadList = sourceHandler.listSources();

    assertEquals(Lists.newArrayList(expectedSourceRead1, expectedSourceRead2), actualSourceReadList.getSources());
  }

  @Test
  void testGetSource() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getStandardSource(source.getSourceId()))
        .thenReturn(source);

    SourceRead expectedSourceRead = new SourceRead()
        .sourceId(source.getSourceId())
        .name(source.getName());

    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(source.getSourceId());

    final SourceRead actualSourceRead = sourceHandler.getSource(sourceIdRequestBody);

    assertEquals(expectedSourceRead, actualSourceRead);
  }

}
