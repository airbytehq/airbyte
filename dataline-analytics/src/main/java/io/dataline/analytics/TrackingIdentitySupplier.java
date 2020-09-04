/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.analytics;

import io.dataline.config.ConfigSchema;
import io.dataline.config.StandardWorkspace;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConstants;
import java.io.IOException;
import java.util.function.Supplier;

public class TrackingIdentitySupplier implements Supplier<TrackingIdentity> {

  private final ConfigPersistence configPersistence;

  public TrackingIdentitySupplier(ConfigPersistence configPersistence) {
    this.configPersistence = configPersistence;
  }

  @Override
  public TrackingIdentity get() {
    try {
      final StandardWorkspace workspace = configPersistence.getConfig(
          ConfigSchema.STANDARD_WORKSPACE,
          PersistenceConstants.DEFAULT_WORKSPACE_ID.toString(),
          StandardWorkspace.class);

      String email = null;
      if (workspace.getAnonymousDataCollection() != null && !workspace.getAnonymousDataCollection()) {
        email = workspace.getEmail();
      }
      return new TrackingIdentity(workspace.getCustomerId(), email);
    } catch (ConfigNotFoundException e) {
      throw new RuntimeException("could not find workspace with id: " + PersistenceConstants.DEFAULT_WORKSPACE_ID, e);
    } catch (JsonValidationException | IOException e) {
      throw new RuntimeException(e);
    }
  }

}
