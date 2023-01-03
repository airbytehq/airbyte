/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job.models;

import java.util.Objects;

public class JobWithStatusAndTimestamp {

  private final long id;
  private final JobStatus status;
  private final long createdAtInSecond;
  private final long updatedAtInSecond;

  public JobWithStatusAndTimestamp(final long id,
                                   final JobStatus status,
                                   final long createdAtInSecond,
                                   final long updatedAtInSecond) {
    this.id = id;
    this.status = status;
    this.createdAtInSecond = createdAtInSecond;
    this.updatedAtInSecond = updatedAtInSecond;
  }

  public long getId() {
    return id;
  }

  public JobStatus getStatus() {
    return status;
  }

  public long getCreatedAtInSecond() {
    return createdAtInSecond;
  }

  public long getUpdatedAtInSecond() {
    return updatedAtInSecond;
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final JobWithStatusAndTimestamp jobWithStatusAndTimestamp = (JobWithStatusAndTimestamp) o;
    return id == jobWithStatusAndTimestamp.id &&
        status == jobWithStatusAndTimestamp.status &&
        createdAtInSecond == jobWithStatusAndTimestamp.createdAtInSecond &&
        updatedAtInSecond == jobWithStatusAndTimestamp.updatedAtInSecond;
  }

  @Override
  public int hashCode() {
    return Objects.hash(id, status, createdAtInSecond, updatedAtInSecond);
  }

  @Override
  public String toString() {
    return "Job{" +
        "id=" + id +
        ", status=" + status +
        ", createdAtInSecond=" + createdAtInSecond +
        ", updatedAtInSecond=" + updatedAtInSecond +
        '}';
  }

}
