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

import io.airbyte.api.model.SourceCreate;
import io.airbyte.api.model.SourceRead;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;

public class WebBackendSourcesHandler {

  private final SourceHandler sourceHandler;
  private final OAuthConfigSupplier oAuthConfigSupplier;

  public WebBackendSourcesHandler(SourceHandler sourceHandler, ConfigRepository configRepository) {
    this.sourceHandler = sourceHandler;
    oAuthConfigSupplier = new OAuthConfigSupplier(configRepository, true);
  }

  public SourceRead webBackendCreateSource(SourceCreate sourceCreate) throws JsonValidationException, ConfigNotFoundException, IOException {
    sourceCreate.connectionConfiguration(
        oAuthConfigSupplier.injectSourceOAuthParameters(
            sourceCreate.getSourceDefinitionId(),
            sourceCreate.getWorkspaceId(),
            sourceCreate.getConnectionConfiguration()));
    return sourceHandler.createSource(sourceCreate);
  }

}
