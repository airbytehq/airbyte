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

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import javax.validation.ConstraintViolation;
import javax.validation.ConstraintViolationException;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;

// https://www.baeldung.com/jersey-bean-validation#custom-exception-handler
// handles exceptions related to the request body not matching the openapi config.
@Provider
public class InvalidInputExceptionMapper implements ExceptionMapper<ConstraintViolationException> {

  @Override
  public Response toResponse(ConstraintViolationException exception) {
    return Response.status(Response.Status.BAD_REQUEST)
        .entity(
            Jsons.serialize(
                ImmutableMap.of(
                    "message",
                    "The received object did not pass validation",
                    "details",
                    prepareMessage(exception))))
        .type("application/json")
        .build();
  }

  private String prepareMessage(ConstraintViolationException exception) {
    final StringBuilder message = new StringBuilder();
    for (ConstraintViolation<?> cv : exception.getConstraintViolations()) {
      message.append(
          "property: "
              + cv.getPropertyPath()
              + " message: "
              + cv.getMessage()
              + " invalid value: "
              + cv.getInvalidValue());
    }
    return message.toString();
  }

}
