package io.airbyte.connectorbuilder.controllers;

import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;

@Controller("/v1/streams/list")
public class ListController {

    @Post(produces = MediaType.TEXT_PLAIN)
    public String manifest() {
        return "{\"list\": false}";
    }
}
