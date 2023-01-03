/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.repositories.routes;

import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.db.repositories.persistence.StandardSyncPersistence;
import io.micronaut.data.model.Page;
import io.micronaut.data.model.Pageable;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Get;
import java.io.IOException;
import java.util.List;
import lombok.extern.slf4j.Slf4j;

@Controller("/standardSync")
@Slf4j
public class StandardSyncController {

  protected final StandardSyncPersistence standardSyncPersistence;

  public StandardSyncController(StandardSyncPersistence standardSyncPersistence) {
    this.standardSyncPersistence = standardSyncPersistence;
  }

  // @Get("/{id}")
  // public StandardSync byId(UUID connectionId) throws ConfigNotFoundException, IOException {
  // return standardSyncPersistence.getStandardSync(connectionId);
  // }

  @Get("/")
  public List<StandardSync> findAll(Pageable pageable) throws ConfigNotFoundException, IOException {
    return standardSyncPersistence.getStandardSyncs(pageable);
  }

  @Get("/test")
  public String test() {
    return "Testing";
  }

}
