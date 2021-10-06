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

import io.airbyte.api.model.NotFoundKnownExceptionInfo;
import org.apache.logging.log4j.core.util.Throwables;

public class IdNotFoundKnownException extends KnownException {

  String id;

  public IdNotFoundKnownException(String message, String id) {
    super(message);
    this.id = id;
  }

  public IdNotFoundKnownException(String message, String id, Throwable cause) {
    super(message, cause);
    this.id = id;
  }

  public IdNotFoundKnownException(String message, Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return 404;
  }

  public String getId() {
    return id;
  }

  public NotFoundKnownExceptionInfo getNotFoundKnownExceptionInfo() {
    NotFoundKnownExceptionInfo exceptionInfo = new NotFoundKnownExceptionInfo()
        .exceptionClassName(this.getClass().getName())
        .message(this.getMessage())
        .exceptionStack(Throwables.toStringList(this));
    if (this.getCause() != null) {
      exceptionInfo.rootCauseExceptionClassName(this.getClass().getClass().getName());
      exceptionInfo.rootCauseExceptionStack(Throwables.toStringList(this.getCause()));
    }
    exceptionInfo.id(this.getId());
    return exceptionInfo;
  }

}
