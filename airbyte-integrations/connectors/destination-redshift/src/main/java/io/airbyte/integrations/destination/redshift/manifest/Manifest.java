/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.manifest;

import java.util.List;

public class Manifest {

  public final List<Entry> entries;

  public Manifest(final List<Entry> entries) {
    this.entries = entries;
  }

}
