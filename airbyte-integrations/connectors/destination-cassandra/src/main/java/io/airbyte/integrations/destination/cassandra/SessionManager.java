/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import com.datastax.oss.driver.api.core.CqlSession;
import java.net.InetSocketAddress;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

class SessionManager {

  // AtomicInteger is used for convenience, this class is not thread safe
  // and needs additional synchronization for that.
  private static final ConcurrentHashMap<CassandraConfig, Tuple<CqlSession, AtomicInteger>> sessions;

  static {
    sessions = new ConcurrentHashMap<>();
  }

  private SessionManager() {

  }

  /*
   * CqlSession objects are heavyweight and can hold several tcp connections to the Cassandra cluster,
   * for that reason it is better if sessions are reused per configuration. Sessions are thread-safe
   * and can be accessed from different threads.
   *
   */
  public static CqlSession initSession(CassandraConfig cassandraConfig) {
    var cachedSession = sessions.get(cassandraConfig);
    if (cachedSession != null) {
      cachedSession.value2().incrementAndGet();
      return cachedSession.value1();
    } else {
      var session = CqlSession.builder()
          .withLocalDatacenter(cassandraConfig.getDatacenter())
          .addContactPoint(new InetSocketAddress(cassandraConfig.getAddress(), cassandraConfig.getPort()))
          .withAuthCredentials(cassandraConfig.getUsername(), cassandraConfig.getPassword())
          .build();
      sessions.put(cassandraConfig, Tuple.of(session, new AtomicInteger(1)));
      return session;
    }
  }

  /*
   * Close session configured with cassandra config. if the session is being used by more than one
   * external instance only decrease the usage count, otherwise close the session and remove it from
   * the map.
   *
   */
  public static void closeSession(CassandraConfig cassandraConfig) {
    var cachedSession = sessions.get(cassandraConfig);
    if (cachedSession == null) {
      throw new IllegalStateException("No session for the provided config");
    }
    int count = cachedSession.value2().decrementAndGet();
    if (count < 1) {
      cachedSession.value1().close();
      sessions.remove(cassandraConfig);
    }
  }

}
