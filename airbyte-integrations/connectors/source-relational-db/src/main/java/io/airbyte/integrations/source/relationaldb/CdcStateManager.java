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

package io.airbyte.integrations.source.relationaldb;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CdcStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(StateManager.class);

  private final CdcState initialState;

  private CdcState currentState;

  @VisibleForTesting
  CdcStateManager(CdcState serialized) {
    this.initialState = serialized;
    this.currentState = serialized;

    LOGGER.info("Initialized CDC state with: {}", serialized);
  }

  public void setCdcState(CdcState state) {
    this.currentState = state;
  }

  public CdcState getCdcState() {
    return currentState != null ? Jsons.clone(currentState) : null;
  }

  @Override
  public String toString() {
    return "JdbcCdcStateManager{" +
        "initialState=" + initialState +
        ", currentState=" + currentState +
        '}';
  }

}
