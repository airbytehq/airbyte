/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.template;

import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.s3.S3Format;
import java.util.Objects;

/**
 * This class is used as argument holder S3FilenameTemplateManager.class
 *
 * @see S3FilenameTemplateManager#adaptFilenameAccordingSpecificationPatternWithDefaultConfig(S3FilenameTemplateParameterObject)
 */
public class S3FilenameTemplateParameterObject {

  private final String objectPath;
  private final SerializableBuffer recordsData;
  private final String fileNamePattern;
  private final String fileExtension;
  private final String partId;
  private final S3Format s3Format;

  S3FilenameTemplateParameterObject(final String objectPath,
                                    final SerializableBuffer recordsData,
                                    final String fileNamePattern,
                                    final String fileExtension,
                                    final String partId,
                                    final S3Format s3Format) {
    this.objectPath = objectPath;
    this.recordsData = recordsData;
    this.fileNamePattern = fileNamePattern;
    this.fileExtension = fileExtension;
    this.partId = partId;
    this.s3Format = s3Format;
  }

  public static FilenameTemplateParameterObjectBuilder builder() {
    return new FilenameTemplateParameterObjectBuilder();
  }

  public String getObjectPath() {
    return objectPath;
  }

  public SerializableBuffer getRecordsData() {
    return recordsData;
  }

  public String getFileNamePattern() {
    return fileNamePattern;
  }

  public String getFileExtension() {
    return fileExtension;
  }

  public String getPartId() {
    return partId;
  }

  public S3Format getS3Format() {
    return s3Format;
  }

  public static class FilenameTemplateParameterObjectBuilder {

    private String objectPath;
    private SerializableBuffer recordsData;
    private String fileNamePattern;
    private String fileExtension;
    private String partId;
    private S3Format s3Format;

    FilenameTemplateParameterObjectBuilder() {}

    public FilenameTemplateParameterObjectBuilder objectPath(final String objectPath) {
      this.objectPath = objectPath;
      return this;
    }

    public FilenameTemplateParameterObjectBuilder recordsData(final SerializableBuffer recordsData) {
      this.recordsData = recordsData;
      return this;
    }

    public FilenameTemplateParameterObjectBuilder fileNamePattern(final String fileNamePattern) {
      this.fileNamePattern = fileNamePattern;
      return this;
    }

    public FilenameTemplateParameterObjectBuilder fileExtension(final String fileExtension) {
      this.fileExtension = fileExtension;
      return this;
    }

    public FilenameTemplateParameterObjectBuilder partId(final String partId) {
      this.partId = partId;
      return this;
    }

    public FilenameTemplateParameterObjectBuilder s3Format(final S3Format s3Format) {
      this.s3Format = s3Format;
      return this;
    }

    public S3FilenameTemplateParameterObject build() {
      return new S3FilenameTemplateParameterObject(objectPath, recordsData, fileNamePattern, fileExtension, partId, s3Format);
    }

    public String toString() {
      return "FilenameTemplateParameterObject.FilenameTemplateParameterObjectBuilder(objectPath=" + objectPath + ", recordsData=" + recordsData
          + ", fileNamePattern=" + fileNamePattern
          + ", fileExtension=" + fileExtension + ", partId=" + partId + ", s3Format=" + s3Format + ")";
    }

  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final S3FilenameTemplateParameterObject that = (S3FilenameTemplateParameterObject) o;
    return Objects.equals(objectPath, that.objectPath) && Objects.equals(recordsData, that.recordsData)
        && Objects.equals(fileNamePattern, that.fileNamePattern)
        && Objects.equals(fileExtension, that.fileExtension) && Objects.equals(partId, that.partId) && s3Format == that.s3Format;
  }

  @Override
  public int hashCode() {
    return Objects.hash(objectPath, recordsData, fileNamePattern, fileExtension, partId, s3Format);
  }

}
