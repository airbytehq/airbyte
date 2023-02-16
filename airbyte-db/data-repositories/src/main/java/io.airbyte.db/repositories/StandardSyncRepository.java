/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.repositories;

import io.airbyte.db.models.StandardSyncModel;
import io.micronaut.data.annotation.Repository;
import io.micronaut.data.repository.PageableRepository;
import java.util.UUID;

@Repository
public interface StandardSyncRepository extends PageableRepository<StandardSyncModel, UUID> {}
