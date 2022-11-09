/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api.server.repositories.impl;

import io.airbyte.api.server.repositories.ConnectionsRepository;
import io.micronaut.data.annotation.Repository;
import java.util.UUID;
import javax.validation.constraints.NotBlank;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.NotImplementedException;

@Repository
@Slf4j
public class ConnectionsRepositoryImpl implements ConnectionsRepository {

  @Override
  public void sync(@NotBlank final UUID connectionId) {
    throw new NotImplementedException();
  }

  @Override
  public void reset(@NotBlank final UUID connectionId) {
    throw new NotImplementedException();
  }

}
