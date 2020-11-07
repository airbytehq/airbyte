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

package io.airbyte.validation.json;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SchemaValidatorsConfig;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;
import io.airbyte.commons.string.Strings;
import java.io.File;
import java.io.IOException;
import java.util.Set;
import me.andrz.jackson.JsonReferenceException;
import me.andrz.jackson.JsonReferenceProcessor;

public class JsonSchemaValidator {

  private final SchemaValidatorsConfig schemaValidatorsConfig;
  private final JsonSchemaFactory jsonSchemaFactory;

  public JsonSchemaValidator() {
    this.schemaValidatorsConfig = new SchemaValidatorsConfig();
    this.jsonSchemaFactory = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7);
  }

  public Set<ValidationMessage> validate(JsonNode schemaJson, JsonNode objectJson) {
    Preconditions.checkNotNull(schemaJson);
    Preconditions.checkNotNull(objectJson);

    return jsonSchemaFactory.getSchema(schemaJson, schemaValidatorsConfig)
        .validate(objectJson);
  }

  public boolean test(JsonNode schemaJson, JsonNode objectJson) {
    return validate(schemaJson, objectJson).isEmpty();
  }

  public void ensure(JsonNode schemaJson, JsonNode objectJson) throws JsonValidationException {
    final Set<ValidationMessage> validationMessages = validate(schemaJson, objectJson);
    if (validationMessages.isEmpty()) {
      return;
    }

    throw new JsonValidationException(String.format(
        "json schema validation failed. \nerrors: %s \nschema: \n%s \nobject: \n%s",
        Strings.join(validationMessages, ", "),
        schemaJson.toPrettyString(),
        objectJson.toPrettyString()));
  }

  public static JsonNode getSchema(final File schemaFile) {
    try {
      // JsonReferenceProcessor follows $ref in json objects. Jackson does not natively support
      // this.
      final JsonReferenceProcessor jsonReferenceProcessor = new JsonReferenceProcessor();
      jsonReferenceProcessor.setMaxDepth(-1); // no max.
      return jsonReferenceProcessor.process(schemaFile);
    } catch (IOException | JsonReferenceException e) {
      throw new RuntimeException(e);
    }
  }

  public static void main(String[] args) {
    String s = "{\n" +
        "  \"documentationUrl\": \"https://docs.airbyte.io/integrations/sources/file\",\n" +
        "\n" +
        "  \"connectionSpecification\": {\n" +
        "    \"$schema\": \"http://json-schema.org/draft-07/schema#\",\n" +
        "    \"title\": \"File Source Spec\",\n" +
        "    \"type\": \"object\",\n" +
        "    \"required\": [\"url\", \"storage\"],\n" +
        "    \"additionalProperties\": true,\n" +
        "    \"properties\": {\n" +
        "      \"format\": {\n" +
        "        \"type\": \"string\",\n" +
        "        \"enum\": [\n" +
        "          \"csv\",\n" +
        "          \"json\",\n" +
        "          \"html\",\n" +
        "          \"excel\",\n" +
        "          \"feather\",\n" +
        "          \"parquet\",\n" +
        "          \"orc\",\n" +
        "          \"pickle\"\n" +
        "        ],\n" +
        "        \"default\": \"csv\",\n" +
        "        \"description\": \"File Format of the file to be replicated. Common formats are (csv, json or excel) but more advanced formats can be specified (html, parquet, orc, feather, pickle)\",\n"
        +
        "        \"examples\": [\"csv\"]\n" +
        "      },\n" +
        "      \"reader_options\": {\n" +
        "        \"type\": \"string\",\n" +
        "        \"description\": \"Parsers for File Formats are currently using the `read_*` methods from the Pandas Library. Each of these readers provides additional options that can be specified as part of this JSON string. As an example, it is possible to change the read_csv behavior to a TSV (tab separated instead of comma) when redefining the delimiter character. See documentation of each `read_*` primitive from here: https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html\",\n"
        +
        "        \"examples\": [\"{}\", \"{'sep': ' '}\"]\n" +
        "      },\n" +
        "\n" +
        "      \"storage\": {\n" +
        "        \"type\": \"string\",\n" +
        "        \"enum\": [\"HTTPS\", \"GCS\", \"S3\", \"SSH\", \"SFTP\", \"WebHDFS\", \"local\"],\n" +
        "        \"description\": \"Storage Provider or Location of the file(s) to be replicated. (Note that local storage of directory where csv files will be read must start with the local mount \\\"/local\\\" at the moment until we implement more advanced mounting options)\",\n"
        +
        "        \"default\": \"HTTPS\"\n" +
        "      },\n" +
        "\n" +
        "      \"url\": {\n" +
        "        \"type\": \"string\",\n" +
        "        \"description\": \"URL path to access the file to be replicated\"\n" +
        "      },\n" +
        "\n" +
        "      \"filename\": {\n" +
        "        \"type\": \"string\",\n" +
        "        \"description\": \"Name of the file (should include only letters, numbers dash and underscores)\"\n" +
        "      }\n" +
        "    },\n" +
        "\n" +
        "    \"dependencies\": {\n" +
        "      \"storage\": {\n" +
        "        \"oneOf\": [\n" +
        "          {\n" +
        "            \"properties\": {\n" +
        "              \"storage\": {\n" +
        "                \"enum\": [\"HTTPS\"]\n" +
        "              }\n" +
        "            }\n" +
        "          },\n" +
        "          {\n" +
        "            \"properties\": {\n" +
        "              \"storage\": {\n" +
        "                \"enum\": [\"GCS\"]\n" +
        "              },\n" +
        "              \"service_account_json\": {\n" +
        "                \"type\": \"string\",\n" +
        "                \"description\": \"In order to access private Buckets stored on Google Cloud, this connector would need a service account json credentials with the proper permissions as described here: https://cloud.google.com/iam/docs/service-accounts Please generate the credentials.json file and copy/paste its content to this field (expecting JSON formats). If accessing publicly available data, this field is not necessary.\"\n"
        +
        "              },\n" +
        "              \"reader_impl\": {\n" +
        "                \"type\": \"string\",\n" +
        "                \"enum\": [\"smart_open\", \"gcsfs\"],\n" +
        "                \"default\": \"gcsfs\",\n" +
        "                \"description\": \"This connector provides multiple methods to retrieve data from GCS using either smart-open python libraries or GCSFS\"\n"
        +
        "              }\n" +
        "            }\n" +
        "          },\n" +
        "\n" +
        "          {\n" +
        "            \"properties\": {\n" +
        "              \"storage\": {\n" +
        "                \"enum\": [\"S3\"]\n" +
        "              },\n" +
        "              \"aws_access_key_id\": {\n" +
        "                \"type\": \"string\",\n" +
        "                \"description\": \"In order to access private Buckets stored on AWS S3, this connector would need credentials with the proper permissions. If accessing publicly available data, this field is not necessary.\"\n"
        +
        "              },\n" +
        "              \"aws_secret_access_key\": {\n" +
        "                \"type\": \"string\",\n" +
        "                \"description\": \"In order to access private Buckets stored on AWS S3, this connector would need credentials with the proper permissions. If accessing publicly available data, this field is not necessary.\"\n"
        +
        "              },\n" +
        "              \"reader_impl\": {\n" +
        "                \"type\": \"string\",\n" +
        "                \"enum\": [\"smart_open\", \"s3fs\"],\n" +
        "                \"default\": \"s3fs\",\n" +
        "                \"description\": \"This connector provides multiple methods to retrieve data from AWS S3 using either smart-open python libraries or S3FS\"\n"
        +
        "              }\n" +
        "            }\n" +
        "          },\n" +
        "\n" +
        "          {\n" +
        "            \"properties\": {\n" +
        "              \"storage\": {\n" +
        "                \"enum\": [\"SSH\"]\n" +
        "              },\n" +
        "              \"user\": {\n" +
        "                \"type\": \"string\"\n" +
        "              },\n" +
        "              \"password\": {\n" +
        "                \"type\": \"string\"\n" +
        "              },\n" +
        "              \"host\": {\n" +
        "                \"type\": \"string\"\n" +
        "              }\n" +
        "            },\n" +
        "            \"required\": [\"user\", \"host\"]\n" +
        "          },\n" +
        "\n" +
        "          {\n" +
        "            \"properties\": {\n" +
        "              \"storage\": {\n" +
        "                \"enum\": [\"SFTP\"]\n" +
        "              },\n" +
        "              \"user\": {\n" +
        "                \"type\": \"string\"\n" +
        "              },\n" +
        "              \"password\": {\n" +
        "                \"type\": \"string\"\n" +
        "              },\n" +
        "              \"host\": {\n" +
        "                \"type\": \"string\"\n" +
        "              }\n" +
        "            },\n" +
        "            \"required\": [\"user\", \"host\"]\n" +
        "          },\n" +
        "          \n" +
        "          {\n" +
        "            \"properties\": {\n" +
        "              \"storage\": {\n" +
        "                \"enum\": [\"WebHDFS\"]\n" +
        "              },\n" +
        "              \"host\": {\n" +
        "                \"type\": \"string\"\n" +
        "              },\n" +
        "              \"port\": {\n" +
        "                \"type\": \"number\"\n" +
        "              }\n" +
        "            },\n" +
        "            \"required\": [\"host\", \"port\"]\n" +
        "          }\n" +
        "        ]\n" +
        "      }\n" +
        "    }\n" +
        "  }\n" +
        "}\n";

    String obj = "{\n" +
        "        \"url\" : \"https://people.sc.fsu.edu/~jburkardt/data/csv/addresses.csv\",\n" +
        "        \"format\" : \"csv\",\n" +
        "        \"storage\" : \"HTTPS\",\n" +
        "        \"reader_options\" : \"{}\"\n" +
        "     }";
  }

}
