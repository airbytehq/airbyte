/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

import io.airbyte.api.model.generated.InvalidInputExceptionInfo;
import io.airbyte.api.model.generated.InvalidInputProperty;
import io.airbyte.commons.json.Jsons;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Produces;
import io.micronaut.http.server.exceptions.ExceptionHandler;
import jakarta.inject.Singleton;
import java.util.ArrayList;
import java.util.List;
import javax.validation.ConstraintViolation;
import javax.validation.ConstraintViolationException;
import org.apache.logging.log4j.core.util.Throwables;

// https://www.baeldung.com/jersey-bean-validation#custom-exception-handler
// handles exceptions related to the request body not matching the openapi config.
@Produces
@Singleton
@Requires(classes = ConstraintViolationException.class)
public class InvalidInputExceptionHandler implements ExceptionHandler<ConstraintViolationException, HttpResponse> {

  public static InvalidInputExceptionInfo infoFromConstraints(final ConstraintViolationException cve) {
    final InvalidInputExceptionInfo exceptionInfo = new InvalidInputExceptionInfo()
        .exceptionClassName(cve.getClass().getName())
        .message("Some properties contained invalid input.")
        .exceptionStack(Throwables.toStringList(cve));

    final List<InvalidInputProperty> props = new ArrayList<InvalidInputProperty>();
    for (final ConstraintViolation<?> cv : cve.getConstraintViolations()) {
      props.add(new InvalidInputProperty()
          .propertyPath(cv.getPropertyPath().toString())
          .message(cv.getMessage())
          .invalidValue(cv.getInvalidValue() != null ? cv.getInvalidValue().toString() : "null"));
    }
    exceptionInfo.validationErrors(props);
    return exceptionInfo;
  }

  @Override
  public HttpResponse handle(final HttpRequest request, final ConstraintViolationException exception) {
    return HttpResponse.status(HttpStatus.BAD_REQUEST)
        .body(Jsons.serialize(InvalidInputExceptionHandler.infoFromConstraints(exception)))
        .contentType(MediaType.APPLICATION_JSON_TYPE);
  }

}
