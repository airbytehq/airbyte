/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
