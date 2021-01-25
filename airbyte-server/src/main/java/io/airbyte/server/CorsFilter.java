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

package io.airbyte.server;

import javax.ws.rs.container.ContainerRequestContext;
import javax.ws.rs.container.ContainerResponseContext;
import javax.ws.rs.container.ContainerResponseFilter;

// https://medium.com/@Leejjon_net/how-to-allow-cross-origin-requests-in-a-jax-rs-microservice-d2a6aa2df484
public class CorsFilter implements ContainerResponseFilter {

  private static final String ALLOW_ORIGIN = "Access-Control-Allow-Origin";
  private static final String ALLOW_HEADERS = "Access-Control-Allow-Headers";
  private static final String ALLOW_METHODS = "Access-Control-Allow-Methods";

  @Override
  public void filter(ContainerRequestContext requestContext,
                     ContainerResponseContext responseContext) {
    responseContext.getHeaders().add(ALLOW_ORIGIN, "*");
    responseContext.getHeaders().add(ALLOW_HEADERS, "Origin, Content-Type, Accept, Content-Encoding");
    responseContext.getHeaders().add(ALLOW_METHODS, "GET, POST, PUT, DELETE, OPTIONS, HEAD");
  }

}
