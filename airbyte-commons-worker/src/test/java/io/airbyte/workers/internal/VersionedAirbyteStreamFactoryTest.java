/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

class VersionedAirbyteStreamFactoryTest {
  /*
   * AirbyteMessageSerDeProvider serDeProvider; AirbyteMessageVersionedMigratorFactory
   * migratorFactory;
   *
   * final static Version defaultVersion = new Version("0.2.0");
   *
   * @BeforeEach void beforeEach() { serDeProvider = spy(new AirbyteMessageSerDeProvider( List.of(new
   * AirbyteMessageV0Deserializer()), List.of(new AirbyteMessageV0Serializer())));
   * serDeProvider.initialize(); final AirbyteMessageMigrator migrator = new AirbyteMessageMigrator(
   * List.of(new AirbyteMessageMigrationV0())); migrator.initialize(); migratorFactory = spy(new
   * AirbyteMessageVersionedMigratorFactory(migrator)); }
   *
   * @Test
   *
   * @Ignore void testCreate() { final Version initialVersion = new Version("0.1.2"); final
   * VersionedAirbyteStreamFactory<?> streamFactory = new
   * VersionedAirbyteStreamFactory<>(serDeProvider, migratorFactory, initialVersion,
   * Optional.empty());
   *
   * final BufferedReader bufferedReader = new BufferedReader(new StringReader(""));
   * streamFactory.create(bufferedReader);
   *
   * verify(serDeProvider).getDeserializer(initialVersion);
   * verify(migratorFactory).getVersionedMigrator(initialVersion); }
   *
   * @Test
   *
   * @Ignore void testCreateWithVersionDetection() { final Version initialVersion = new
   * Version("0.0.0"); final VersionedAirbyteStreamFactory<?> streamFactory = new
   * VersionedAirbyteStreamFactory<>(serDeProvider, migratorFactory, initialVersion, Optional.empty())
   * .withDetectVersion(true);
   *
   * final BufferedReader bufferedReader =
   * getBuffereredReader("version-detection/logs-with-version.jsonl"); final Stream<AirbyteMessage>
   * stream = streamFactory.create(bufferedReader);
   *
   * final long messageCount = stream.toList().size();
   * verify(serDeProvider).getDeserializer(initialVersion); verify(serDeProvider).getDeserializer(new
   * Version("0.5.9")); assertEquals(1, messageCount); }
   *
   * @Test
   *
   * @Ignore void testCreateWithVersionDetectionFallback() { final Version initialVersion = new
   * Version("0.0.6"); final VersionedAirbyteStreamFactory<?> streamFactory = new
   * VersionedAirbyteStreamFactory<>(serDeProvider, migratorFactory, initialVersion, Optional.empty())
   * .withDetectVersion(true);
   *
   * final BufferedReader bufferedReader =
   * getBuffereredReader("version-detection/logs-without-version.jsonl"); final Stream<AirbyteMessage>
   * stream = streamFactory.create(bufferedReader);
   *
   * final long messageCount = stream.toList().size();
   * verify(serDeProvider).getDeserializer(initialVersion);
   * verify(serDeProvider).getDeserializer(defaultVersion); assertEquals(1, messageCount); }
   *
   * @Test
   *
   * @Ignore void testCreateWithVersionDetectionWithoutSpecMessage() { final Version initialVersion =
   * new Version("0.0.1"); final VersionedAirbyteStreamFactory<?> streamFactory = new
   * VersionedAirbyteStreamFactory<>(serDeProvider, migratorFactory, initialVersion, Optional.empty())
   * .withDetectVersion(true);
   *
   * final BufferedReader bufferedReader =
   * getBuffereredReader("version-detection/logs-without-spec-message.jsonl"); final
   * Stream<AirbyteMessage> stream = streamFactory.create(bufferedReader);
   *
   * final long messageCount = stream.toList().size();
   * verify(serDeProvider).getDeserializer(initialVersion);
   * verify(serDeProvider).getDeserializer(defaultVersion); assertEquals(2, messageCount); }
   *
   * BufferedReader getBuffereredReader(final String resourceFile) { return new BufferedReader( new
   * InputStreamReader( ClassLoaderUtils.getDefaultClassLoader().getResourceAsStream(resourceFile),
   * Charset.defaultCharset())); }
   */
}
