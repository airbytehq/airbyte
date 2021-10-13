/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.manifest;

import java.util.List;

public class Manifest {

  public final List<Entry> entries;

  public Manifest(List<Entry> entries) {
    this.entries = entries;
  }

}
