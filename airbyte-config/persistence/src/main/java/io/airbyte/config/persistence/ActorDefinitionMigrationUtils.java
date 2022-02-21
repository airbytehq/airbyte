/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ActorDefinition;
import io.airbyte.config.ActorDefinition.ActorType;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;

/**
 * Helpers for migration of StandardSourceDefinition, StandardDefinitionDefinition to
 * ActorDefinition. Remove after migration.
 */
public class ActorDefinitionMigrationUtils {

  // todo (cgardens) - while we are migrating to ActorDefinitions, we have a shim layer in
  // ConfigRepository to convert from ActorDefinition (used internally in the db) and
  // StandardSourceDefinition, used externally.
  public static StandardSourceDefinition mapActorDefToSourceDef(final ActorDefinition actorDefinition) {
    System.out.println("actorDefinition.getActorType() = " + actorDefinition.getActorType());
    Preconditions.checkArgument(actorDefinition.getActorType() == ActorType.SOURCE);
    return new StandardSourceDefinition()
        .withName(actorDefinition.getName())
        .withSourceDefinitionId(actorDefinition.getId())
        .withDockerRepository(actorDefinition.getDockerRepository())
        .withDockerImageTag(actorDefinition.getDockerImageTag())
        .withDocumentationUrl(actorDefinition.getDocumentationUrl())
        .withIcon(actorDefinition.getIcon())
        .withSpec(actorDefinition.getSpec())
        .withSourceType(actorDefinition.getSourceType())
        .withTombstone(actorDefinition.getTombstone())
        .withReleaseStage(actorDefinition.getReleaseStage())
        .withReleaseDate(actorDefinition.getReleaseDate())
        .withResourceRequirements(actorDefinition.getResourceRequirements());
  }

  // todo (cgardens) - while we are migrating to ActorDefinitions, we have a shim layer in
  // ConfigRepository to convert from ActorDefinition (used internally in the db) and
  // StandardSourceDefinition, used externally.
  public static ActorDefinition mapSourceDefToActorDef(final StandardSourceDefinition sourceDefinition) {
    return new ActorDefinition()
        .withName(sourceDefinition.getName())
        .withId(sourceDefinition.getSourceDefinitionId())
        .withActorType(ActorType.SOURCE)
        .withDockerRepository(sourceDefinition.getDockerRepository())
        .withDockerImageTag(sourceDefinition.getDockerImageTag())
        .withDocumentationUrl(sourceDefinition.getDocumentationUrl())
        .withIcon(sourceDefinition.getIcon())
        .withSpec(sourceDefinition.getSpec())
        .withSourceType(sourceDefinition.getSourceType())
        .withTombstone(sourceDefinition.getTombstone())
        .withReleaseStage(sourceDefinition.getReleaseStage())
        .withReleaseDate(sourceDefinition.getReleaseDate())
        .withResourceRequirements(sourceDefinition.getResourceRequirements());
  }

  // todo (cgardens) - while we are migrating to ActorDefinitions, we have a shim layer in
  // ConfigRepository to convert from ActorDefinition (used internally in the db) and
  // StandardDestinationDefinition, used externally.
  public static StandardDestinationDefinition mapActorDefToDestDef(final ActorDefinition actorDefinition) {
    Preconditions.checkArgument(actorDefinition.getActorType() == ActorType.DESTINATION);
    return new StandardDestinationDefinition()
        .withName(actorDefinition.getName())
        .withDestinationDefinitionId(actorDefinition.getId())
        .withDockerRepository(actorDefinition.getDockerRepository())
        .withDockerImageTag(actorDefinition.getDockerImageTag())
        .withDocumentationUrl(actorDefinition.getDocumentationUrl())
        .withIcon(actorDefinition.getIcon())
        .withSpec(actorDefinition.getSpec())
        .withTombstone(actorDefinition.getTombstone())
        .withReleaseStage(actorDefinition.getReleaseStage())
        .withReleaseDate(actorDefinition.getReleaseDate())
        .withResourceRequirements(actorDefinition.getResourceRequirements());
  }

  // todo (cgardens) - while we are migrating to ActorDefinitions, we have a shim layer in
  // ConfigRepository to convert from ActorDefinition (used internally in the db) and
  // StandardSourceDefinition, used externally.
  public static ActorDefinition mapDestDefToActorDef(final StandardDestinationDefinition destDefinition) {
    return new ActorDefinition()
        .withName(destDefinition.getName())
        .withId(destDefinition.getDestinationDefinitionId())
        .withActorType(ActorType.DESTINATION)
        .withDockerRepository(destDefinition.getDockerRepository())
        .withDockerImageTag(destDefinition.getDockerImageTag())
        .withDocumentationUrl(destDefinition.getDocumentationUrl())
        .withIcon(destDefinition.getIcon())
        .withSpec(destDefinition.getSpec())
        .withTombstone(destDefinition.getTombstone())
        .withReleaseStage(destDefinition.getReleaseStage())
        .withReleaseDate(destDefinition.getReleaseDate())
        .withResourceRequirements(destDefinition.getResourceRequirements());
  }

  /**
   * If an object is stored as a StandardSourceDefinition or StandardDestinationDefinition, map it to
   * an ActorDefinition. The ConfigPersistence iface should deal only in ActorDefinitions going
   * forward. In all other cases, returns the original object.
   *
   * This is a shim until we update the yaml to match the actor definition format.
   *
   * @param configType - type of the config
   * @param json - object to maybe convert
   * @return object after conversion
   */
  public static JsonNode convertIfNeeded(final AirbyteConfig configType, final JsonNode json) {
    if (configType == ConfigSchema.STANDARD_SOURCE_DEFINITION) {
      // detect if it is using ActorDefinition or StandardSourceDefinition. If StandardSourceDefinition,
      // normalize it to ActorDefinition.
      if (json.has("sourceDefinitionId")) {
        return Jsons.jsonNode(mapSourceDefToActorDef(Jsons.object(json, StandardSourceDefinition.class)));
      } else {
        return json;
      }
    } else if (configType == ConfigSchema.STANDARD_DESTINATION_DEFINITION) {
      // detect if it is using ActorDefinition or StandardDestinationDefinition. If
      // StandardDestinationDefinition, normalize it to ActorDefinition.
      if (json.has("destinationDefinitionId")) {
        return Jsons.jsonNode(mapDestDefToActorDef(Jsons.object(json, StandardDestinationDefinition.class)));
      } else {
        return json;
      }
    } else {
      return json;
    }
  }

}
