/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage.file

import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.PartFactory
import java.io.InputStream

/** Turns a file into a series of Part chunks. */
class FilePartIterator(
    private val inputStream: InputStream,
    private val partSizeBytes: Int,
    finalPath: String,
) : Iterator<Part> {
    private val partFactory =
        PartFactory(
            key = finalPath,
            fileNumber = 0,
        )

    lateinit var complete: Unit

    override fun hasNext(): Boolean = !::complete.isInitialized

    /** Reads up to partSizeByes from inputStream and wraps it in a Part */
    override fun next(): Part {
        val bytes = inputStream.readNBytes(partSizeBytes)
        return if (bytes.isEmpty()) {
            onComplete()
            partFactory.nextPart(null, isFinal = true)
        } else if (bytes.size < partSizeBytes) {
            onComplete()
            partFactory.nextPart(bytes, isFinal = true)
        } else {
            partFactory.nextPart(bytes, isFinal = false)
        }
    }

    private fun onComplete() {
        complete = Unit
    }
}
