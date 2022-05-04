package io.airbyte.integrations.destination.redshift;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.sentry.AirbyteSentry;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.redshift.enums.RedshiftDataTmpTableMode;
import io.airbyte.integrations.destination.redshift.manifest.Entry;
import io.airbyte.integrations.destination.redshift.manifest.Manifest;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;
import io.airbyte.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;
import io.airbyte.integrations.destination.staging.StagingOperations;
import org.joda.time.DateTime;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

import static io.airbyte.integrations.destination.s3.S3StorageOperations.getFilename;

public class RedshiftS3StagingSqlOperations extends RedshiftSqlOperations implements StagingOperations {
    private final NamingConventionTransformer nameTransformer;
    private final S3StorageOperations s3StorageOperations;
    private final S3DestinationConfig s3Config;
    private final ObjectMapper objectMapper;
    private UUID connectionId;

    public RedshiftS3StagingSqlOperations(NamingConventionTransformer nameTransformer, AmazonS3 s3Client, S3DestinationConfig s3Config, RedshiftDataTmpTableMode redshiftDataTmpTableMode) {
        super(redshiftDataTmpTableMode);
        this.nameTransformer = nameTransformer;
        this.s3StorageOperations = new S3StorageOperations(nameTransformer, s3Client, s3Config);
        this.s3Config = s3Config;
        this.objectMapper = new ObjectMapper();
    }

    @Override
    public String getStageName(String namespace, String streamName) {
        return nameTransformer.applyDefaultCase(String.join("_",
                nameTransformer.convertStreamName(namespace),
                nameTransformer.convertStreamName(streamName)));
    }

    @Override
    public String getStagingPath(UUID connectionId, String namespace, String streamName, DateTime writeDatetime) {
        this.connectionId = connectionId;
        return nameTransformer.applyDefaultCase(String.format("%s/%s_%02d_%02d_%02d_%s/",
                getStageName(namespace, streamName),
                writeDatetime.year().get(),
                writeDatetime.monthOfYear().get(),
                writeDatetime.dayOfMonth().get(),
                writeDatetime.hourOfDay().get(),
                connectionId));
    }

    @Override
    public void createStageIfNotExists(JdbcDatabase database, String stageName) throws Exception {
        AirbyteSentry.executeWithTracing("CreateStageIfNotExists",
                () -> s3StorageOperations.createBucketObjectIfNotExists(stageName),
                Map.of("stage", stageName));
    }

    @Override
    public String uploadRecordsToStage(JdbcDatabase database, SerializableBuffer recordsData, String schemaName, String stageName, String stagingPath) throws Exception {
        String filename = s3StorageOperations.uploadRecordsToBucket(recordsData, schemaName, stageName, stagingPath);

        //        AirbyteSentry.executeWithTracing("UploadRecordsToStage",
//                () -> s3StorageOperations.uploadRecordsToBucket(recordsData, schemaName, stageName, stagingPath),
//                Map.of("stage", stageName, "path", stagingPath));
//        String fullObjectKey = s3StorageOperations.getFullObjectKey(stagingPath, recordsData);
//        return getFilename(fullObjectKey);
        return filename;
    }
    /**
     * Upload the supplied manifest file to S3
     *
     * @param manifestContents the manifest contents, never null
     * @param schemaName
     * @param stagingPath
     * @return the path where the manifest file was placed in S3
     */
    private String putManifest(final String manifestContents, String schemaName, String stagingPath) {
        String manifestFilePath =
                stagingPath + String.format("%s.manifest", UUID.randomUUID());
//                String.join("/", s3Config.getBucketPath(), stagingFolder, schemaName, String.format("%s.manifest", UUID.randomUUID()));
        s3StorageOperations.uploadManifest(s3Config.getBucketName(), manifestFilePath, manifestContents);
//        s3Client.putObject(s3Config.getBucketName(), manifestFilePath, manifestContents);

        return manifestFilePath;
    }
    @Override
    public void copyIntoTmpTableFromStage(JdbcDatabase database,
                                          String stageName,
                                          String stagingPath,
                                          List<String> stagedFiles,
                                          String dstTableName,
                                          String schemaName) throws Exception {
        LOGGER.info("Starting copy to tmp table from stage: {} in destination from stage: {}, schema: {}, .", dstTableName, stagingPath, schemaName);

        final var possibleManifest = Optional.ofNullable(createManifest(stagedFiles, stagingPath));

//        possibleManifest.stream()
//                .map(manifestContent -> putManifest(manifestContent,schemaName))
//                .forEach(manifestPath -> executeCopy(manifestPath, database, schemaName, dstTableName));
//        LOGGER.info("Copy to tmp table {}.{} in destination complete.", schemaName, dstTableName);

        LOGGER.info("Staging PATH {}", stagingPath);

        AirbyteSentry.executeWithTracing("CopyIntoTableFromStage",
                () -> Exceptions.toRuntime(() ->
                        possibleManifest.stream()
                                .map(manifestContent -> putManifest(manifestContent,schemaName,stagingPath))
                                .forEach(manifestPath -> executeCopy(manifestPath, database, schemaName, dstTableName))),
                Map.of("schema", schemaName, "path", stagingPath, "table", dstTableName));
        LOGGER.info("Copy to tmp table {}.{} in destination complete.", schemaName, dstTableName);
    }

    /**
     * Run Redshift COPY command with the given manifest file
     *
     * @param manifestPath the path in S3 to the manifest file
     */
    private void executeCopy(final String manifestPath, JdbcDatabase db, String schemaName, String tmpTableName) {
        final S3AccessKeyCredentialConfig credentialConfig = (S3AccessKeyCredentialConfig) s3Config.getS3CredentialConfig();
        final var copyQuery = String.format(
                "COPY %s.%s FROM '%s'\n"
                        + "CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'\n"
                        + "CSV REGION '%s' TIMEFORMAT 'auto'\n"
                        + "STATUPDATE OFF\n"
                        + "MANIFEST;",
                schemaName,
                tmpTableName,
                getFullS3Path(s3Config.getBucketName(), manifestPath),
                credentialConfig.getAccessKeyId(),
                credentialConfig.getSecretAccessKey(),
                s3Config.getBucketRegion());

        Exceptions.toRuntime(() -> db.execute(copyQuery));
    }
    /**
     * Creates the contents of a manifest file given the `s3StagingFiles`. There must be at least one
     * entry in a manifest file otherwise it is not considered valid for the COPY command.
     *
     * @return null if no stagingFiles exist otherwise the manifest body String
     * @param stagedFiles
     * @param stagingPath
     */
    private String createManifest(List<String> stagedFiles, String stagingPath) {
        if (stagedFiles.isEmpty()) {
            return null;
        }

        final var s3FileEntries = stagedFiles.stream()
                .map(file -> new Entry(getFullS3Path(s3Config.getBucketName(), file, stagingPath)))
                .collect(Collectors.toList());
        final var manifest = new Manifest(s3FileEntries);

        return Exceptions.toRuntime(() -> objectMapper.writeValueAsString(manifest));
    }


//    protected String getCopyQuery(final String stageName,
//                                  final String stagingPath,
//                                  final List<String> stagedFiles,
//                                  final String dstTableName,
//                                  final String schemaName) {
//        return String.format(COPY_QUERY + generateFilesList(stagedFiles) + ";",
//                schemaName,
//                dstTableName,
//                generateBucketPath(stageName, stagingPath),
//                s3Config.getAccessKeyId(),
//                s3Config.getSecretAccessKey());
//    }

//    private String generateBucketPath(final String stageName, final String stagingPath) {
//        return "s3://" + s3Config.getBucketName() + "/" + stagingPath + s3StagingFile;
//    }
private static String getFullS3Path(final String s3BucketName, final String s3StagingFile) {
    return String.join("/", "s3:/", s3BucketName,  s3StagingFile);
}
    private static String getFullS3Path(final String s3BucketName, final String s3StagingFile, final String stagingPath) {
//        return String.join("/", "s3:/", s3BucketName, stagingPath,  s3StagingFile);
        return "s3://" + s3BucketName + "/" + stagingPath + s3StagingFile;

    }

    @Override
    public void cleanUpStage(JdbcDatabase database, String stageName, List<String> stagedFiles) throws Exception {
        AirbyteSentry.executeWithTracing("CleanStage",
                () -> s3StorageOperations.cleanUpBucketObject(stageName, stagedFiles),
                Map.of("stage", stageName));
    }

    @Override
    public void dropStageIfExists(JdbcDatabase database, String stageName) throws Exception {
        AirbyteSentry.executeWithTracing("DropStageIfExists",
                () -> s3StorageOperations.dropBucketObject(stageName),
                Map.of("stage", stageName));
    }
}
