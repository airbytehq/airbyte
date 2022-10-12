package io.airbyte.integrations.destination.doris;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import java.nio.file.Path;

public class DorisWriteConfig {

    private final Path tmpPath;
    private final DorisStreamLoad dorisStreamLoad;

    private final CSVPrinter writer;
    private final CSVFormat format;

    public DorisWriteConfig(Path tmpPath, DorisStreamLoad dorisStreamLoad, CSVPrinter writer, CSVFormat format) {
        this.tmpPath = tmpPath;
        this.dorisStreamLoad = dorisStreamLoad;
        this.writer = writer;
        this.format = format;

    }

    public Path getTmpPath() {
        return tmpPath;
    }

    public DorisStreamLoad getDorisStreamLoad() {
        return dorisStreamLoad;
    }

    public CSVFormat getFormat() {
        return format;
    }

    public CSVPrinter getWriter() {
        return writer;
    }
}
