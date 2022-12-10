package io.airbyte.connectorbuilder.controllers;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.IOUtils;

import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;

@Controller("/v1/streams/read")
@Slf4j
public class ReadController {

    @Post(produces = MediaType.TEXT_PLAIN)
    public String manifest(final StreamReadRequestBody body) throws IOException, InterruptedException {
        final String json = new ObjectMapper().writer().writeValueAsString(body);

        //final File f = new File(".");
        //return Arrays.stream(f.listFiles()).map(s -> s.toString()).collect(Collectors.joining());
        log.info("Recevied read request with body: " + body);
        final ProcessBuilder processBuilder = new ProcessBuilder("python3.9", "connector_builder/entrypoint.py", "read", json);
        processBuilder.redirectErrorStream(true);

        final Process process = processBuilder.start();

        final List<String> results = IOUtils.readLines(process.getInputStream());
//        final int exitCode = process.waitFor();

        return results.stream().collect(Collectors.joining());
    }
}
