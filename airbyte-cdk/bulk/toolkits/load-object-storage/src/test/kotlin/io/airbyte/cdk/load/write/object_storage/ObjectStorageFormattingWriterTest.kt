/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriter
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriter
import io.mockk.coEvery
import io.mockk.impl.annotations.MockK
import io.mockk.mockk
import java.io.ByteArrayOutputStream
import org.junit.jupiter.api.Test

class ObjectStorageFormattingWriterTest {
    @MockK(relaxed = true) lateinit var underlyingWriter: ObjectStorageFormattingWriter

    @Test
    fun `buffered formatting writer never produces empty parts`() {
        val outputStream = ByteArrayOutputStream()
        outputStream.write("i am a header".toByteArray())
        val bufferedWriter =
            BufferedFormattingWriter(
                underlyingWriter,
                outputStream,
                NoopProcessor,
                NoopProcessor.wrapper(outputStream),
            )

        assert(bufferedWriter.bufferSize == 0) { "buffer appears empty despite header" }
        assert(bufferedWriter.takeBytes() == null) { "buffer yields no data despite header" }
        assert(bufferedWriter.finish() == null) { "buffer yields no data despite header" }
    }

    @Test
    fun `buffered formatting writer yields entire buffer once any data has been added`() {
        val outputStream = ByteArrayOutputStream()
        outputStream.write("i am a header".toByteArray())
        val bufferedWriter =
            BufferedFormattingWriter(
                underlyingWriter,
                outputStream,
                NoopProcessor,
                NoopProcessor.wrapper(outputStream),
            )

        assert(bufferedWriter.takeBytes() == null)
        coEvery { bufferedWriter.accept(any()) } coAnswers { outputStream.write("!".toByteArray()) }
        bufferedWriter.accept(mockk())
        val bytes = bufferedWriter.takeBytes()
        assert(bytes != null) { "buffer yields data now that we've written to it" }
        assert(bytes.contentEquals("i am a header!".toByteArray())) {
            "buffer yields all data written to it"
        }
    }
}
