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

package io.airbyte.server.services;

import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpResponse.BodyHandlers;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Convenience class for retrieving files checked into the Airbyte Github repo.
 */

public class BlotoutAuthentication {

    private final Configs configs = new EnvConfigs();

    private static final HttpClient httpClient = HttpClient.newHttpClient();
    private static final Logger LOGGER = LoggerFactory.getLogger(BlotoutAuthentication.class);

    public boolean validateToken(String token) throws IOException, InterruptedException {
        final var request = HttpRequest
                .newBuilder(URI.create(configs.getBlotoutBaseUrl() + configs.getBlotoutAuthEndpoint()))
                .timeout(Duration.ofSeconds(120))
                .header("Content-Type", "application/json") // connect type
                .header("token", token) // validate token
                .build();
        HttpResponse response = httpClient.send(request, BodyHandlers.ofString());
        LOGGER.info(" response " + response.body());
        if (response.statusCode() == 200) {
            return true;
        } else {
            return false;
        }
    }

}