/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.connectorbuilder.controllers;

import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Get;

@Controller("/v1/manifest_template")
public class ManifestTemplateController {

  @Get(produces = MediaType.TEXT_PLAIN)
  public String manifest() {
    return "version: \"0.1.0\"\n" +
        "definitions:\n" +
        "  selector:\n" +
        "    extractor:\n" +
        "      field_pointer: []\n" +
        "  requester:\n" +
        "    url_base: \"https://example.com\"\n" +
        "    http_method: \"GET\"\n" +
        "    authenticator:\n" +
        "      type: BearerAuthenticator\n" +
        "      api_token: \"{{ config['api_key'] }}\"\n" +
        "  retriever:\n" +
        "    record_selector:\n" +
        "      $ref: \"*ref(definitions.selector)\"\n" +
        "    paginator:\n" +
        "      type: NoPagination\n" +
        "    requester:\n" +
        "      $ref: \"*ref(definitions.requester)\"\n" +
        "  base_stream:\n" +
        "    retriever:\n" +
        "      $ref: \"*ref(definitions.retriever)\"\n" +
        "  customers_stream:\n" +
        "    $ref: \"*ref(definitions.base_stream)\"\n" +
        "    $options:\n" +
        "      name: \"customers\"\n" +
        "      primary_key: \"id\"\n" +
        "      path: \"/example\"\n" +
        "\n" +
        "streams:\n" +
        "  - \"*ref(definitions.customers_stream)\"\n" +
        "\n" +
        "check:\n" +
        "  stream_names:\n" +
        "    - \"customers\"\n" +
        "\n" +
        "spec:\n" +
        "  documentation_url: https://docsurl.com\n" +
        "  connection_specification:\n" +
        "    title: Source Name Spec # 'TODO: Replace this with the name of your source.'\n" +
        "    type: object\n" +
        "    required:\n" +
        "      - api_key\n" +
        "    additionalProperties: true\n" +
        "    properties:\n" +
        "      # 'TODO: This schema defines the configuration required for the source. This usually involves metadata such as database and/or authentication information.':\n"
        +
        "      api_key:\n" +
        "        type: string\n" +
        "        description: API Key";
  }

}
