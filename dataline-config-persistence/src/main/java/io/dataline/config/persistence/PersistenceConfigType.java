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

package io.dataline.config.persistence;

public enum PersistenceConfigType {
  // workspace
  STANDARD_WORKSPACE,

  // source
  STANDARD_SOURCE,
  SOURCE_CONNECTION_SPECIFICATION,
  SOURCE_CONNECTION_IMPLEMENTATION,

  // destination
  STANDARD_DESTINATION,
  DESTINATION_CONNECTION_SPECIFICATION,
  DESTINATION_CONNECTION_IMPLEMENTATION,

  // test connection
  STANDARD_CONNECTION_STATUS,

  // discover schema
  STANDARD_DISCOVERY_OUTPUT,

  // sync
  STANDARD_SYNC,
  STANDARD_SYNC_SUMMARY,
  STANDARD_SYNC_SCHEDULE,
  STATE,
}
