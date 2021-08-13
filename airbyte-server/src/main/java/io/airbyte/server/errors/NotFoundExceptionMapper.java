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

package io.airbyte.server.errors;

import io.airbyte.commons.json.Jsons;
import javax.ws.rs.NotFoundException;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class NotFoundExceptionMapper implements ExceptionMapper<NotFoundException> {

  private static final Logger LOGGER = LoggerFactory.getLogger(NotFoundExceptionMapper.class);

  @Override
  public Response toResponse(NotFoundException e) {
    // Would like to send the id along but we don't have access to the http request anymore to fetch it
    // from. TODO: Come back to this with issue #4189
    IdNotFoundKnownException idnf = new IdNotFoundKnownException("Object not found. " + e.getMessage(), e);
    LOGGER.error("Not found exception", idnf.getNotFoundKnownExceptionInfo());
    return Response.status(404)
        .entity(Jsons.serialize(idnf.getNotFoundKnownExceptionInfo()))
        .type("application/json")
        .build();
  }

}
