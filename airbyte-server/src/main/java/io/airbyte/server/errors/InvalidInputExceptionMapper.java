/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

import io.airbyte.api.model.InvalidInputExceptionInfo;
import io.airbyte.api.model.InvalidInputProperty;
import io.airbyte.commons.json.Jsons;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Produces;
import io.micronaut.http.server.exceptions.ExceptionHandler;
import java.util.ArrayList;
import java.util.List;
import javax.inject.Singleton;
import javax.validation.ConstraintViolation;
import javax.validation.ConstraintViolationException;
import org.apache.logging.log4j.core.util.Throwables;

// https://www.baeldung.com/jersey-bean-validation#custom-exception-handler
// handles exceptions related to the request body not matching the openapi config.
@Produces
@Singleton
@Requires(classes = ConstraintViolationException.class)
public class InvalidInputExceptionMapper implements ExceptionHandler<ConstraintViolationException, HttpResponse> {

  public static InvalidInputExceptionInfo infoFromConstraints(final ConstraintViolationException cve) {
    final List<InvalidInputProperty> props = new ArrayList<InvalidInputProperty>();
    for (final ConstraintViolation<?> cv : cve.getConstraintViolations()) {
      props.add(new InvalidInputProperty()
          .message(cv.getMessage())
          .propertyPath(cv.getPropertyPath().toString())
          .invalidValue(cv.getInvalidValue() != null ? cv.getInvalidValue().toString() : "null"));
    }
    final InvalidInputExceptionInfo exceptionInfo = new InvalidInputExceptionInfo()
        .exceptionClassName(cve.getClass().getName())
        .exceptionStack(Throwables.toStringList(cve))
        .message("Some properties contained invalid input.")
        .validationErrors(props);
    return exceptionInfo;
  }

  @Override
  public HttpResponse handle(final HttpRequest request, final ConstraintViolationException exception) {
    return HttpResponse.status(HttpStatus.BAD_REQUEST)
        .body(Jsons.serialize(InvalidInputExceptionMapper.infoFromConstraints(exception)))
        .contentType(MediaType.APPLICATION_JSON_TYPE);
  }

}
