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

package io.airbyte.config;

import static org.mockito.Mockito.when;

import java.nio.file.Paths;
import java.util.List;
import java.util.function.Function;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class EnvConfigsTest {

  private Function<String, String> function;
  private EnvConfigs config;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() {
    function = Mockito.mock(Function.class);
    config = new EnvConfigs(function);
  }

  @Test
  void ensureGetEnvBehavior() {
    Assertions.assertNull(System.getenv("MY_RANDOM_VAR_1234"));
  }

  @Test
  void testAirbyteRole() {
    when(function.apply(EnvConfigs.AIRBYTE_ROLE)).thenReturn(null);
    Assertions.assertNull(config.getAirbyteRole());

    when(function.apply(EnvConfigs.AIRBYTE_ROLE)).thenReturn("dev");
    Assertions.assertEquals("dev", config.getAirbyteRole());
  }

  @Test
  void testAirbyteVersion() {
    when(function.apply(EnvConfigs.AIRBYTE_VERSION)).thenReturn(null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getAirbyteVersion());

    when(function.apply(EnvConfigs.AIRBYTE_VERSION)).thenReturn("dev");
    Assertions.assertEquals("dev", config.getAirbyteVersion());
  }

  @Test
  void testWorkspaceRoot() {
    when(function.apply(EnvConfigs.WORKSPACE_ROOT)).thenReturn(null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getWorkspaceRoot());

    when(function.apply(EnvConfigs.WORKSPACE_ROOT)).thenReturn("abc/def");
    Assertions.assertEquals(Paths.get("abc/def"), config.getWorkspaceRoot());
  }

  @Test
  void testLocalRoot() {
    when(function.apply(EnvConfigs.LOCAL_ROOT)).thenReturn(null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getLocalRoot());

    when(function.apply(EnvConfigs.LOCAL_ROOT)).thenReturn("abc/def");
    Assertions.assertEquals(Paths.get("abc/def"), config.getLocalRoot());
  }

  @Test
  void testConfigRoot() {
    when(function.apply(EnvConfigs.CONFIG_ROOT)).thenReturn(null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getConfigRoot());

    when(function.apply(EnvConfigs.CONFIG_ROOT)).thenReturn("a/b");
    Assertions.assertEquals(Paths.get("a/b"), config.getConfigRoot());
  }

  @Test
  void testGetDatabaseUser() {
    when(function.apply(EnvConfigs.DATABASE_USER)).thenReturn(null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getDatabaseUser());

    when(function.apply(EnvConfigs.DATABASE_USER)).thenReturn("user");
    Assertions.assertEquals("user", config.getDatabaseUser());
  }

  @Test
  void testGetDatabasePassword() {
    when(function.apply(EnvConfigs.DATABASE_PASSWORD)).thenReturn(null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getDatabasePassword());

    when(function.apply(EnvConfigs.DATABASE_PASSWORD)).thenReturn("password");
    Assertions.assertEquals("password", config.getDatabasePassword());
  }

  @Test
  void testGetDatabaseUrl() {
    when(function.apply(EnvConfigs.DATABASE_URL)).thenReturn(null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getDatabaseUrl());

    when(function.apply(EnvConfigs.DATABASE_URL)).thenReturn("url");
    Assertions.assertEquals("url", config.getDatabaseUrl());
  }

  @Test
  void testGetWorkspaceDockerMount() {
    when(function.apply(EnvConfigs.WORKSPACE_DOCKER_MOUNT)).thenReturn(null);
    when(function.apply(EnvConfigs.WORKSPACE_ROOT)).thenReturn("abc/def");
    Assertions.assertEquals("abc/def", config.getWorkspaceDockerMount());

    when(function.apply(EnvConfigs.WORKSPACE_DOCKER_MOUNT)).thenReturn("root");
    when(function.apply(EnvConfigs.WORKSPACE_ROOT)).thenReturn("abc/def");
    Assertions.assertEquals("root", config.getWorkspaceDockerMount());

    when(function.apply(EnvConfigs.WORKSPACE_DOCKER_MOUNT)).thenReturn(null);
    when(function.apply(EnvConfigs.WORKSPACE_ROOT)).thenReturn(null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getWorkspaceDockerMount());
  }

  @Test
  void testGetLocalDockerMount() {
    when(function.apply(EnvConfigs.LOCAL_DOCKER_MOUNT)).thenReturn(null);
    when(function.apply(EnvConfigs.LOCAL_ROOT)).thenReturn("abc/def");
    Assertions.assertEquals("abc/def", config.getLocalDockerMount());

    when(function.apply(EnvConfigs.LOCAL_DOCKER_MOUNT)).thenReturn("root");
    when(function.apply(EnvConfigs.LOCAL_ROOT)).thenReturn("abc/def");
    Assertions.assertEquals("root", config.getLocalDockerMount());

    when(function.apply(EnvConfigs.LOCAL_DOCKER_MOUNT)).thenReturn(null);
    when(function.apply(EnvConfigs.LOCAL_ROOT)).thenReturn(null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getLocalDockerMount());
  }

  @Test
  void testDockerNetwork() {
    when(function.apply(EnvConfigs.DOCKER_NETWORK)).thenReturn(null);
    Assertions.assertEquals("host", config.getDockerNetwork());

    when(function.apply(EnvConfigs.DOCKER_NETWORK)).thenReturn("abc");
    Assertions.assertEquals("abc", config.getDockerNetwork());
  }

  @Test
  void testTrackingStrategy() {
    when(function.apply(EnvConfigs.TRACKING_STRATEGY)).thenReturn(null);
    Assertions.assertEquals(Configs.TrackingStrategy.LOGGING, config.getTrackingStrategy());

    when(function.apply(EnvConfigs.TRACKING_STRATEGY)).thenReturn("abc");
    Assertions.assertEquals(Configs.TrackingStrategy.LOGGING, config.getTrackingStrategy());

    when(function.apply(EnvConfigs.TRACKING_STRATEGY)).thenReturn("logging");
    Assertions.assertEquals(Configs.TrackingStrategy.LOGGING, config.getTrackingStrategy());

    when(function.apply(EnvConfigs.TRACKING_STRATEGY)).thenReturn("segment");
    Assertions.assertEquals(Configs.TrackingStrategy.SEGMENT, config.getTrackingStrategy());

    when(function.apply(EnvConfigs.TRACKING_STRATEGY)).thenReturn("LOGGING");
    Assertions.assertEquals(Configs.TrackingStrategy.LOGGING, config.getTrackingStrategy());
  }

  @Test
  void testWorkerPodTolerations() {
    when(function.apply(EnvConfigs.WORKER_POD_TOLERATIONS)).thenReturn(null);
    Assertions.assertEquals(config.getWorkerPodTolerations(), List.of());

    when(function.apply(EnvConfigs.WORKER_POD_TOLERATIONS)).thenReturn(";;;");
    Assertions.assertEquals(config.getWorkerPodTolerations(), List.of());

    when(function.apply(EnvConfigs.WORKER_POD_TOLERATIONS)).thenReturn("key=k,value=v;");
    Assertions.assertEquals(config.getWorkerPodTolerations(), List.of());

    when(function.apply(EnvConfigs.WORKER_POD_TOLERATIONS)).thenReturn("key=airbyte-server,operator=Exists,effect=NoSchedule");
    Assertions.assertEquals(config.getWorkerPodTolerations(), List.of(new WorkerPodToleration("airbyte-server", "NoSchedule", null, "Exists")));

    when(function.apply(EnvConfigs.WORKER_POD_TOLERATIONS)).thenReturn("key=airbyte-server,operator=Equals,value=true,effect=NoSchedule");
    Assertions.assertEquals(config.getWorkerPodTolerations(), List.of(new WorkerPodToleration("airbyte-server", "NoSchedule", "true", "Equals")));

    when(function.apply(EnvConfigs.WORKER_POD_TOLERATIONS))
        .thenReturn("key=airbyte-server,operator=Exists,effect=NoSchedule;key=airbyte-server,operator=Equals,value=true,effect=NoSchedule");
    Assertions.assertEquals(config.getWorkerPodTolerations(), List.of(
        new WorkerPodToleration("airbyte-server", "NoSchedule", null, "Exists"),
        new WorkerPodToleration("airbyte-server", "NoSchedule", "true", "Equals")));
  }

}
