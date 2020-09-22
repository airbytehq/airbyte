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

package io.airbyte.commons.io;

import java.util.AbstractMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.event.Level;

public class LogTypeMapper implements Consumer<String> {

  private static final Map<Level, Function<Logger, Consumer<String>>> LEVEL_TO_CONSUMER_FACTORY = Map.ofEntries(
      new AbstractMap.SimpleEntry<>(Level.ERROR, logger -> logger::error),
      new AbstractMap.SimpleEntry<>(Level.WARN, logger -> logger::warn),
      new AbstractMap.SimpleEntry<>(Level.INFO, logger -> logger::info),
      new AbstractMap.SimpleEntry<>(Level.DEBUG, logger -> logger::debug),
      new AbstractMap.SimpleEntry<>(Level.TRACE, logger -> logger::trace));

  private final Logger logger;
  private final Function<Logger, Consumer<String>> defaultLogConsumerFactory;

  public LogTypeMapper(Logger logger, Function<Logger, Consumer<String>> defaultLogConsumerFactory) {
    this.logger = logger;
    this.defaultLogConsumerFactory = defaultLogConsumerFactory;
  }

  @Override
  public void accept(String message) {
    getConsumer(message).accept(message);
  }

  private Consumer<String> getConsumer(String message) {
    for (Level level : LEVEL_TO_CONSUMER_FACTORY.keySet()) {
      if (message.startsWith(level.toString())) {
        return LEVEL_TO_CONSUMER_FACTORY.get(level).apply(logger);
      }
    }

    return defaultLogConsumerFactory.apply(logger);
  }

}
