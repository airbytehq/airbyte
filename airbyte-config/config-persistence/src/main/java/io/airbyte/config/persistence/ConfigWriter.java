/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_DEFINITION;

import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.Version;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.db.instance.configs.jooq.generated.Tables;
import io.airbyte.db.instance.configs.jooq.generated.enums.ActorType;
import io.airbyte.db.instance.configs.jooq.generated.enums.ReleaseStage;
import io.airbyte.db.instance.configs.jooq.generated.enums.SourceType;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.*;
import java.util.Map.Entry;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.jooq.Record4;
import org.jooq.impl.DSL;

/**
 * This class can be used to store DB queries for persisting configs that we may want to reuse
 * across this package.
 * <p>
 * Currently this class is used to move write queries out of {@link ConfigPersistence} so that they
 * can be reused/composed in {@link ConfigRepository}.
 */
@SuppressWarnings("PMD.CognitiveComplexity")
public class ConfigWriter {

  /**
   * @return A set of connectors (both source and destination) that are already used in standard
   *         syncs. We identify connectors by its repository name instead of definition id because
   *         connectors can be added manually by users, and their config ids are not always the same
   *         as those in the seed.
   */
  static Set<String> getConnectorRepositoriesInUse(final DSLContext ctx) {
    return getActorDefinitionsInUse(ctx)
        .map(r -> r.get(ACTOR_DEFINITION.DOCKER_REPOSITORY))
        .collect(Collectors.toSet());
  }

  /**
   * Get a map of connector to protocol version for all the connectors that are used in a standard
   * syncs.
   */
  static Map<UUID, Entry<io.airbyte.config.ActorType, Version>> getActorDefinitionsInUseToProtocolVersion(final DSLContext ctx) {
    return getActorDefinitionsInUse(ctx)
        .collect(Collectors.toMap(r -> r.get(ACTOR_DEFINITION.ID),
            r -> Map.entry(
                r.get(ACTOR_DEFINITION.ACTOR_TYPE) == ActorType.source ? io.airbyte.config.ActorType.SOURCE : io.airbyte.config.ActorType.DESTINATION,
                AirbyteProtocolVersion.getWithDefault(r.get(ACTOR_DEFINITION.PROTOCOL_VERSION))),
            // We may have duplicated entries from the data. We can pick any values in the merge function
            (lhs, rhs) -> lhs));
  }

  private static Stream<Record4<UUID, String, ActorType, String>> getActorDefinitionsInUse(final DSLContext ctx) {
    return ctx.select(ACTOR_DEFINITION.ID, ACTOR_DEFINITION.DOCKER_REPOSITORY, ACTOR_DEFINITION.ACTOR_TYPE, ACTOR_DEFINITION.PROTOCOL_VERSION)
        .from(ACTOR_DEFINITION)
        .join(ACTOR).on(ACTOR.ACTOR_DEFINITION_ID.equal(ACTOR_DEFINITION.ID))
        .fetch()
        .stream();
  }

  static void writeStandardSourceDefinition(final List<StandardSourceDefinition> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((standardSourceDefinition) -> {
      final boolean isExistingConfig = ctx.fetchExists(DSL.select()
          .from(Tables.ACTOR_DEFINITION)
          .where(Tables.ACTOR_DEFINITION.ID.eq(standardSourceDefinition.getSourceDefinitionId())));

      if (isExistingConfig) {
        ctx.update(Tables.ACTOR_DEFINITION)
            .set(Tables.ACTOR_DEFINITION.ID, standardSourceDefinition.getSourceDefinitionId())
            .set(Tables.ACTOR_DEFINITION.NAME, standardSourceDefinition.getName())
            .set(Tables.ACTOR_DEFINITION.DOCKER_REPOSITORY, standardSourceDefinition.getDockerRepository())
            .set(Tables.ACTOR_DEFINITION.DOCKER_IMAGE_TAG, standardSourceDefinition.getDockerImageTag())
            .set(Tables.ACTOR_DEFINITION.DOCUMENTATION_URL, standardSourceDefinition.getDocumentationUrl())
            .set(Tables.ACTOR_DEFINITION.ICON, standardSourceDefinition.getIcon())
            .set(Tables.ACTOR_DEFINITION.ACTOR_TYPE, ActorType.source)
            .set(Tables.ACTOR_DEFINITION.SOURCE_TYPE,
                standardSourceDefinition.getSourceType() == null ? null
                    : Enums.toEnum(standardSourceDefinition.getSourceType().value(),
                        SourceType.class).orElseThrow())
            .set(Tables.ACTOR_DEFINITION.SPEC, JSONB.valueOf(Jsons.serialize(standardSourceDefinition.getSpec())))
            .set(Tables.ACTOR_DEFINITION.PROTOCOL_VERSION, standardSourceDefinition.getProtocolVersion())
            .set(Tables.ACTOR_DEFINITION.TOMBSTONE, standardSourceDefinition.getTombstone())
            .set(Tables.ACTOR_DEFINITION.PUBLIC, standardSourceDefinition.getPublic())
            .set(Tables.ACTOR_DEFINITION.CUSTOM, standardSourceDefinition.getCustom())
            .set(Tables.ACTOR_DEFINITION.RELEASE_STAGE, standardSourceDefinition.getReleaseStage() == null ? null
                : Enums.toEnum(standardSourceDefinition.getReleaseStage().value(),
                    ReleaseStage.class).orElseThrow())
            .set(Tables.ACTOR_DEFINITION.RELEASE_DATE, standardSourceDefinition.getReleaseDate() == null ? null
                : LocalDate.parse(standardSourceDefinition.getReleaseDate()))
            .set(Tables.ACTOR_DEFINITION.RESOURCE_REQUIREMENTS,
                standardSourceDefinition.getResourceRequirements() == null ? null
                    : JSONB.valueOf(Jsons.serialize(standardSourceDefinition.getResourceRequirements())))
            .set(Tables.ACTOR_DEFINITION.ALLOWED_HOSTS, standardSourceDefinition.getAllowedHosts() == null ? null
                : JSONB.valueOf(Jsons.serialize(standardSourceDefinition.getAllowedHosts())))
            .set(ACTOR_DEFINITION.SUGGESTED_STREAMS, standardSourceDefinition.getSuggestedStreams() == null ? null
                : JSONB.valueOf(Jsons.serialize(standardSourceDefinition.getSuggestedStreams())))
            .set(Tables.ACTOR_DEFINITION.UPDATED_AT, timestamp)
            .where(Tables.ACTOR_DEFINITION.ID.eq(standardSourceDefinition.getSourceDefinitionId()))
            .execute();

      } else {
        ctx.insertInto(Tables.ACTOR_DEFINITION)
            .set(Tables.ACTOR_DEFINITION.ID, standardSourceDefinition.getSourceDefinitionId())
            .set(Tables.ACTOR_DEFINITION.NAME, standardSourceDefinition.getName())
            .set(Tables.ACTOR_DEFINITION.DOCKER_REPOSITORY, standardSourceDefinition.getDockerRepository())
            .set(Tables.ACTOR_DEFINITION.DOCKER_IMAGE_TAG, standardSourceDefinition.getDockerImageTag())
            .set(Tables.ACTOR_DEFINITION.DOCUMENTATION_URL, standardSourceDefinition.getDocumentationUrl())
            .set(Tables.ACTOR_DEFINITION.ICON, standardSourceDefinition.getIcon())
            .set(Tables.ACTOR_DEFINITION.ACTOR_TYPE, ActorType.source)
            .set(Tables.ACTOR_DEFINITION.SOURCE_TYPE,
                standardSourceDefinition.getSourceType() == null ? null
                    : Enums.toEnum(standardSourceDefinition.getSourceType().value(),
                        SourceType.class).orElseThrow())
            .set(Tables.ACTOR_DEFINITION.SPEC, JSONB.valueOf(Jsons.serialize(standardSourceDefinition.getSpec())))
            .set(Tables.ACTOR_DEFINITION.PROTOCOL_VERSION, standardSourceDefinition.getProtocolVersion())
            .set(Tables.ACTOR_DEFINITION.TOMBSTONE, standardSourceDefinition.getTombstone() != null && standardSourceDefinition.getTombstone())
            .set(Tables.ACTOR_DEFINITION.PUBLIC, standardSourceDefinition.getPublic())
            .set(Tables.ACTOR_DEFINITION.CUSTOM, standardSourceDefinition.getCustom())
            .set(Tables.ACTOR_DEFINITION.RELEASE_STAGE,
                standardSourceDefinition.getReleaseStage() == null ? null
                    : Enums.toEnum(standardSourceDefinition.getReleaseStage().value(),
                        ReleaseStage.class).orElseThrow())
            .set(Tables.ACTOR_DEFINITION.RELEASE_DATE, standardSourceDefinition.getReleaseDate() == null ? null
                : LocalDate.parse(standardSourceDefinition.getReleaseDate()))
            .set(Tables.ACTOR_DEFINITION.RESOURCE_REQUIREMENTS,
                standardSourceDefinition.getResourceRequirements() == null ? null
                    : JSONB.valueOf(Jsons.serialize(standardSourceDefinition.getResourceRequirements())))
            .set(ACTOR_DEFINITION.ALLOWED_HOSTS, standardSourceDefinition.getAllowedHosts() == null ? null
                : JSONB.valueOf(Jsons.serialize(standardSourceDefinition.getAllowedHosts())))
            .set(ACTOR_DEFINITION.SUGGESTED_STREAMS, standardSourceDefinition.getSuggestedStreams() == null ? null
                : JSONB.valueOf(Jsons.serialize(standardSourceDefinition.getSuggestedStreams())))
            .set(Tables.ACTOR_DEFINITION.CREATED_AT, timestamp)
            .set(Tables.ACTOR_DEFINITION.UPDATED_AT, timestamp)
            .execute();
      }
    });
  }

  static void writeStandardDestinationDefinition(final List<StandardDestinationDefinition> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((standardDestinationDefinition) -> {
      final boolean isExistingConfig = ctx.fetchExists(DSL.select()
          .from(Tables.ACTOR_DEFINITION)
          .where(Tables.ACTOR_DEFINITION.ID.eq(standardDestinationDefinition.getDestinationDefinitionId())));

      if (isExistingConfig) {
        ctx.update(Tables.ACTOR_DEFINITION)
            .set(Tables.ACTOR_DEFINITION.ID, standardDestinationDefinition.getDestinationDefinitionId())
            .set(Tables.ACTOR_DEFINITION.NAME, standardDestinationDefinition.getName())
            .set(Tables.ACTOR_DEFINITION.DOCKER_REPOSITORY, standardDestinationDefinition.getDockerRepository())
            .set(Tables.ACTOR_DEFINITION.DOCKER_IMAGE_TAG, standardDestinationDefinition.getDockerImageTag())
            .set(Tables.ACTOR_DEFINITION.DOCUMENTATION_URL, standardDestinationDefinition.getDocumentationUrl())
            .set(Tables.ACTOR_DEFINITION.ICON, standardDestinationDefinition.getIcon())
            .set(Tables.ACTOR_DEFINITION.ACTOR_TYPE, ActorType.destination)
            .set(Tables.ACTOR_DEFINITION.SPEC, JSONB.valueOf(Jsons.serialize(standardDestinationDefinition.getSpec())))
            .set(Tables.ACTOR_DEFINITION.PROTOCOL_VERSION, standardDestinationDefinition.getProtocolVersion())
            .set(Tables.ACTOR_DEFINITION.TOMBSTONE, standardDestinationDefinition.getTombstone())
            .set(Tables.ACTOR_DEFINITION.PUBLIC, standardDestinationDefinition.getPublic())
            .set(Tables.ACTOR_DEFINITION.CUSTOM, standardDestinationDefinition.getCustom())
            .set(Tables.ACTOR_DEFINITION.RELEASE_STAGE, standardDestinationDefinition.getReleaseStage() == null ? null
                : Enums.toEnum(standardDestinationDefinition.getReleaseStage().value(),
                    ReleaseStage.class).orElseThrow())
            .set(Tables.ACTOR_DEFINITION.RELEASE_DATE, standardDestinationDefinition.getReleaseDate() == null ? null
                : LocalDate.parse(standardDestinationDefinition.getReleaseDate()))
            .set(Tables.ACTOR_DEFINITION.RESOURCE_REQUIREMENTS,
                standardDestinationDefinition.getResourceRequirements() == null ? null
                    : JSONB.valueOf(Jsons.serialize(standardDestinationDefinition.getResourceRequirements())))
            .set(Tables.ACTOR_DEFINITION.NORMALIZATION_REPOSITORY,
                Objects.nonNull(standardDestinationDefinition.getNormalizationConfig())
                    ? standardDestinationDefinition.getNormalizationConfig().getNormalizationRepository()
                    : null)
            .set(Tables.ACTOR_DEFINITION.NORMALIZATION_TAG,
                Objects.nonNull(standardDestinationDefinition.getNormalizationConfig())
                    ? standardDestinationDefinition.getNormalizationConfig().getNormalizationTag()
                    : null)
            .set(Tables.ACTOR_DEFINITION.SUPPORTS_DBT, standardDestinationDefinition.getSupportsDbt())
            .set(Tables.ACTOR_DEFINITION.NORMALIZATION_INTEGRATION_TYPE,
                Objects.nonNull(standardDestinationDefinition.getNormalizationConfig())
                    ? standardDestinationDefinition.getNormalizationConfig().getNormalizationIntegrationType()
                    : null)
            .set(ACTOR_DEFINITION.ALLOWED_HOSTS, standardDestinationDefinition.getAllowedHosts() == null ? null
                : JSONB.valueOf(Jsons.serialize(standardDestinationDefinition.getAllowedHosts())))
            .set(Tables.ACTOR_DEFINITION.UPDATED_AT, timestamp)
            .where(Tables.ACTOR_DEFINITION.ID.eq(standardDestinationDefinition.getDestinationDefinitionId()))
            .execute();

      } else {
        ctx.insertInto(Tables.ACTOR_DEFINITION)
            .set(Tables.ACTOR_DEFINITION.ID, standardDestinationDefinition.getDestinationDefinitionId())
            .set(Tables.ACTOR_DEFINITION.NAME, standardDestinationDefinition.getName())
            .set(Tables.ACTOR_DEFINITION.DOCKER_REPOSITORY, standardDestinationDefinition.getDockerRepository())
            .set(Tables.ACTOR_DEFINITION.DOCKER_IMAGE_TAG, standardDestinationDefinition.getDockerImageTag())
            .set(Tables.ACTOR_DEFINITION.DOCUMENTATION_URL, standardDestinationDefinition.getDocumentationUrl())
            .set(Tables.ACTOR_DEFINITION.ICON, standardDestinationDefinition.getIcon())
            .set(Tables.ACTOR_DEFINITION.ACTOR_TYPE, ActorType.destination)
            .set(Tables.ACTOR_DEFINITION.SPEC, JSONB.valueOf(Jsons.serialize(standardDestinationDefinition.getSpec())))
            .set(Tables.ACTOR_DEFINITION.PROTOCOL_VERSION, standardDestinationDefinition.getProtocolVersion())
            .set(Tables.ACTOR_DEFINITION.TOMBSTONE,
                standardDestinationDefinition.getTombstone() != null && standardDestinationDefinition.getTombstone())
            .set(Tables.ACTOR_DEFINITION.PUBLIC, standardDestinationDefinition.getPublic())
            .set(Tables.ACTOR_DEFINITION.CUSTOM, standardDestinationDefinition.getCustom())
            .set(Tables.ACTOR_DEFINITION.RELEASE_STAGE,
                standardDestinationDefinition.getReleaseStage() == null ? null
                    : Enums.toEnum(standardDestinationDefinition.getReleaseStage().value(),
                        ReleaseStage.class).orElseThrow())
            .set(Tables.ACTOR_DEFINITION.RELEASE_DATE, standardDestinationDefinition.getReleaseDate() == null ? null
                : LocalDate.parse(standardDestinationDefinition.getReleaseDate()))
            .set(Tables.ACTOR_DEFINITION.RESOURCE_REQUIREMENTS,
                standardDestinationDefinition.getResourceRequirements() == null ? null
                    : JSONB.valueOf(Jsons.serialize(standardDestinationDefinition.getResourceRequirements())))
            .set(Tables.ACTOR_DEFINITION.NORMALIZATION_REPOSITORY,
                Objects.nonNull(standardDestinationDefinition.getNormalizationConfig())
                    ? standardDestinationDefinition.getNormalizationConfig().getNormalizationRepository()
                    : null)
            .set(Tables.ACTOR_DEFINITION.NORMALIZATION_TAG,
                Objects.nonNull(standardDestinationDefinition.getNormalizationConfig())
                    ? standardDestinationDefinition.getNormalizationConfig().getNormalizationTag()
                    : null)
            .set(Tables.ACTOR_DEFINITION.SUPPORTS_DBT, standardDestinationDefinition.getSupportsDbt())
            .set(Tables.ACTOR_DEFINITION.NORMALIZATION_INTEGRATION_TYPE,
                Objects.nonNull(standardDestinationDefinition.getNormalizationConfig())
                    ? standardDestinationDefinition.getNormalizationConfig().getNormalizationIntegrationType()
                    : null)
            .set(ACTOR_DEFINITION.ALLOWED_HOSTS, standardDestinationDefinition.getAllowedHosts() == null ? null
                : JSONB.valueOf(Jsons.serialize(standardDestinationDefinition.getAllowedHosts())))
            .set(Tables.ACTOR_DEFINITION.CREATED_AT, timestamp)
            .set(Tables.ACTOR_DEFINITION.UPDATED_AT, timestamp)
            .execute();
      }
    });
  }

}
