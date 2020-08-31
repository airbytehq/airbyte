/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.server.helpers;

import io.dataline.config.SourceConnectionSpecification;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

public class SourceSpecificationHelpers {

  public static SourceConnectionSpecification generateSourceSpecification() throws IOException {
    final UUID sourceId = UUID.randomUUID();
    final UUID sourceSpecificationId = UUID.randomUUID();

    final Path path =
        Paths.get("../dataline-server/src/test/resources/json/TestSpecification.json");

    final SourceConnectionSpecification sourceConnectionSpecification =
        new SourceConnectionSpecification();
    sourceConnectionSpecification.setSourceId(sourceId);
    sourceConnectionSpecification.setSourceSpecificationId(sourceSpecificationId);
    sourceConnectionSpecification.setSpecificationJson(Files.readString(path));

    return sourceConnectionSpecification;
  }

}
