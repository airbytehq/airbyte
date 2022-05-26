/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.scylla;

import com.datastax.driver.core.Cluster;
import com.datastax.driver.core.Session;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

class ScyllaSessionPool {

  private static final ConcurrentHashMap<ScyllaConfig, Triplet<Cluster, Session, AtomicInteger>> sessions;

  static {
    sessions = new ConcurrentHashMap<>();
  }

  private ScyllaSessionPool() {

  }

  static Tuple<Cluster, Session> initSession(ScyllaConfig scyllaConfig) {
    var cachedSession = sessions.get(scyllaConfig);
    if (cachedSession != null) {
      cachedSession.value3().incrementAndGet();
      return Tuple.of(cachedSession.value1(), cachedSession.value2());
    } else {
      var cluster = Cluster.builder()
          .addContactPoint(scyllaConfig.getAddress())
          .withPort(scyllaConfig.getPort())
          .withCredentials(scyllaConfig.getUsername(), scyllaConfig.getPassword())
          .build();
      var session = cluster.connect();
      sessions.put(scyllaConfig, Triplet.of(cluster, session, new AtomicInteger(1)));
      return Tuple.of(cluster, session);
    }
  }

  static void closeSession(ScyllaConfig scyllaConfig) {
    var session = sessions.get(scyllaConfig);
    if (session == null) {
      throw new IllegalStateException("No session for the provided config");
    }
    int usage = session.value3().decrementAndGet();
    if (usage < 1) {
      session.value2().close();
      session.value1().close();
      sessions.remove(scyllaConfig);
    }
  }

}
