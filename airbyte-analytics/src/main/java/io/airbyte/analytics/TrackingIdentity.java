/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.analytics;

import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

public class TrackingIdentity {

  private final String airbyteVersion;
  private final UUID customerId;
  private final String email;
  private final Boolean anonymousDataCollection;
  private final Boolean news;
  private final Boolean securityUpdates;

  public static TrackingIdentity empty() {
    return new TrackingIdentity(null, null, null, null, null, null);
  }

  public TrackingIdentity(
                          final String airbyteVersion,
                          final UUID customerId,
                          final String email,
                          final Boolean anonymousDataCollection,
                          final Boolean news,
                          final Boolean securityUpdates) {
    this.airbyteVersion = airbyteVersion;
    this.customerId = customerId;
    this.email = email;
    this.anonymousDataCollection = anonymousDataCollection;
    this.news = news;
    this.securityUpdates = securityUpdates;
  }

  public String getAirbyteVersion() {
    return airbyteVersion;
  }

  public UUID getCustomerId() {
    return customerId;
  }

  public Optional<String> getEmail() {
    return Optional.ofNullable(email);
  }

  public boolean isAnonymousDataCollection() {
    return anonymousDataCollection != null && anonymousDataCollection;
  }

  public boolean isNews() {
    return news != null && news;
  }

  public boolean isSecurityUpdates() {
    return securityUpdates != null && securityUpdates;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    TrackingIdentity that = (TrackingIdentity) o;
    return anonymousDataCollection == that.anonymousDataCollection &&
        news == that.news &&
        securityUpdates == that.securityUpdates &&
        Objects.equals(customerId, that.customerId) &&
        Objects.equals(email, that.email);
  }

  @Override
  public int hashCode() {
    return Objects.hash(customerId, email, anonymousDataCollection, news, securityUpdates);
  }

}
