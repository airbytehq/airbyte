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
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.api.model.SourceCreate;
import io.airbyte.api.model.SourceRead;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.server.converters.ConfigurationUpdate;
import io.airbyte.server.converters.JsonSecretsProcessor;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.server.helpers.SourceDefinitionHelpers;
import io.airbyte.server.helpers.SourceHelpers;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class WebBackendSourceHandlerTest {

  private static String SECRETS_MASK = "**********";

  private WebBackendSourceHandler wbSourceHandler;
  private ConfigRepository configRepository;
  private SpecFetcher specFetcher;
  private Supplier<UUID> uuidGenerator;

  private StandardSourceDefinition standardSourceDefinition;
  private UUID sourceId;

  @BeforeEach
  public void setup() throws IOException, JsonValidationException, ConfigNotFoundException {
    configRepository = mock(ConfigRepository.class);
    specFetcher = mock(SpecFetcher.class);
    uuidGenerator = mock(Supplier.class);
    sourceId = UUID.randomUUID();

    final SourceHandler sourceHandler = new SourceHandler(
        configRepository,
        mock(JsonSchemaValidator.class),
        specFetcher,
        mock(ConnectionsHandler.class),
        uuidGenerator,
        new JsonSecretsProcessor(),
        new ConfigurationUpdate(configRepository, specFetcher));
    final OAuthHandler oAuthHandler = new OAuthHandler(configRepository);
    wbSourceHandler = new WebBackendSourceHandler(sourceHandler, oAuthHandler);

    when(specFetcher.execute(anyString())).thenReturn(new ConnectorSpecification()
        .withConnectionSpecification(Jsons.jsonNode(ImmutableMap.builder()
            .put("type", "object")
            .put("properties", Map.of(
                "api_secret", Map.of("type", "string", JsonSecretsProcessor.AIRBYTE_SECRET_FIELD, true),
                "api_client", Map.of("type", "string")))
            .build())));
    standardSourceDefinition = SourceDefinitionHelpers.generateSource();
    when(uuidGenerator.get()).thenReturn(sourceId);
    when(configRepository.getStandardSourceDefinition(standardSourceDefinition.getSourceDefinitionId())).thenReturn(standardSourceDefinition);
  }

  @Test
  public void testWebBackendCreateSource() throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceConnection source = SourceHelpers.generateSource(standardSourceDefinition.getSourceDefinitionId())
        .withSourceId(sourceId);
    when(configRepository.getSourceConnection(sourceId)).thenReturn(source);
    final SourceRead sourceRead = SourceHelpers.getSourceRead(source, standardSourceDefinition);

    final SourceCreate sourceCreate = new SourceCreate();
    sourceCreate.setName(sourceRead.getName());
    sourceCreate.setConnectionConfiguration(sourceRead.getConnectionConfiguration());
    sourceCreate.setWorkspaceId(sourceRead.getWorkspaceId());
    sourceCreate.setSourceDefinitionId(sourceRead.getSourceDefinitionId());

    final SourceRead actualSourceRead = wbSourceHandler.webBackendCreateSource(Jsons.clone(sourceCreate));

    verify(configRepository).writeSourceConnection(new SourceConnection()
        .withName(sourceRead.getName())
        .withSourceDefinitionId(sourceRead.getSourceDefinitionId())
        .withWorkspaceId(sourceRead.getWorkspaceId())
        .withSourceId(sourceRead.getSourceId())
        .withTombstone(false)
        .withConfiguration(sourceRead.getConnectionConfiguration()));

    assertEquals(sourceRead, actualSourceRead);
  }

  @Test
  public void testWebBackendCreateSourceWithGlobalOAuthParameters() throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceConnection source = SourceHelpers.generateSource(standardSourceDefinition.getSourceDefinitionId())
        .withSourceId(sourceId);

    final SourceRead sourceRead = SourceHelpers.getSourceRead(source, standardSourceDefinition);

    final Map<String, String> oauthParameters = generateOAuthParameters();

    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(
        new SourceOAuthParameter()
            .withOauthParameterId(UUID.randomUUID())
            .withSourceDefinitionId(standardSourceDefinition.getSourceDefinitionId())
            .withWorkspaceId(null)
            .withConfiguration(Jsons.jsonNode(oauthParameters)),
        new SourceOAuthParameter()
            .withOauthParameterId(UUID.randomUUID())
            .withSourceDefinitionId(UUID.randomUUID())
            .withConfiguration(Jsons.jsonNode(generateOAuthParameters()))));

    final SourceCreate sourceCreate = new SourceCreate();
    sourceCreate.setName(sourceRead.getName());
    sourceCreate.setConnectionConfiguration(sourceRead.getConnectionConfiguration());
    sourceCreate.setWorkspaceId(sourceRead.getWorkspaceId());
    sourceCreate.setSourceDefinitionId(sourceRead.getSourceDefinitionId());

    final ObjectNode expectedConfig = ((ObjectNode) Jsons.clone(sourceCreate.getConnectionConfiguration()));
    for (String key : oauthParameters.keySet()) {
      expectedConfig.set(key, Jsons.jsonNode(oauthParameters.get(key)));
    }
    when(configRepository.getSourceConnection(sourceId))
        .thenReturn(Jsons.clone(source).withConfiguration(expectedConfig));

    final SourceRead actualSourceRead = wbSourceHandler.webBackendCreateSource(Jsons.clone(sourceCreate));

    verify(configRepository).writeSourceConnection(new SourceConnection()
        .withName(sourceRead.getName())
        .withSourceDefinitionId(sourceRead.getSourceDefinitionId())
        .withWorkspaceId(sourceRead.getWorkspaceId())
        .withSourceId(sourceRead.getSourceId())
        .withTombstone(false)
        .withConfiguration(expectedConfig));

    expectedConfig.set("api_secret", Jsons.jsonNode(SECRETS_MASK));
    assertEquals(sourceRead.connectionConfiguration(expectedConfig), actualSourceRead);
  }

  private Map<String, String> generateOAuthParameters() {
    return ImmutableMap.<String, String>builder()
        .put("api_secret", "mysecret")
        .put("api_client", UUID.randomUUID().toString())
        .build();
  }

}
