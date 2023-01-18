/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.connectorbuilder.controllers;

import io.airbyte.connectorbuilder.clients.RedirectClient;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Get;

@Controller("/v1/manifest_template")
public class ManifestTemplateController {

    @Get(produces = MediaType.TEXT_PLAIN)
    public String manifest() {
        return new RedirectClient().manifest();
    }

}
