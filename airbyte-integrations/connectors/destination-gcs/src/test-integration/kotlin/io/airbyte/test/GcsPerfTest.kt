package io.airbyte.test

import io.airbyte.cdk.load.write.BasicPerformanceTest
import org.junit.jupiter.api.Test

class GcsPerfTest : BasicPerformanceTest(
    configContents = "{}",
    configSpecClass = GcsSpec::class.java,
    defaultRecordsToInsert = 2_000_000,
    numFilesForFileTransfer = 5,
    fileSizeMbForFileTransfer = 1024,
) {
    @Test
    override fun testInsertRecords() {
        super.testInsertRecords()
    }
}
