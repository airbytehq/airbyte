/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.models;

import io.micronaut.core.annotation.NonNull;
import io.micronaut.data.annotation.GeneratedValue;
import io.micronaut.data.annotation.Id;
import io.micronaut.data.annotation.MappedEntity;

import javax.persistence.Entity;
import java.util.UUID;

@MappedEntity
@Entity(name="connection")
public class StandardSyncModel {
  @NonNull
  public UUID getId() {
    return id;
  }

  public void setId(@NonNull final UUID id) {
    this.id = id;
  }

  @NonNull
  public String getName() {
    return name;
  }

  public void setName(@NonNull final String name) {
    this.name = name;
  }

  @GeneratedValue
  @NonNull @javax.persistence.Id @Id UUID id;
  @NonNull String name;

  public StandardSyncModel() {
  }

  public StandardSyncModel(@NonNull final UUID id, @NonNull final String name) {
    this.id = id;
    this.name = name;
  }

}