/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.workers.protocols.singer;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DataType;
import io.airbyte.config.Field;
import io.airbyte.config.Schema;
import io.airbyte.config.Stream;
import io.airbyte.singer.SingerCatalog;
import io.airbyte.singer.SingerColumn;
import io.airbyte.singer.SingerMetadata;
import io.airbyte.singer.SingerMetadataChild;
import io.airbyte.singer.SingerStream;
import io.airbyte.singer.SingerType;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class SingerCatalogConverters {

  /**
   * Takes in a singer catalog and a airbyte schema. It then applies the airbyte configuration to that
   * catalog. e.g. If airbyte says that a certain field should or should not be included in the sync,
   * this method applies that to the catalog. Thus we produce a valid singer catalog that contains
   * configurations stored in airbyte.
   *
   * @param catalog - singer catalog
   * @param schema - airbyte schema
   * @return singer catalog with airbyte schema applied to it.
   */
  public static SingerCatalog applySchemaToDiscoveredCatalog(SingerCatalog catalog, Schema schema) {
    Map<String, Stream> streamNameToAirbyteStream = schema.getStreams()
        .stream()
        .collect(Collectors.toMap(Stream::getName, stream -> stream));

    final List<SingerStream> updatedStreams =
        catalog.getStreams().stream()
            .map(
                stream -> {

                  // recourse here is probably to run discovery again and update sync
                  // configuration. this method just outputs the original metadata.
                  if (!streamNameToAirbyteStream.containsKey(stream.getStream())) {
                    return stream;
                  }
                  final Stream airbyteStream = streamNameToAirbyteStream.get(stream.getStream());
                  final Map<String, Field> fieldNameToField =
                      airbyteStream.getFields()
                          .stream()
                          .collect(Collectors.toMap(Field::getName, field -> field));

                  final List<SingerMetadata> newMetadata =
                      stream.getMetadata().stream()
                          .map(
                              metadata -> {
                                final SingerMetadata newSingerMetadata = Jsons.clone(metadata);
                                if (isFieldMetadata(metadata)) {
                                  // field metadata
                                  final String fieldName = getFieldName(metadata);
                                  // recourse here is probably to run discovery again and update
                                  // sync configuration. this method just outputs the original
                                  // metadata.
                                  if (!fieldNameToField.containsKey(fieldName)) {
                                    return metadata;
                                  }
                                  final Field field = fieldNameToField.get(fieldName);

                                  newSingerMetadata.getMetadata().setSelected(field.getSelected());
                                } else {

                                  // stream metadata
                                  // TODO HACK set replication mode to full_refresh on every stream
                                  // to unblock some other dev work. Needs to be fixed ASAP. Sherif
                                  // is working on this.

                                  newSingerMetadata.getMetadata()
                                      .withReplicationMethod(SingerMetadataChild.ReplicationMethod.FULL_TABLE)
                                      .withSelected(airbyteStream.getSelected());
                                }
                                return newSingerMetadata;
                              })
                          .collect(Collectors.toList());

                  return new SingerStream()
                      .withStream(stream.getStream())
                      .withTableName(stream.getTableName())
                      .withTapStreamId(stream.getTapStreamId())
                      // TODO
                      .withMetadata(newMetadata)
                      // todo (cgardens) - this will not work for legacy catalogs. want to handle this
                      // in a subsequent PR, because handling this is going to require doing another
                      // one of these monster map tasks.
                      .withSchema(stream.getSchema());
                })
            .collect(Collectors.toList());

    return new SingerCatalog().withStreams(updatedStreams);
  }

  // assumes discoverable input only.
  public static Schema toAirbyteSchema(SingerCatalog catalog) {
    Map<String, List<SingerMetadata>> streamNameToMetadata =
        getStreamNameToMetadataList(catalog.getStreams());

    List<Stream> streams = catalog.getStreams()
        .stream()
        .map(
            stream -> {
              final Map<String, SingerMetadataChild> fieldNameToMetadata =
                  getFieldMetadataForStream(streamNameToMetadata, stream.getStream());
              final SingerMetadata streamMetadata = streamNameToMetadata.get(stream.getStream())
                  .stream()
                  .filter(metadata -> metadata.getBreadcrumb().equals(new ArrayList<>()))
                  .findFirst()
                  .orElseThrow(() -> new RuntimeException("Could not find stream metadata"));
              return new Stream()
                  .withName(stream.getStream())
                  .withSelected(isSelected(streamMetadata.getMetadata()))
                  .withFields(
                      stream
                          .getSchema()
                          .getProperties()
                          .getAdditionalProperties()
                          .entrySet()
                          .stream()
                          .map(
                              entry -> {
                                final String fieldName = entry.getKey();
                                final SingerColumn singerField = entry.getValue();
                                final SingerMetadataChild singerFieldMetadata =
                                    fieldNameToMetadata.get(fieldName);

                                final Field field = new Field();
                                field.withName(fieldName);
                                field.withDataType(singerTypesToDataType(singerField.getType()));
                                // in discovery, you can find fields that are replicated by
                                // default. we set those to selected. the rest are not.
                                field.withSelected(isSelected(singerFieldMetadata));
                                return field;
                              })
                          .collect(Collectors.toList()));
            })
        .collect(Collectors.toList());

    return new Schema().withStreams(streams);
  }

  private static boolean isSelected(SingerMetadataChild metadataChild) {
    Boolean selected = metadataChild.getSelected();
    if (selected != null) {
      return metadataChild.getSelected();
    }
    Boolean selectedByDefault = metadataChild.getSelectedByDefault();
    if (selectedByDefault != null) {
      return selectedByDefault;
    }

    // absent of a default, don't replicate by default.
    return false;
  }

  private static Map<String, List<SingerMetadata>> getStreamNameToMetadataList(List<SingerStream> streams) {
    // todo (cgardens) - figure out if it's stream or stream id or stream name.
    return streams.stream()
        .collect(Collectors.toMap(SingerStream::getStream, SingerStream::getMetadata));
  }

  private static Map<String, SingerMetadataChild> getFieldMetadataForStream(Map<String, List<SingerMetadata>> streamNameToMetadata,
                                                                            String streamName) {
    if (!streamNameToMetadata.containsKey(streamName)) {
      throw new RuntimeException("could not find metadata for stream: " + streamName);
    }
    return streamNameToMetadata.get(streamName).stream()
        // singer breadcrumb is empty if it is stream metadata and it it has two
        // items if it is field metadata. the first item is "properties" and
        // the second item is the field name.
        .filter(SingerCatalogConverters::isFieldMetadata)
        .collect(
            Collectors.toMap(
                metadata -> metadata.getBreadcrumb().get(1), SingerMetadata::getMetadata));
  }

  private static boolean isFieldMetadata(SingerMetadata metadata) {
    // field metadata must have 2 breadcrumb entries
    if (metadata.getBreadcrumb().size() != 2) {
      return false;
    }
    // field metadata must have first breadcrumb be property
    return !metadata.getBreadcrumb().get(0).equals("property");
  }

  private static String getFieldName(SingerMetadata metadata) {
    if (!isFieldMetadata(metadata)) {
      throw new RuntimeException("Cannot get field name for non-field metadata");
    }

    return metadata.getBreadcrumb().get(1);
  }

  /**
   * Singer tends to have 2 types for fields one of which is null. The null is pretty irrelevant, so
   * look at types and find the first non-null one and use that.
   *
   * @param singerTypes - list of types discovered by singer.
   * @return reduce down to one type which best matches the field's data type
   */
  private static DataType singerTypesToDataType(List<SingerType> singerTypes) {
    return singerTypes.stream()
        .filter(singerType -> !SingerType.NULL.equals(singerType))
        .map(SingerCatalogConverters::singerTypeToDataType)
        .findFirst()
        .orElse(DataType.STRING);
  }

  /**
   * Singer doesn't seem to have an official list of the data types that they support, so we will have
   * to do our best here as we discover them. If it becomes too awful, we can just map types we don't
   * recognize to string.
   *
   * @param singerType - singer's field data type
   * @return best match for our own data type
   */
  private static DataType singerTypeToDataType(SingerType singerType) {
    switch (singerType) {
      case STRING:
        return DataType.STRING;
      case INTEGER:
        return DataType.NUMBER;
      case NULL:
        // noinspection DuplicateBranchesInSwitch
        return DataType.STRING; // todo (cgardens) - hackasaurus rex
      case BOOLEAN:
        return DataType.BOOLEAN;
      default:
        throw new RuntimeException(
            String.format("could not map SingerType: %s to DataType", singerType));
    }
  }

}
