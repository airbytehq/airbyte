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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.dataline.config.ConfigSchema;
import io.dataline.config.StandardWorkspace;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConstants;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class TrackingIdentitySupplierTest {

  private ConfigPersistence configPersistence;
  private TrackingIdentitySupplier supplier;

  @BeforeEach
  void setup() {
    configPersistence = mock(ConfigPersistence.class);
    supplier = new TrackingIdentitySupplier(configPersistence);
  }

  @Test
  void testGetTrackingIdentityInitialSetupNotComplete() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardWorkspace workspace = new StandardWorkspace().withCustomerId(UUID.randomUUID());

    when(configPersistence.getConfig(
        ConfigSchema.STANDARD_WORKSPACE,
        PersistenceConstants.DEFAULT_WORKSPACE_ID.toString(),
        StandardWorkspace.class)).thenReturn(workspace);

    final TrackingIdentity actual = supplier.get();
    final TrackingIdentity expected = new TrackingIdentity(workspace.getCustomerId(), null);

    assertEquals(expected, actual);
  }

  @Test
  void testGetTrackingIdentityNonAnonymous() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardWorkspace workspace = new StandardWorkspace()
        .withCustomerId(UUID.randomUUID())
        .withEmail("a@dataline.io")
        .withAnonymousDataCollection(false);

    when(configPersistence.getConfig(
        ConfigSchema.STANDARD_WORKSPACE,
        PersistenceConstants.DEFAULT_WORKSPACE_ID.toString(),
        StandardWorkspace.class)).thenReturn(workspace);

    final TrackingIdentity actual = supplier.get();
    final TrackingIdentity expected = new TrackingIdentity(workspace.getCustomerId(), workspace.getEmail());

    assertEquals(expected, actual);
  }

  @Test
  void testGetTrackingIdentityAnonymous() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardWorkspace workspace = new StandardWorkspace()
        .withCustomerId(UUID.randomUUID())
        .withEmail("a@dataline.io")
        .withAnonymousDataCollection(true);

    when(configPersistence.getConfig(
        ConfigSchema.STANDARD_WORKSPACE,
        PersistenceConstants.DEFAULT_WORKSPACE_ID.toString(),
        StandardWorkspace.class)).thenReturn(workspace);

    final TrackingIdentity actual = supplier.get();
    final TrackingIdentity expected = new TrackingIdentity(workspace.getCustomerId(), null);

    assertEquals(expected, actual);
  }

}
