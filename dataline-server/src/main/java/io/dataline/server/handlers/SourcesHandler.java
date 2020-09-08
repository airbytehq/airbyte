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

import io.dataline.api.model.SourceIdRequestBody;
import io.dataline.api.model.SourceRead;
import io.dataline.api.model.SourceReadList;
import io.dataline.config.StandardSource;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigRepository;
import io.dataline.config.persistence.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;

public class SourcesHandler {

  private final ConfigRepository configRepository;

  public SourcesHandler(final ConfigRepository configRepository) {
    this.configRepository = configRepository;
  }

  public SourceReadList listSources() throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<SourceRead> reads = configRepository.listStandardSources()
        .stream()
        .map(SourcesHandler::buildSourceRead)
        .collect(Collectors.toList());

    return new SourceReadList().sources(reads);
  }

  public SourceRead getSource(SourceIdRequestBody sourceIdRequestBody) throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSource standardSource = configRepository.getStandardSource(sourceIdRequestBody.getSourceId());
    return buildSourceRead(standardSource);
  }

  private static SourceRead buildSourceRead(StandardSource standardSource) {
    final SourceRead sourceRead = new SourceRead();
    sourceRead.setSourceId(standardSource.getSourceId());
    sourceRead.setName(standardSource.getName());

    return sourceRead;
  }

}
