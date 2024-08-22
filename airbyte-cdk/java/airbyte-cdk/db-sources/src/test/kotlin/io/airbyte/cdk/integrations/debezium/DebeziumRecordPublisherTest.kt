/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium

import com.google.common.collect.ImmutableList
import io.airbyte.cdk.integrations.debezium.internals.RelationalDbDebeziumPropertiesManager
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import java.util.regex.Pattern
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class DebeziumRecordPublisherTest {
    @Test
    fun testTableIncludelistCreation() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    ImmutableList.of(
                        CatalogHelpers.createConfiguredAirbyteStream("id_and_name", "public")
                            .withSyncMode(SyncMode.INCREMENTAL),
                        CatalogHelpers.createConfiguredAirbyteStream("id_,something", "public")
                            .withSyncMode(SyncMode.INCREMENTAL),
                        CatalogHelpers.createConfiguredAirbyteStream("n\"aMéS", "public")
                            .withSyncMode(SyncMode.INCREMENTAL),
                    ),
                )

        val expectedWhitelist =
            "\\Qpublic.id_and_name\\E,\\Qpublic.id_\\,something\\E,\\Qpublic.n\"aMéS\\E"
        val actualWhitelist =
            RelationalDbDebeziumPropertiesManager.getTableIncludelist(
                catalog,
                getCdcStreamListFromCatalog(catalog)
            )

        Assertions.assertEquals(expectedWhitelist, actualWhitelist)
    }

    @Test
    fun testTableIncludelistFiltersFullRefresh() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    ImmutableList.of(
                        CatalogHelpers.createConfiguredAirbyteStream("id_and_name", "public")
                            .withSyncMode(SyncMode.INCREMENTAL),
                        CatalogHelpers.createConfiguredAirbyteStream("id_and_name2", "public")
                            .withSyncMode(SyncMode.FULL_REFRESH),
                    ),
                )

        val expectedWhitelist = "\\Qpublic.id_and_name\\E"
        val actualWhitelist =
            RelationalDbDebeziumPropertiesManager.getTableIncludelist(
                catalog,
                getCdcStreamListFromCatalog(catalog)
            )

        Assertions.assertEquals(expectedWhitelist, actualWhitelist)
    }

    @Test
    fun testColumnIncludelistFiltersFullRefresh() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    ImmutableList.of(
                        CatalogHelpers.createConfiguredAirbyteStream(
                                "id_and_name",
                                "public",
                                Field.of("fld1", JsonSchemaType.NUMBER),
                                Field.of("fld2", JsonSchemaType.STRING),
                            )
                            .withSyncMode(SyncMode.INCREMENTAL),
                        CatalogHelpers.createConfiguredAirbyteStream("id_,something", "public")
                            .withSyncMode(SyncMode.INCREMENTAL),
                        CatalogHelpers.createConfiguredAirbyteStream("id_and_name2", "public")
                            .withSyncMode(SyncMode.FULL_REFRESH),
                        CatalogHelpers.createConfiguredAirbyteStream("n\"aMéS", "public")
                            .withSyncMode(SyncMode.INCREMENTAL),
                    ),
                )

        val expectedWhitelist =
            "\\Qpublic.id_and_name\\E\\.(\\Qfld2\\E|\\Qfld1\\E),\\Qpublic.id_\\,something\\E,\\Qpublic.n\"aMéS\\E"
        val actualWhitelist =
            RelationalDbDebeziumPropertiesManager.getColumnIncludeList(
                catalog,
                getCdcStreamListFromCatalog(catalog)
            )

        Assertions.assertEquals(expectedWhitelist, actualWhitelist)
    }

    @Test
    fun testTableIncludelistFiltersStreamList() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    ImmutableList.of(
                        CatalogHelpers.createConfiguredAirbyteStream("id_and_name", "public")
                            .withSyncMode(SyncMode.INCREMENTAL),
                        CatalogHelpers.createConfiguredAirbyteStream("id_and_name2", "public")
                            .withSyncMode(SyncMode.INCREMENTAL),
                    ),
                )

        val expectedWhitelist = "\\Qpublic.id_and_name\\E"
        val cdcStreamList =
            catalog.streams
                .stream()
                .filter { configuredStream: ConfiguredAirbyteStream ->
                    configuredStream.stream.name.equals("id_and_name")
                }
                .map { stream: ConfiguredAirbyteStream ->
                    stream.stream.namespace + "." + stream.stream.name
                }
                .toList()
        val actualWhitelist =
            RelationalDbDebeziumPropertiesManager.getTableIncludelist(catalog, cdcStreamList)

        Assertions.assertEquals(expectedWhitelist, actualWhitelist)
    }

    @Test
    fun testColumnIncludelistFiltersStreamList() {
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    ImmutableList.of(
                        CatalogHelpers.createConfiguredAirbyteStream(
                                "id_and_name",
                                "public",
                                Field.of("fld1", JsonSchemaType.NUMBER),
                                Field.of("fld2", JsonSchemaType.STRING),
                            )
                            .withSyncMode(SyncMode.INCREMENTAL),
                        CatalogHelpers.createConfiguredAirbyteStream("id_,something", "public")
                            .withSyncMode(SyncMode.INCREMENTAL),
                        CatalogHelpers.createConfiguredAirbyteStream("id_and_name2", "public")
                            .withSyncMode(SyncMode.FULL_REFRESH),
                        CatalogHelpers.createConfiguredAirbyteStream("n\"aMéS", "public")
                            .withSyncMode(SyncMode.INCREMENTAL),
                    ),
                )

        val expectedWhitelist =
            "\\Qpublic.id_and_name\\E\\.(\\Qfld2\\E|\\Qfld1\\E),\\Qpublic.id_\\,something\\E,\\Qpublic.n\"aMéS\\E"
        val cdcStreamList =
            catalog.streams
                .stream()
                .filter { configuredStream: ConfiguredAirbyteStream ->
                    !configuredStream.stream.name.equals("id_and_name2")
                }
                .map { stream: ConfiguredAirbyteStream ->
                    stream.stream.namespace + "." + stream.stream.name
                }
                .toList()
        val actualWhitelist =
            RelationalDbDebeziumPropertiesManager.getColumnIncludeList(catalog, cdcStreamList)

        Assertions.assertEquals(expectedWhitelist, actualWhitelist)
    }

    @Test
    fun testColumnIncludeListEscaping() {
        // final String a = "public\\.products\\*\\^\\$\\+-\\\\";
        // final String b = "public.products*^$+-\\";
        // final Pattern p = Pattern.compile(a, Pattern.UNIX_LINES);
        // assertTrue(p.matcher(b).find());
        // assertTrue(Pattern.compile(Pattern.quote(b)).matcher(b).find());

        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    ImmutableList.of(
                        CatalogHelpers.createConfiguredAirbyteStream(
                                "id_and_name",
                                "public",
                                Field.of("fld1", JsonSchemaType.NUMBER),
                                Field.of("fld2", JsonSchemaType.STRING),
                            )
                            .withSyncMode(SyncMode.INCREMENTAL),
                    ),
                )

        val anchored =
            "^" +
                RelationalDbDebeziumPropertiesManager.getColumnIncludeList(
                    catalog,
                    getCdcStreamListFromCatalog(catalog)
                ) +
                "$"
        val pattern = Pattern.compile(anchored)

        Assertions.assertTrue(pattern.matcher("public.id_and_name.fld1").find())
        Assertions.assertTrue(pattern.matcher("public.id_and_name.fld2").find())
        Assertions.assertFalse(pattern.matcher("ic.id_and_name.fl").find())
        Assertions.assertFalse(pattern.matcher("ppppublic.id_and_name.fld2333").find())
        Assertions.assertFalse(pattern.matcher("public.id_and_name.fld_wrong_wrong").find())
    }

    fun getCdcStreamListFromCatalog(catalog: ConfiguredAirbyteCatalog): List<String> {
        return catalog.streams
            .stream()
            .filter { stream: ConfiguredAirbyteStream -> stream.syncMode == SyncMode.INCREMENTAL }
            .map { stream: ConfiguredAirbyteStream ->
                stream.stream.namespace + "." + stream.stream.name
            }
            .toList()
    }
}
