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

import io.airbyte.api.model.InvalidInputExceptionInfo;
import io.airbyte.api.model.InvalidInputProperty;
import io.airbyte.commons.json.Jsons;
import java.util.ArrayList;
import java.util.List;
import javax.validation.ConstraintViolation;
import javax.validation.ConstraintViolationException;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;
import org.apache.logging.log4j.core.util.Throwables;

// https://www.baeldung.com/jersey-bean-validation#custom-exception-handler
// handles exceptions related to the request body not matching the openapi config.
@Provider
public class InvalidInputExceptionMapper implements ExceptionMapper<ConstraintViolationException> {

  public static InvalidInputExceptionInfo infoFromConstraints(ConstraintViolationException cve) {
    InvalidInputExceptionInfo exceptionInfo = new InvalidInputExceptionInfo()
        .exceptionClassName(cve.getClass().getName())
        .message("Some properties contained invalid input.")
        .exceptionStack(Throwables.toStringList(cve));

    List<InvalidInputProperty> props = new ArrayList<InvalidInputProperty>();
    for (ConstraintViolation<?> cv : cve.getConstraintViolations()) {
      props.add(new InvalidInputProperty()
          .propertyPath(cv.getPropertyPath().toString())
          .message(cv.getMessage())
          .invalidValue(cv.getInvalidValue() != null ? cv.getInvalidValue().toString() : "null"));
    }
    exceptionInfo.validationErrors(props);
    return exceptionInfo;
  }

  @Override
  public Response toResponse(ConstraintViolationException e) {
    return Response.status(Response.Status.BAD_REQUEST)
        .entity(Jsons.serialize(InvalidInputExceptionMapper.infoFromConstraints(e)))
        .type("application/json")
        .build();
  }

}
