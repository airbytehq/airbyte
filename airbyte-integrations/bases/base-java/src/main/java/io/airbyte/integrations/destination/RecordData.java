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

package io.airbyte.integrations.destination;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.airbyte.commons.json.Jsons;
import java.sql.Timestamp;
import java.time.Instant;

/**
 * This class is an immutable POJO containing all data necessary to write an
 * {@link io.airbyte.protocol.models.AirbyteRecordMessage} to a Destination.
 *
 * This removes the need to pass the entire AirbyteRecordMessage around internally, which make syncs
 * slightly more efficient.
 *
 * It's immutable nature - there are no method to allow internal state modification - help with
 * readability.
 *
 * Internal Destination interfaces should use this when necessary.
 */
public class RecordData {

  @JsonProperty("jsonData")
  private final String jsonData;

  @JsonProperty("emittedAt")
  private final Timestamp emittedAt;

  public RecordData(String jsonData, Timestamp emittedAt) {
    this.jsonData = jsonData;
    this.emittedAt = emittedAt;
  }

  public String getJsonData() {
    return jsonData;
  }

  public Timestamp getEmittedAt() {
    return emittedAt;
  }

  public static void main(String[] args) {
    var r = new RecordData("her her", Timestamp.from(Instant.now()));
    var str = Jsons.serialize(r);
    System.out.println(str);

    var o = Jsons.deserialize(str, RecordData.class);
    System.out.println(o.getEmittedAt());
    System.out.println(o.getJsonData());
  }

}
