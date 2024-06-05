/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.base.Preconditions
import io.airbyte.commons.json.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.EOFException
import java.io.IOException
import java.io.ObjectOutputStream
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.NoSuchFileException
import java.nio.file.Path
import java.util.*
import java.util.function.BiFunction
import org.apache.commons.io.FileUtils
import org.apache.kafka.connect.errors.ConnectException
import org.apache.kafka.connect.util.SafeObjectInputStream

private val LOGGER = KotlinLogging.logger {}
/**
 * This class handles reading and writing a debezium offset file. In many cases it is duplicating
 * logic in debezium because that logic is not exposed in the public API. We mostly treat the
 * contents of this state file like a black box. We know it is a Map&lt;ByteBuffer, Bytebuffer&gt;.
 * We deserialize it to a Map&lt;String, String&gt; so that the state file can be human readable. If
 * we ever discover that any of the contents of these offset files is not string serializable we
 * will likely have to drop the human readability support and just base64 encode it.
 */
class AirbyteFileOffsetBackingStore(
    private val offsetFilePath: Path,
    private val dbName: Optional<String>
) {
    fun read(): Map<String, String> {
        val raw = load()

        return raw.entries.associate { byteBufferToString(it.key) to byteBufferToString(it.value) }
    }

    fun persist(cdcState: JsonNode?) {
        @Suppress("unchecked_cast")
        val mapAsString: Map<String, String> =
            if (cdcState != null)
                Jsons.`object`(cdcState, MutableMap::class.java) as Map<String, String>
            else emptyMap()

        val updatedMap = updateStateForDebezium2_1(mapAsString)

        val mappedAsStrings: Map<ByteBuffer?, ByteBuffer?> =
            updatedMap.entries.associate {
                stringToByteBuffer(it.key) to stringToByteBuffer(it.value)
            }

        FileUtils.deleteQuietly(offsetFilePath.toFile())
        save(mappedAsStrings)
    }

    private fun updateStateForDebezium2_1(mapAsString: Map<String, String>): Map<String, String> {
        val updatedMap: MutableMap<String, String> = LinkedHashMap()
        if (mapAsString.size > 0) {
            // We're getting the 1st of a map. Something fishy going on here
            val key = mapAsString.keys.toList()[0]
            val i = key.indexOf('[')
            val i1 = key.lastIndexOf(']')

            if (i == 0 && i1 == key.length - 1) {
                // The state is Debezium 2.1 compatible. No need to change anything.
                return mapAsString
            }

            LOGGER.info { "Mutating sate to make it Debezium 2.1 compatible" }
            val newKey =
                if (dbName.isPresent)
                    SQL_SERVER_STATE_MUTATION.apply(key.substring(i, i1 + 1), dbName.get())
                else key.substring(i, i1 + 1)
            val value = mapAsString.getValue(key)
            updatedMap[newKey] = value
        }
        return updatedMap
    }

    /**
     * See FileOffsetBackingStore#load - logic is mostly borrowed from here. duplicated because this
     * method is not public. Reduced the try catch block to only the read operation from original
     * code to reduce errors when reading the file.
     */
    private fun load(): Map<ByteBuffer?, ByteBuffer?> {
        var obj: Any
        try {
            SafeObjectInputStream(Files.newInputStream(offsetFilePath)).use { `is` ->
                // todo (cgardens) - we currently suppress a security warning for this line. use of
                // readObject from
                // untrusted sources is considered unsafe. Since the source is controlled by us in
                // this case it
                // should be safe. That said, changing this implementation to not use readObject
                // would remove some
                // headache.
                obj = `is`.readObject()
            }
        } catch (e: NoSuchFileException) {
            // NoSuchFileException: Ignore, may be new.
            // EOFException: Ignore, this means the file was missing or corrupt
            return emptyMap()
        } catch (e: EOFException) {
            return emptyMap()
        } catch (e: IOException) {
            throw ConnectException(e)
        } catch (e: ClassNotFoundException) {
            throw ConnectException(e)
        }

        if (obj !is HashMap<*, *>)
            throw ConnectException("Expected HashMap but found " + obj.javaClass)
        @Suppress("unchecked_cast") val raw = obj as Map<ByteArray?, ByteArray?>
        val data: MutableMap<ByteBuffer?, ByteBuffer?> = HashMap()
        for ((key1, value1) in raw) {
            val key = if ((key1 != null)) ByteBuffer.wrap(key1) else null
            val value = if ((value1 != null)) ByteBuffer.wrap(value1) else null
            data[key] = value
        }

        return data
    }

    /**
     * See FileOffsetBackingStore#save - logic is mostly borrowed from here. duplicated because this
     * method is not public.
     */
    private fun save(data: Map<ByteBuffer?, ByteBuffer?>) {
        try {
            ObjectOutputStream(Files.newOutputStream(offsetFilePath)).use { os ->
                val raw: MutableMap<ByteArray?, ByteArray?> = HashMap()
                for ((key1, value1) in data) {
                    val key = if ((key1 != null)) key1.array() else null
                    val value = if ((value1 != null)) value1.array() else null
                    raw[key] = value
                }
                os.writeObject(raw)
            }
        } catch (e: IOException) {
            throw ConnectException(e)
        }
    }

    fun setDebeziumProperties(props: Properties) {
        // debezium engine configuration
        // https://debezium.io/documentation/reference/2.2/development/engine.html#engine-properties
        props.setProperty(
            "offset.storage",
            "org.apache.kafka.connect.storage.FileOffsetBackingStore"
        )
        props.setProperty("offset.storage.file.filename", offsetFilePath.toString())
        props.setProperty("offset.flush.interval.ms", "1000") // todo: make this longer
    }

    companion object {
        private val SQL_SERVER_STATE_MUTATION = BiFunction { key: String, databaseName: String ->
            (key.substring(0, key.length - 2) +
                ",\"database\":\"" +
                databaseName +
                "\"" +
                key.substring(key.length - 2))
        }

        private fun byteBufferToString(byteBuffer: ByteBuffer?): String {
            Preconditions.checkNotNull(byteBuffer)
            return String(byteBuffer!!.array(), StandardCharsets.UTF_8)
        }

        private fun stringToByteBuffer(s: String?): ByteBuffer {
            Preconditions.checkNotNull(s)
            return ByteBuffer.wrap(s!!.toByteArray(StandardCharsets.UTF_8))
        }

        @JvmStatic
        fun initializeState(
            cdcState: JsonNode?,
            dbName: Optional<String>
        ): AirbyteFileOffsetBackingStore {
            val cdcWorkingDir: Path
            try {
                cdcWorkingDir = Files.createTempDirectory(Path.of("/tmp"), "cdc-state-offset")
            } catch (e: IOException) {
                throw RuntimeException(e)
            }
            val cdcOffsetFilePath = cdcWorkingDir.resolve("offset.dat")

            val offsetManager = AirbyteFileOffsetBackingStore(cdcOffsetFilePath, dbName)
            offsetManager.persist(cdcState)
            return offsetManager
        }

        @JvmStatic
        fun initializeDummyStateForSnapshotPurpose(): AirbyteFileOffsetBackingStore {
            val cdcWorkingDir: Path
            try {
                cdcWorkingDir = Files.createTempDirectory(Path.of("/tmp"), "cdc-dummy-state-offset")
            } catch (e: IOException) {
                throw RuntimeException(e)
            }
            val cdcOffsetFilePath = cdcWorkingDir.resolve("offset.dat")

            return AirbyteFileOffsetBackingStore(cdcOffsetFilePath, Optional.empty())
        }
    }
}
