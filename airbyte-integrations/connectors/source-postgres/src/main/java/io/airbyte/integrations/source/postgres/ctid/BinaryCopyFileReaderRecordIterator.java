package io.airbyte.integrations.source.postgres.ctid;
import io.airbyte.commons.functional.CheckedConsumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Iterator;
import java.util.Optional;

public class BinaryCopyFileReaderRecordIterator implements Iterator<String> {
  private static final Logger LOGGER = LoggerFactory.getLogger(BinaryCopyFileReaderRecordIterator.class);
  private static final String MAGIC ="PGCOPY\n\377\r\n\0";
  private static final long HEADER_LEN = MAGIC.length() + 4 + 4;
  private Optional<Runnable> cleanup;

  record header (boolean has_oids) {}

  header fileHeader;
  final DataInputStream input;

  BinaryCopyFileReaderRecordIterator(final String filePath) throws FileNotFoundException {
    this.input = new DataInputStream(
            new BufferedInputStream(new FileInputStream(filePath), 1_000_000));
    this.cleanup = Optional.of(() -> {
        try {
            Files.deleteIfExists(Paths.get(filePath));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    });
  }

  BinaryCopyFileReaderRecordIterator(final DataInputStream input) {
    this.input = input;
    this.fileHeader = null;
  }


  @Override
  public boolean hasNext()  {
    try {
      input.mark(2);
//      LOGGER.info("*** avail {}", input.available());
      if (input.available() <= 0) {
        return false;
      }
      int len = input.readShort();
      input.reset();
      return len != -1;
    } catch (final IOException e) {
      return false;
    }

  }

  @Override
  public String next() {
    try {
      if (fileHeader == null) {
        assert (check_remaining(HEADER_LEN));
        input.skip(MAGIC.length());
        final int flags = input.readInt();
        final boolean has_oids = (flags & (1 << 16)) != 0;
        final int val_header_extension = input.readInt();
        final long header_extension = Integer.toUnsignedLong(val_header_extension);
        assert (check_remaining(header_extension));
        fileHeader = new header(has_oids);
      }

      assert (check_remaining(2));
      int len = input.readShort();
      if (len == -1) {
        return null;
      }
      if (fileHeader.has_oids) {
        len++;
      }
      if (len != 1) {
        throw new RuntimeException("expected 1 value per row but got %d".formatted(len));
      }

      // assume it's one columns
      // for ...
      assert (check_remaining(4));
      len = input.readInt();
      if (len == -1) {
        throw new RuntimeException("Unexpected EOF");
      } else {
        final long recordLen = Integer.toUnsignedLong(len);
        assert(check_remaining(recordLen));
        final byte[] b = new byte[(int) recordLen];
        final int numRead = input.read(b);
        assert (numRead == recordLen);
        return new String(b, StandardCharsets.UTF_8);
//        return stringFromBytes(b);
      }

    } catch (final IOException ex) {
      throw new RuntimeException(ex);
    }
  }

  boolean check_remaining(final long bytes) {
    return true; // TEMP
  }

/*  public static String stringFromBytes(byte byteData[]) {
    char charData[] = new char[byteData.length];
    for(int i = 0; i < charData.length; i++) {
      charData[i] = (char) (((int) byteData[i]) & 0xFF);
    }
    return new String(charData);
  }*/

  public void close() {
    if (input != null) {
        try {
            input.close();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
    if (cleanup.isPresent()) {
      cleanup.get().run();
    }
  }
}
