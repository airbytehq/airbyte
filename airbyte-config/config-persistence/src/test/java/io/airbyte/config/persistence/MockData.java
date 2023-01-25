/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ActorCatalog;
import io.airbyte.config.ActorCatalogFetchEvent;
import io.airbyte.config.ActorDefinitionResourceRequirements;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.FieldSelectionData;
import io.airbyte.config.Geography;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.config.OperatorDbt;
import io.airbyte.config.OperatorNormalization;
import io.airbyte.config.OperatorNormalization.Option;
import io.airbyte.config.OperatorWebhook;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.Schedule;
import io.airbyte.config.Schedule.TimeUnit;
import io.airbyte.config.SlackNotificationConfiguration;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.SourceType;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.NonBreakingChangesPreference;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.config.StandardSyncState;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.State;
import io.airbyte.config.WebhookConfig;
import io.airbyte.config.WebhookOperationConfigs;
import io.airbyte.config.WorkspaceServiceAccount;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AuthSpecification;
import io.airbyte.protocol.models.AuthSpecification.AuthType;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.net.URI;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.UUID;
import java.util.stream.Collectors;
import lombok.Data;

public class MockData {

  public static final UUID WORKSPACE_ID_1 = UUID.randomUUID();
  private static final UUID WORKSPACE_ID_2 = UUID.randomUUID();
  private static final UUID WORKSPACE_ID_3 = UUID.randomUUID();
  private static final UUID WORKSPACE_CUSTOMER_ID = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID_1 = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID_2 = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID_3 = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID_4 = UUID.randomUUID();
  private static final UUID DESTINATION_DEFINITION_ID_1 = UUID.randomUUID();
  private static final UUID DESTINATION_DEFINITION_ID_2 = UUID.randomUUID();
  private static final UUID DESTINATION_DEFINITION_ID_3 = UUID.randomUUID();
  private static final UUID DESTINATION_DEFINITION_ID_4 = UUID.randomUUID();
  public static final UUID SOURCE_ID_1 = UUID.randomUUID();
  public static final UUID SOURCE_ID_2 = UUID.randomUUID();
  private static final UUID SOURCE_ID_3 = UUID.randomUUID();
  public static final UUID DESTINATION_ID_1 = UUID.randomUUID();
  public static final UUID DESTINATION_ID_2 = UUID.randomUUID();
  public static final UUID DESTINATION_ID_3 = UUID.randomUUID();
  private static final UUID OPERATION_ID_1 = UUID.randomUUID();
  private static final UUID OPERATION_ID_2 = UUID.randomUUID();
  private static final UUID OPERATION_ID_3 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_1 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_2 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_3 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_4 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_5 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_6 = UUID.randomUUID();
  private static final UUID SOURCE_OAUTH_PARAMETER_ID_1 = UUID.randomUUID();
  private static final UUID SOURCE_OAUTH_PARAMETER_ID_2 = UUID.randomUUID();
  private static final UUID DESTINATION_OAUTH_PARAMETER_ID_1 = UUID.randomUUID();
  private static final UUID DESTINATION_OAUTH_PARAMETER_ID_2 = UUID.randomUUID();
  public static final UUID ACTOR_CATALOG_ID_1 = UUID.randomUUID();
  private static final UUID ACTOR_CATALOG_ID_2 = UUID.randomUUID();
  public static final UUID ACTOR_CATALOG_ID_3 = UUID.randomUUID();
  private static final UUID ACTOR_CATALOG_FETCH_EVENT_ID_1 = UUID.randomUUID();
  private static final UUID ACTOR_CATALOG_FETCH_EVENT_ID_2 = UUID.randomUUID();
  private static final UUID ACTOR_CATALOG_FETCH_EVENT_ID_3 = UUID.randomUUID();

  public static final String MOCK_SERVICE_ACCOUNT_1 = "{\n"
      + "  \"type\" : \"service_account\",\n"
      + "  \"project_id\" : \"random-gcp-project\",\n"
      + "  \"private_key_id\" : \"123a1234ab1a123ab12345678a1234ab1abc1a12\",\n"
      + "  \"private_key\" : \"-----BEGIN RSA PRIVATE KEY-----\\nMIIEoQIBAAKCAQBtkKBs9oe9pFhEWjBls9OrY0PXE/QN6nL4Bfw4+UqcBpTyItXo\\n3aBXuVqDIZ377zjbJUcYuc4NzAsLImy7VVT1XrdAkkCKQEMoA9pQgONA/3kD8Xff\\nSUGfdup8UJg925paaRhM7u81e3XKGwGyL/qcxpuHtfqimeWWfSPy5AawyOFl+l25\\nOqbm8PK4/QVqk4pcorQuISUkrehY0Ji0gVQF+ZeBvg7lvBtjNEl//eysGtcZvk7X\\nHqg+EIBqRjVNDsViHj0xeoDFcFgXDeWzxeQ0c7gMsDthfm4SjgaVFdQwsJUeoC6X\\nlwUoBbFIVVKW0n+SH+kxLc7mhaGjyRYJLS6tAgMBAAECggEAaowetlf4IR/VBoN+\\nVSjPSvg5XMr2pyG7tB597RngyGJOLjpaMx5zc1u4/ZSPghRdAh/6R71I+HnYs3dC\\nrdqJyCPXqV+Qi+F6bUtx3p+4X9kQ4hjMLcOboWuPFF1774vDSvCwxQAGd8gb//LL\\nb3DhEdzCGvOJTN7EOdhwQSAmsXsfj0qKlmm8vv0HBQDvjYYWhy/UcPry5sAGQ8KU\\nnUPTkz/OMS56nBIgKXgZtGRTP1Q7Q9a6oLmlvbDxuKGUByUPNlveZplzyWDO3RUN\\nNPt9dwgGk6rZK0umunGr0lq+WOK33Ue1RJy2VIvvV6dt32x20ehfVKND8N8q+wJ3\\neJQggQKBgQC//dOX8RwkmIloRzzmbu+qY8o44/F5gtxj8maR+OJhvbpFEID49bBr\\nzYqcMKfcgHJr6638CXVGSO66IiKtQcTMJ/Vd8TQVPcNPI1h/RD+wT/nkWX6R/0YH\\njwwNmikeUDH2/hLQlRZ8O45hc4frDGRMeHn3MSS2YsBDSl6YL/zHpQKBgQCSF9Ka\\nyCZmw5eS63G5/X9SVXbLRPuc6Fus+IbRPttOzSRviUXHaBjwwVEJgIKODx/eVXgD\\nA/OvFUmwIn73uZD/XgJrhkwAendaa+yhWKAkO5pO/EdAslxRmgxqTXfRcyslKBbo\\ns4YAgeYUgzOaMH4UxY4pJ7H6BLsFlboL+8BcaQKBgDSCM1Cm/M91eH8wnJNZW+r6\\nB+CvVueoxqX/MdZSf3fD8CHbdaqhZ3LUcEhvdjl0V9b0Sk1YON7UK5Z0p49DIZPE\\nifL7eQcmMTh/rkCAZfrOpMWzRE6hxoFiuiUuOHi17jRjILozTEcF8tbsRgwfA392\\no8Tbh/Lp5zOAL4bn+PaRAoGAZ2AgEJJsSe9BRB8CPF+aRoJfKvrHKIJqzHyXuVzH\\nBn22uI3kKHQKoeHJG/Ypa6hcHpFP+KJFPrDLkaz3NwfCCFFXWQqQoQ4Hgp43tPvn\\nZXwfdqChMrCDDuL4wgfLLxRVhVdWzpapzZYdXopwazzBGqWoMIr8LzRFum/2VCBy\\nP3ECgYBGqjuYud6gtrzaQwmMfcA0pSYsii96d2LKwWzjgcMzLxge59PIWXeQJqOb\\nh97m3qCkkPzbceD6Id8m/EyrNb04V8Zr0ERlcK/a4nRSHoIWQZY01lDSGhneRKn1\\nncBvRqCfz6ajf+zBg3zK0af98IHL0FI2NsNJLPrOBFMcthjx/g==\\n-----END RSA PRIVATE KEY-----\",\n"
      + "  \"client_email\" : \"a1e5ac98-7531-48e1-943b-b46636@random-gcp-project.abc.abcdefghijklmno.com\",\n"
      + "  \"client_id\" : \"123456789012345678901\",\n"
      + "  \"auth_uri\" : \"https://blah.blah.com/x/blah1/blah\",\n"
      + "  \"token_uri\" : \"https://blah.blah.com/blah\",\n"
      + "  \"auth_provider_x509_cert_url\" : \"https://www.blah.com/blah/v1/blah\",\n"
      + "  \"client_x509_cert_url\" : \"https://www.blah.com/blah/v1/blah/a123/a1e5ac98-7531-48e1-943b-b46636%40random-gcp-project.abc.abcdefghijklmno.com\"\n"
      + "}";

  public static final String MOCK_SERVICE_ACCOUNT_2 = "{\n"
      + "  \"type\" : \"service_account-2\",\n"
      + "  \"project_id\" : \"random-gcp-project\",\n"
      + "  \"private_key_id\" : \"123a1234ab1a123ab12345678a1234ab1abc1a12\",\n"
      + "  \"private_key\" : \"-----BEGIN RSA PRIVATE KEY-----\\nMIIEoQIBAAKCAQBtkKBs9oe9pFhEWjBls9OrY0PXE/QN6nL4Bfw4+UqcBpTyItXo\\n3aBXuVqDIZ377zjbJUcYuc4NzAsLImy7VVT1XrdAkkCKQEMoA9pQgONA/3kD8Xff\\nSUGfdup8UJg925paaRhM7u81e3XKGwGyL/qcxpuHtfqimeWWfSPy5AawyOFl+l25\\nOqbm8PK4/QVqk4pcorQuISUkrehY0Ji0gVQF+ZeBvg7lvBtjNEl//eysGtcZvk7X\\nHqg+EIBqRjVNDsViHj0xeoDFcFgXDeWzxeQ0c7gMsDthfm4SjgaVFdQwsJUeoC6X\\nlwUoBbFIVVKW0n+SH+kxLc7mhaGjyRYJLS6tAgMBAAECggEAaowetlf4IR/VBoN+\\nVSjPSvg5XMr2pyG7tB597RngyGJOLjpaMx5zc1u4/ZSPghRdAh/6R71I+HnYs3dC\\nrdqJyCPXqV+Qi+F6bUtx3p+4X9kQ4hjMLcOboWuPFF1774vDSvCwxQAGd8gb//LL\\nb3DhEdzCGvOJTN7EOdhwQSAmsXsfj0qKlmm8vv0HBQDvjYYWhy/UcPry5sAGQ8KU\\nnUPTkz/OMS56nBIgKXgZtGRTP1Q7Q9a6oLmlvbDxuKGUByUPNlveZplzyWDO3RUN\\nNPt9dwgGk6rZK0umunGr0lq+WOK33Ue1RJy2VIvvV6dt32x20ehfVKND8N8q+wJ3\\neJQggQKBgQC//dOX8RwkmIloRzzmbu+qY8o44/F5gtxj8maR+OJhvbpFEID49bBr\\nzYqcMKfcgHJr6638CXVGSO66IiKtQcTMJ/Vd8TQVPcNPI1h/RD+wT/nkWX6R/0YH\\njwwNmikeUDH2/hLQlRZ8O45hc4frDGRMeHn3MSS2YsBDSl6YL/zHpQKBgQCSF9Ka\\nyCZmw5eS63G5/X9SVXbLRPuc6Fus+IbRPttOzSRviUXHaBjwwVEJgIKODx/eVXgD\\nA/OvFUmwIn73uZD/XgJrhkwAendaa+yhWKAkO5pO/EdAslxRmgxqTXfRcyslKBbo\\ns4YAgeYUgzOaMH4UxY4pJ7H6BLsFlboL+8BcaQKBgDSCM1Cm/M91eH8wnJNZW+r6\\nB+CvVueoxqX/MdZSf3fD8CHbdaqhZ3LUcEhvdjl0V9b0Sk1YON7UK5Z0p49DIZPE\\nifL7eQcmMTh/rkCAZfrOpMWzRE6hxoFiuiUuOHi17jRjILozTEcF8tbsRgwfA392\\no8Tbh/Lp5zOAL4bn+PaRAoGAZ2AgEJJsSe9BRB8CPF+aRoJfKvrHKIJqzHyXuVzH\\nBn22uI3kKHQKoeHJG/Ypa6hcHpFP+KJFPrDLkaz3NwfCCFFXWQqQoQ4Hgp43tPvn\\nZXwfdqChMrCDDuL4wgfLLxRVhVdWzpapzZYdXopwazzBGqWoMIr8LzRFum/2VCBy\\nP3ECgYBGqjuYud6gtrzaQwmMfcA0pSYsii96d2LKwWzjgcMzLxge59PIWXeQJqOb\\nh97m3qCkkPzbceD6Id8m/EyrNb04V8Zr0ERlcK/a4nRSHoIWQZY01lDSGhneRKn1\\nncBvRqCfz6ajf+zBg3zK0af98IHL0FI2NsNJLPrOBFMcthjx/g==\\n-----END RSA PRIVATE KEY-----\",\n"
      + "  \"client_email\" : \"a1e5ac98-7531-48e1-943b-b46636@random-gcp-project.abc.abcdefghijklmno.com\",\n"
      + "  \"client_id\" : \"123456789012345678901\",\n"
      + "  \"auth_uri\" : \"https://blah.blah.com/x/blah1/blah\",\n"
      + "  \"token_uri\" : \"https://blah.blah.com/blah\",\n"
      + "  \"auth_provider_x509_cert_url\" : \"https://www.blah.com/blah/v1/blah\",\n"
      + "  \"client_x509_cert_url\" : \"https://www.blah.com/blah/v1/blah/a123/a1e5ac98-7531-48e1-943b-b46636%40random-gcp-project.abc.abcdefghijklmno.com\"\n"
      + "}";

  public static final JsonNode HMAC_SECRET_PAYLOAD_1 = Jsons.jsonNode(sortMap(
      Map.of("access_id", "ABCD1A1ABCDEFG1ABCDEFGH1ABC12ABCDEF1ABCDE1ABCDE1ABCDE12ABCDEF", "secret", "AB1AbcDEF//ABCDeFGHijKlmNOpqR1ABC1aBCDeF")));
  public static final JsonNode HMAC_SECRET_PAYLOAD_2 = Jsons.jsonNode(sortMap(
      Map.of("access_id", "ABCD1A1ABCDEFG1ABCDEFGH1ABC12ABCDEF1ABCDE1ABCDE1ABCDE12ABCDEX", "secret", "AB1AbcDEF//ABCDeFGHijKlmNOpqR1ABC1aBCDeX")));

  private static final Instant NOW = Instant.parse("2021-12-15T20:30:40.00Z");

  private static final String CONNECTION_SPECIFICATION = "{\"name\":\"John\", \"age\":30, \"car\":null}";
  private static final UUID OPERATION_ID_4 = UUID.randomUUID();
  private static final UUID WEBHOOK_CONFIG_ID = UUID.randomUUID();
  private static final String WEBHOOK_OPERATION_EXECUTION_URL = "test-webhook-url";
  private static final String WEBHOOK_OPERATION_EXECUTION_BODY = "test-webhook-body";
  public static final String CONFIG_HASH = "1394";
  public static final String CONNECTOR_VERSION = "1.2.0";

  public static List<StandardWorkspace> standardWorkspaces() {
    final Notification notification = new Notification()
        .withNotificationType(NotificationType.SLACK)
        .withSendOnFailure(true)
        .withSendOnSuccess(true)
        .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook("webhook-url"));

    final StandardWorkspace workspace1 = new StandardWorkspace()
        .withWorkspaceId(WORKSPACE_ID_1)
        .withCustomerId(WORKSPACE_CUSTOMER_ID)
        .withName("test-workspace")
        .withSlug("random-string")
        .withEmail("abc@xyz.com")
        .withInitialSetupComplete(true)
        .withAnonymousDataCollection(true)
        .withNews(true)
        .withSecurityUpdates(true)
        .withDisplaySetupWizard(true)
        .withTombstone(false)
        .withNotifications(Collections.singletonList(notification))
        .withFirstCompletedSync(true)
        .withFeedbackDone(true)
        .withDefaultGeography(Geography.US)
        .withWebhookOperationConfigs(Jsons.jsonNode(
            new WebhookOperationConfigs().withWebhookConfigs(List.of(new WebhookConfig().withId(WEBHOOK_CONFIG_ID).withName("name")))));

    final StandardWorkspace workspace2 = new StandardWorkspace()
        .withWorkspaceId(WORKSPACE_ID_2)
        .withName("Another Workspace")
        .withSlug("another-workspace")
        .withInitialSetupComplete(true)
        .withTombstone(false)
        .withDefaultGeography(Geography.AUTO);

    final StandardWorkspace workspace3 = new StandardWorkspace()
        .withWorkspaceId(WORKSPACE_ID_3)
        .withName("Tombstoned")
        .withSlug("tombstoned")
        .withInitialSetupComplete(true)
        .withTombstone(true)
        .withDefaultGeography(Geography.AUTO);

    return Arrays.asList(workspace1, workspace2, workspace3);
  }

  public static StandardSourceDefinition publicSourceDefinition() {
    return new StandardSourceDefinition()
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_1)
        .withSourceType(SourceType.API)
        .withName("random-source-1")
        .withDockerImageTag("tag-1")
        .withDockerRepository("repository-1")
        .withDocumentationUrl("documentation-url-1")
        .withIcon("icon-1")
        .withSpec(connectorSpecification())
        .withProtocolVersion("0.2.1")
        .withTombstone(false)
        .withPublic(true)
        .withCustom(false)
        .withResourceRequirements(new ActorDefinitionResourceRequirements().withDefault(new ResourceRequirements().withCpuRequest("2")));
  }

  public static StandardSourceDefinition grantableSourceDefinition1() {
    return new StandardSourceDefinition()
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_2)
        .withSourceType(SourceType.DATABASE)
        .withName("random-source-2")
        .withDockerImageTag("tag-2")
        .withDockerRepository("repository-2")
        .withDocumentationUrl("documentation-url-2")
        .withIcon("icon-2")
        .withTombstone(false)
        .withPublic(false)
        .withCustom(false);
  }

  public static StandardSourceDefinition grantableSourceDefinition2() {
    return new StandardSourceDefinition()
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_3)
        .withSourceType(SourceType.DATABASE)
        .withName("random-source-3")
        .withDockerImageTag("tag-3")
        .withDockerRepository("repository-3")
        .withDocumentationUrl("documentation-url-3")
        .withProtocolVersion("0.2.2")
        .withIcon("icon-3")
        .withTombstone(false)
        .withPublic(false)
        .withCustom(false);
  }

  public static StandardSourceDefinition customSourceDefinition() {
    return new StandardSourceDefinition()
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_4)
        .withSourceType(SourceType.DATABASE)
        .withName("random-source-4")
        .withDockerImageTag("tag-4")
        .withDockerRepository("repository-4")
        .withDocumentationUrl("documentation-url-4")
        .withProtocolVersion("0.2.4")
        .withIcon("icon-4")
        .withTombstone(false)
        .withPublic(false)
        .withCustom(true);
  }

  public static List<StandardSourceDefinition> standardSourceDefinitions() {
    return Arrays.asList(
        publicSourceDefinition(),
        grantableSourceDefinition1(),
        grantableSourceDefinition2(),
        customSourceDefinition());
  }

  private static ConnectorSpecification connectorSpecification() {
    return new ConnectorSpecification()
        .withAuthSpecification(new AuthSpecification().withAuthType(AuthType.OAUTH_2_0))
        .withConnectionSpecification(Jsons.jsonNode(CONNECTION_SPECIFICATION))
        .withDocumentationUrl(URI.create("whatever"))
        .withAdvancedAuth(null)
        .withChangelogUrl(URI.create("whatever"))
        .withSupportedDestinationSyncModes(Arrays.asList(DestinationSyncMode.APPEND, DestinationSyncMode.OVERWRITE, DestinationSyncMode.APPEND_DEDUP))
        .withSupportsDBT(true)
        .withSupportsIncremental(true)
        .withSupportsNormalization(true);
  }

  public static StandardDestinationDefinition publicDestinationDefinition() {
    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_1)
        .withName("random-destination-1")
        .withDockerImageTag("tag-3")
        .withDockerRepository("repository-3")
        .withDocumentationUrl("documentation-url-3")
        .withIcon("icon-3")
        .withSpec(connectorSpecification())
        .withProtocolVersion("0.3.1")
        .withTombstone(false)
        .withPublic(true)
        .withCustom(false)
        .withResourceRequirements(new ActorDefinitionResourceRequirements().withDefault(new ResourceRequirements().withCpuRequest("2")));
  }

  public static StandardDestinationDefinition grantableDestinationDefinition1() {
    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_2)
        .withName("random-destination-2")
        .withDockerImageTag("tag-4")
        .withDockerRepository("repository-4")
        .withDocumentationUrl("documentation-url-4")
        .withIcon("icon-4")
        .withSpec(connectorSpecification())
        .withTombstone(false)
        .withPublic(false)
        .withCustom(false);
  }

  public static StandardDestinationDefinition grantableDestinationDefinition2() {
    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_3)
        .withName("random-destination-3")
        .withDockerImageTag("tag-33")
        .withDockerRepository("repository-33")
        .withDocumentationUrl("documentation-url-33")
        .withIcon("icon-3")
        .withSpec(connectorSpecification())
        .withTombstone(false)
        .withPublic(false)
        .withCustom(false);
  }

  public static StandardDestinationDefinition cusstomDestinationDefinition() {
    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_4)
        .withName("random-destination-4")
        .withDockerImageTag("tag-44")
        .withDockerRepository("repository-44")
        .withDocumentationUrl("documentation-url-44")
        .withIcon("icon-4")
        .withSpec(connectorSpecification())
        .withProtocolVersion("0.3.2")
        .withTombstone(false)
        .withPublic(false)
        .withCustom(true);
  }

  public static List<StandardDestinationDefinition> standardDestinationDefinitions() {
    return Arrays.asList(
        publicDestinationDefinition(),
        grantableDestinationDefinition1(),
        grantableDestinationDefinition2(),
        cusstomDestinationDefinition());
  }

  public static List<SourceConnection> sourceConnections() {
    final SourceConnection sourceConnection1 = new SourceConnection()
        .withName("source-1")
        .withTombstone(false)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_1)
        .withWorkspaceId(WORKSPACE_ID_1)
        .withConfiguration(Jsons.deserialize(CONNECTION_SPECIFICATION))
        .withSourceId(SOURCE_ID_1);
    final SourceConnection sourceConnection2 = new SourceConnection()
        .withName("source-2")
        .withTombstone(false)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_2)
        .withWorkspaceId(WORKSPACE_ID_1)
        .withConfiguration(Jsons.deserialize(CONNECTION_SPECIFICATION))
        .withSourceId(SOURCE_ID_2);
    final SourceConnection sourceConnection3 = new SourceConnection()
        .withName("source-3")
        .withTombstone(false)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_1)
        .withWorkspaceId(WORKSPACE_ID_2)
        .withConfiguration(Jsons.emptyObject())
        .withSourceId(SOURCE_ID_3);
    return Arrays.asList(sourceConnection1, sourceConnection2, sourceConnection3);
  }

  public static List<DestinationConnection> destinationConnections() {
    final DestinationConnection destinationConnection1 = new DestinationConnection()
        .withName("destination-1")
        .withTombstone(false)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_1)
        .withWorkspaceId(WORKSPACE_ID_1)
        .withConfiguration(Jsons.deserialize(CONNECTION_SPECIFICATION))
        .withDestinationId(DESTINATION_ID_1);
    final DestinationConnection destinationConnection2 = new DestinationConnection()
        .withName("destination-2")
        .withTombstone(false)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_2)
        .withWorkspaceId(WORKSPACE_ID_1)
        .withConfiguration(Jsons.deserialize(CONNECTION_SPECIFICATION))
        .withDestinationId(DESTINATION_ID_2);
    final DestinationConnection destinationConnection3 = new DestinationConnection()
        .withName("destination-3")
        .withTombstone(true)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_2)
        .withWorkspaceId(WORKSPACE_ID_2)
        .withConfiguration(Jsons.emptyObject())
        .withDestinationId(DESTINATION_ID_3);
    return Arrays.asList(destinationConnection1, destinationConnection2, destinationConnection3);
  }

  public static List<SourceOAuthParameter> sourceOauthParameters() {
    final SourceOAuthParameter sourceOAuthParameter1 = new SourceOAuthParameter()
        .withConfiguration(Jsons.jsonNode(CONNECTION_SPECIFICATION))
        .withWorkspaceId(WORKSPACE_ID_1)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_1)
        .withOauthParameterId(SOURCE_OAUTH_PARAMETER_ID_1);
    final SourceOAuthParameter sourceOAuthParameter2 = new SourceOAuthParameter()
        .withConfiguration(Jsons.jsonNode(CONNECTION_SPECIFICATION))
        .withWorkspaceId(WORKSPACE_ID_1)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_2)
        .withOauthParameterId(SOURCE_OAUTH_PARAMETER_ID_2);
    return Arrays.asList(sourceOAuthParameter1, sourceOAuthParameter2);
  }

  public static List<DestinationOAuthParameter> destinationOauthParameters() {
    final DestinationOAuthParameter destinationOAuthParameter1 = new DestinationOAuthParameter()
        .withConfiguration(Jsons.jsonNode(CONNECTION_SPECIFICATION))
        .withWorkspaceId(WORKSPACE_ID_1)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_1)
        .withOauthParameterId(DESTINATION_OAUTH_PARAMETER_ID_1);
    final DestinationOAuthParameter destinationOAuthParameter2 = new DestinationOAuthParameter()
        .withConfiguration(Jsons.jsonNode(CONNECTION_SPECIFICATION))
        .withWorkspaceId(WORKSPACE_ID_1)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_2)
        .withOauthParameterId(DESTINATION_OAUTH_PARAMETER_ID_2);
    return Arrays.asList(destinationOAuthParameter1, destinationOAuthParameter2);
  }

  public static List<StandardSyncOperation> standardSyncOperations() {
    final OperatorDbt operatorDbt = new OperatorDbt()
        .withDbtArguments("dbt-arguments")
        .withDockerImage("image-tag")
        .withGitRepoBranch("git-repo-branch")
        .withGitRepoUrl("git-repo-url");
    final StandardSyncOperation standardSyncOperation1 = new StandardSyncOperation()
        .withName("operation-1")
        .withTombstone(false)
        .withOperationId(OPERATION_ID_1)
        .withWorkspaceId(WORKSPACE_ID_1)
        .withOperatorDbt(operatorDbt)
        .withOperatorNormalization(null)
        .withOperatorType(OperatorType.DBT);
    final StandardSyncOperation standardSyncOperation2 = new StandardSyncOperation()
        .withName("operation-1")
        .withTombstone(false)
        .withOperationId(OPERATION_ID_2)
        .withWorkspaceId(WORKSPACE_ID_1)
        .withOperatorDbt(null)
        .withOperatorNormalization(new OperatorNormalization().withOption(Option.BASIC))
        .withOperatorType(OperatorType.NORMALIZATION);
    final StandardSyncOperation standardSyncOperation3 = new StandardSyncOperation()
        .withName("operation-3")
        .withTombstone(false)
        .withOperationId(OPERATION_ID_3)
        .withWorkspaceId(WORKSPACE_ID_2)
        .withOperatorDbt(null)
        .withOperatorNormalization(new OperatorNormalization().withOption(Option.BASIC))
        .withOperatorType(OperatorType.NORMALIZATION);
    final StandardSyncOperation standardSyncOperation4 = new StandardSyncOperation()
        .withName("webhook-operation")
        .withTombstone(false)
        .withOperationId(OPERATION_ID_4)
        .withWorkspaceId(WORKSPACE_ID_1)
        .withOperatorType(OperatorType.WEBHOOK)
        .withOperatorDbt(null)
        .withOperatorNormalization(null)
        .withOperatorWebhook(
            new OperatorWebhook()
                .withWebhookConfigId(WEBHOOK_CONFIG_ID)
                .withExecutionUrl(WEBHOOK_OPERATION_EXECUTION_URL)
                .withExecutionBody(WEBHOOK_OPERATION_EXECUTION_BODY));
    return Arrays.asList(standardSyncOperation1, standardSyncOperation2, standardSyncOperation3, standardSyncOperation4);
  }

  public static List<StandardSync> standardSyncs() {
    final ResourceRequirements resourceRequirements = new ResourceRequirements()
        .withCpuRequest("1")
        .withCpuLimit("1")
        .withMemoryRequest("1")
        .withMemoryLimit("1");
    final Schedule schedule = new Schedule().withTimeUnit(TimeUnit.DAYS).withUnits(1L);
    final StandardSync standardSync1 = new StandardSync()
        .withOperationIds(Arrays.asList(OPERATION_ID_1, OPERATION_ID_2))
        .withConnectionId(CONNECTION_ID_1)
        .withSourceId(SOURCE_ID_1)
        .withDestinationId(DESTINATION_ID_1)
        .withCatalog(getConfiguredCatalog())
        .withFieldSelectionData(new FieldSelectionData().withAdditionalProperty("foo", true))
        .withName("standard-sync-1")
        .withManual(true)
        .withNamespaceDefinition(NamespaceDefinitionType.CUSTOMFORMAT)
        .withNamespaceFormat("")
        .withPrefix("")
        .withResourceRequirements(resourceRequirements)
        .withStatus(Status.ACTIVE)
        .withSchedule(schedule)
        .withGeography(Geography.AUTO)
        .withBreakingChange(false)
        .withNonBreakingChangesPreference(NonBreakingChangesPreference.IGNORE)
        .withNotifySchemaChanges(true);

    final StandardSync standardSync2 = new StandardSync()
        .withOperationIds(Arrays.asList(OPERATION_ID_1, OPERATION_ID_2))
        .withConnectionId(CONNECTION_ID_2)
        .withSourceId(SOURCE_ID_1)
        .withDestinationId(DESTINATION_ID_2)
        .withCatalog(getConfiguredCatalog())
        .withName("standard-sync-2")
        .withManual(true)
        .withNamespaceDefinition(NamespaceDefinitionType.SOURCE)
        .withNamespaceFormat("")
        .withPrefix("")
        .withResourceRequirements(resourceRequirements)
        .withStatus(Status.ACTIVE)
        .withSchedule(schedule)
        .withGeography(Geography.AUTO)
        .withBreakingChange(false)
        .withNonBreakingChangesPreference(NonBreakingChangesPreference.IGNORE)
        .withNotifySchemaChanges(true);

    final StandardSync standardSync3 = new StandardSync()
        .withOperationIds(Arrays.asList(OPERATION_ID_1, OPERATION_ID_2))
        .withConnectionId(CONNECTION_ID_3)
        .withSourceId(SOURCE_ID_2)
        .withDestinationId(DESTINATION_ID_1)
        .withCatalog(getConfiguredCatalog())
        .withName("standard-sync-3")
        .withManual(true)
        .withNamespaceDefinition(NamespaceDefinitionType.DESTINATION)
        .withNamespaceFormat("")
        .withPrefix("")
        .withResourceRequirements(resourceRequirements)
        .withStatus(Status.ACTIVE)
        .withSchedule(schedule)
        .withGeography(Geography.AUTO)
        .withBreakingChange(false)
        .withNonBreakingChangesPreference(NonBreakingChangesPreference.IGNORE)
        .withNotifySchemaChanges(true);

    final StandardSync standardSync4 = new StandardSync()
        .withOperationIds(Collections.emptyList())
        .withConnectionId(CONNECTION_ID_4)
        .withSourceId(SOURCE_ID_2)
        .withDestinationId(DESTINATION_ID_2)
        .withCatalog(getConfiguredCatalog())
        .withName("standard-sync-4")
        .withManual(true)
        .withNamespaceDefinition(NamespaceDefinitionType.CUSTOMFORMAT)
        .withNamespaceFormat("")
        .withPrefix("")
        .withResourceRequirements(resourceRequirements)
        .withStatus(Status.DEPRECATED)
        .withSchedule(schedule)
        .withGeography(Geography.AUTO)
        .withBreakingChange(false)
        .withNonBreakingChangesPreference(NonBreakingChangesPreference.IGNORE)
        .withNotifySchemaChanges(true);

    final StandardSync standardSync5 = new StandardSync()
        .withOperationIds(Arrays.asList(OPERATION_ID_3))
        .withConnectionId(CONNECTION_ID_5)
        .withSourceId(SOURCE_ID_3)
        .withDestinationId(DESTINATION_ID_3)
        .withCatalog(getConfiguredCatalog())
        .withName("standard-sync-5")
        .withManual(true)
        .withNamespaceDefinition(NamespaceDefinitionType.CUSTOMFORMAT)
        .withNamespaceFormat("")
        .withPrefix("")
        .withResourceRequirements(resourceRequirements)
        .withStatus(Status.ACTIVE)
        .withSchedule(schedule)
        .withGeography(Geography.AUTO)
        .withBreakingChange(false)
        .withNonBreakingChangesPreference(NonBreakingChangesPreference.IGNORE)
        .withNotifySchemaChanges(true);

    final StandardSync standardSync6 = new StandardSync()
        .withOperationIds(Arrays.asList())
        .withConnectionId(CONNECTION_ID_6)
        .withSourceId(SOURCE_ID_3)
        .withDestinationId(DESTINATION_ID_3)
        .withCatalog(getConfiguredCatalog())
        .withName("standard-sync-6")
        .withManual(true)
        .withNamespaceDefinition(NamespaceDefinitionType.CUSTOMFORMAT)
        .withNamespaceFormat("")
        .withPrefix("")
        .withResourceRequirements(resourceRequirements)
        .withStatus(Status.DEPRECATED)
        .withSchedule(schedule)
        .withGeography(Geography.AUTO)
        .withBreakingChange(false)
        .withNonBreakingChangesPreference(NonBreakingChangesPreference.IGNORE)
        .withNotifySchemaChanges(true);

    return Arrays.asList(standardSync1, standardSync2, standardSync3, standardSync4, standardSync5, standardSync6);
  }

  private static ConfiguredAirbyteCatalog getConfiguredCatalog() {
    final AirbyteCatalog catalog = new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            "models",
            "models_schema",
            io.airbyte.protocol.models.Field.of("id", JsonSchemaType.NUMBER),
            io.airbyte.protocol.models.Field.of("make_id", JsonSchemaType.NUMBER),
            io.airbyte.protocol.models.Field.of("model", JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of("id")))));
    return CatalogHelpers.toDefaultConfiguredCatalog(catalog);
  }

  public static ConfiguredAirbyteCatalog getConfiguredCatalogWithV1DataTypes() {
    final AirbyteCatalog catalog = new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            "models",
            "models_schema",
            io.airbyte.protocol.models.Field.of("id", JsonSchemaType.NUMBER_V1),
            io.airbyte.protocol.models.Field.of("make_id", JsonSchemaType.NUMBER_V1),
            io.airbyte.protocol.models.Field.of("model", JsonSchemaType.STRING_V1))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of("id")))));
    return CatalogHelpers.toDefaultConfiguredCatalog(catalog);
  }

  public static List<StandardSyncState> standardSyncStates() {
    final StandardSyncState standardSyncState1 = new StandardSyncState()
        .withConnectionId(CONNECTION_ID_1)
        .withState(new State().withState(Jsons.jsonNode(CONNECTION_SPECIFICATION)));
    final StandardSyncState standardSyncState2 = new StandardSyncState()
        .withConnectionId(CONNECTION_ID_2)
        .withState(new State().withState(Jsons.jsonNode(CONNECTION_SPECIFICATION)));
    final StandardSyncState standardSyncState3 = new StandardSyncState()
        .withConnectionId(CONNECTION_ID_3)
        .withState(new State().withState(Jsons.jsonNode(CONNECTION_SPECIFICATION)));
    final StandardSyncState standardSyncState4 = new StandardSyncState()
        .withConnectionId(CONNECTION_ID_4)
        .withState(new State().withState(Jsons.jsonNode(CONNECTION_SPECIFICATION)));
    return Arrays.asList(standardSyncState1, standardSyncState2, standardSyncState3, standardSyncState4);
  }

  public static List<ActorCatalog> actorCatalogs() {
    final ActorCatalog actorCatalog1 = new ActorCatalog()
        .withId(ACTOR_CATALOG_ID_1)
        .withCatalog(Jsons.deserialize("{}"))
        .withCatalogHash("TESTHASH");
    final ActorCatalog actorCatalog2 = new ActorCatalog()
        .withId(ACTOR_CATALOG_ID_2)
        .withCatalog(Jsons.deserialize("{}"))
        .withCatalogHash("12345");
    final ActorCatalog actorCatalog3 = new ActorCatalog()
        .withId(ACTOR_CATALOG_ID_3)
        .withCatalog(Jsons.deserialize("{}"))
        .withCatalogHash("SomeOtherHash");
    return Arrays.asList(actorCatalog1, actorCatalog2, actorCatalog3);
  }

  public static List<ActorCatalogFetchEvent> actorCatalogFetchEvents() {
    final ActorCatalogFetchEvent actorCatalogFetchEvent1 = new ActorCatalogFetchEvent()
        .withId(ACTOR_CATALOG_FETCH_EVENT_ID_1)
        .withActorCatalogId(ACTOR_CATALOG_ID_1)
        .withActorId(SOURCE_ID_1)
        .withConfigHash("CONFIG_HASH")
        .withConnectorVersion("1.0.0");
    final ActorCatalogFetchEvent actorCatalogFetchEvent2 = new ActorCatalogFetchEvent()
        .withId(ACTOR_CATALOG_FETCH_EVENT_ID_2)
        .withActorCatalogId(ACTOR_CATALOG_ID_2)
        .withActorId(SOURCE_ID_2)
        .withConfigHash("1395")
        .withConnectorVersion("1.42.0");
    return Arrays.asList(actorCatalogFetchEvent1, actorCatalogFetchEvent2);
  }

  public static List<ActorCatalogFetchEvent> actorCatalogFetchEventsSameSource() {
    final ActorCatalogFetchEvent actorCatalogFetchEvent1 = new ActorCatalogFetchEvent()
        .withId(ACTOR_CATALOG_FETCH_EVENT_ID_1)
        .withActorCatalogId(ACTOR_CATALOG_ID_1)
        .withActorId(SOURCE_ID_1)
        .withConfigHash("CONFIG_HASH")
        .withConnectorVersion("1.0.0");
    final ActorCatalogFetchEvent actorCatalogFetchEvent2 = new ActorCatalogFetchEvent()
        .withId(ACTOR_CATALOG_FETCH_EVENT_ID_2)
        .withActorCatalogId(ACTOR_CATALOG_ID_2)
        .withActorId(SOURCE_ID_1)
        .withConfigHash(CONFIG_HASH)
        .withConnectorVersion(CONNECTOR_VERSION);
    return Arrays.asList(actorCatalogFetchEvent1, actorCatalogFetchEvent2);
  }

  @Data
  public static class ActorCatalogFetchEventWithCreationDate {

    private final ActorCatalogFetchEvent actorCatalogFetchEvent;
    private final OffsetDateTime createdAt;

  }

  public static List<ActorCatalogFetchEventWithCreationDate> actorCatalogFetchEventsForAggregationTest() {
    final OffsetDateTime now = OffsetDateTime.now();
    final OffsetDateTime yesterday = OffsetDateTime.now().minusDays(1l);

    final ActorCatalogFetchEvent actorCatalogFetchEvent1 = new ActorCatalogFetchEvent()
        .withId(ACTOR_CATALOG_FETCH_EVENT_ID_1)
        .withActorCatalogId(ACTOR_CATALOG_ID_1)
        .withActorId(SOURCE_ID_1)
        .withConfigHash("CONFIG_HASH")
        .withConnectorVersion("1.0.0");
    final ActorCatalogFetchEvent actorCatalogFetchEvent2 = new ActorCatalogFetchEvent()
        .withId(ACTOR_CATALOG_FETCH_EVENT_ID_2)
        .withActorCatalogId(ACTOR_CATALOG_ID_2)
        .withActorId(SOURCE_ID_2)
        .withConfigHash(CONFIG_HASH)
        .withConnectorVersion(CONNECTOR_VERSION);
    final ActorCatalogFetchEvent actorCatalogFetchEvent3 = new ActorCatalogFetchEvent()
        .withId(ACTOR_CATALOG_FETCH_EVENT_ID_3)
        .withActorCatalogId(ACTOR_CATALOG_ID_3)
        .withActorId(SOURCE_ID_2)
        .withConfigHash(CONFIG_HASH)
        .withConnectorVersion(CONNECTOR_VERSION);
    final ActorCatalogFetchEvent actorCatalogFetchEvent4 = new ActorCatalogFetchEvent()
        .withId(ACTOR_CATALOG_FETCH_EVENT_ID_3)
        .withActorCatalogId(ACTOR_CATALOG_ID_3)
        .withActorId(SOURCE_ID_3)
        .withConfigHash(CONFIG_HASH)
        .withConnectorVersion(CONNECTOR_VERSION);
    return Arrays.asList(
        new ActorCatalogFetchEventWithCreationDate(actorCatalogFetchEvent1, now),
        new ActorCatalogFetchEventWithCreationDate(actorCatalogFetchEvent2, yesterday),
        new ActorCatalogFetchEventWithCreationDate(actorCatalogFetchEvent3, now),
        new ActorCatalogFetchEventWithCreationDate(actorCatalogFetchEvent4, now));
  }

  public static List<WorkspaceServiceAccount> workspaceServiceAccounts() {
    final WorkspaceServiceAccount workspaceServiceAccount = new WorkspaceServiceAccount()
        .withWorkspaceId(WORKSPACE_ID_1)
        .withHmacKey(HMAC_SECRET_PAYLOAD_1)
        .withServiceAccountId("a1e5ac98-7531-48e1-943b-b46636")
        .withServiceAccountEmail("a1e5ac98-7531-48e1-943b-b46636@random-gcp-project.abc.abcdefghijklmno.com")
        .withJsonCredential(Jsons.deserialize(MOCK_SERVICE_ACCOUNT_1));

    return Arrays.asList(workspaceServiceAccount);
  }

  private static Map<String, String> sortMap(final Map<String, String> originalMap) {
    return originalMap.entrySet().stream()
        .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue, (oldValue, newValue) -> newValue, TreeMap::new));
  }

  public static Instant now() {
    return NOW;
  }

}
