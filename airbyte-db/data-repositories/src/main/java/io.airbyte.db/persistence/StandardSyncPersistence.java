/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.persistence;

import io.airbyte.config.StandardSync;
import io.airbyte.db.models.StandardSyncModel;
import io.airbyte.db.repositories.StandardSyncRepository;
import io.micronaut.data.model.Page;
import io.micronaut.data.model.Pageable;
import jakarta.inject.Singleton;

import java.util.List;
import java.util.UUID;

@Singleton
public class StandardSyncPersistence {

  // private record StandardSyncIdsWithProtocolVersions(
  // UUID standardSyncId,
  // UUID sourceDefId,
  // Version sourceProtocolVersion,
  // UUID destinationDefId,
  // Version destinationProtocolVersion) {}

  private final StandardSyncRepository standardSyncRepository;

  public StandardSyncPersistence(final StandardSyncRepository standardSyncRepository) {
    this.standardSyncRepository = standardSyncRepository;

  }

  public StandardSync getStandardSync(final UUID connectionId) {
    final StandardSyncModel standardSyncModel = standardSyncRepository.findById(connectionId).get();
    return toStandardSync(standardSyncModel);
    // return toStandardSync(standardSyncRepository.findById(connectionId));
  }

  public List<StandardSync> getStandardSyncs(final Pageable pageable) {
//    return standardSyncRepository.findAll(Pageable.from(0, 1)).map(this::toStandardSync);
    return standardSyncRepository.findAll(pageable).getContent().stream().map(this::toStandardSync).toList();
//    Iterable<StandardSyncModel> syncModels = standardSyncRepository.findAll();
//    List<StandardSync> list = new ArrayList<StandardSync>();
//    for (StandardSyncModel model : syncModels) {
//      StandardSync standardSync = toStandardSync(model);
//      list.add(standardSync);
//    }
//    return list.stream().toList();
  }

  private StandardSync toStandardSync(final StandardSyncModel model) {
    return new StandardSync().withConnectionId(model.getId()).withName(model.getName());
  }
}
