package io.airbyte.integrations.destination.redshift;

import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftCopier {
  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftCopier.class);

  public void copy(AirbyteRecordMessage message) {
    // this needs to be in a format that can be ingested into a raw airbyte table

  }

  public void close(boolean hasFailed) {
    // copy to Redshift
    // create tmp table
    // copy into tmp table
    // copy into final table

    // clean up
    // delete tmp table
    // delete staging file
  }

  public static void main(String[] args) throws IOException {
    var awsCreds = new BasicAWSCredentials("", "");
    var client = AmazonS3ClientBuilder.standard()
        // region has to be the same as the redshift cluster
        .withCredentials(new AWSStaticCredentialsProvider(awsCreds)).withRegion(Regions.DEFAULT_REGION)
        .build();

    var bucket = "airbyte.davin";
    var key = "tests/test-library-1.csv";
    var srcFile = "/Users/davinchia/Desktop/films_truncate.csv";

    final StreamTransferManager manager = new StreamTransferManager(bucket, key, client)
        .numUploadThreads(20)
        .queueCapacity(20)
        .partSize(10);
    var writeStream = manager.getMultiPartOutputStreams().get(0);

    var path = Paths.get(srcFile);
    var buffReader = Files.newBufferedReader(path);
    String line;
    while (null != (line = buffReader.readLine())) {
      System.out.println(line);
      line += "\n";
      System.out.println(line);
      writeStream.write(line.getBytes(StandardCharsets.UTF_8));
    }
    // Finishing off
    writeStream.close();
    manager.complete();
  }
}
