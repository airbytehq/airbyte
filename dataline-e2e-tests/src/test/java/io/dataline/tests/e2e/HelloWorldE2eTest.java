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

package io.dataline.tests.e2e;

import io.dataline.api.model.SourceReadList;
import io.dataline.commons.json.Jsons;
import java.io.IOException;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import org.junit.jupiter.api.Test;

public class HelloWorldE2eTest {
  static final MediaType JSON_CONTENT = MediaType.get("application/json; charset=utf-8");
  static final String SERVER_URL = "http://localhost:8001/api/v1/";

  @Test
  public void dontRunAsPartOfBuild() throws IOException {
    OkHttpClient client = new OkHttpClient();
    System.out.println("Hello e2e!");
    getPostgresSourceId(client, "sources/list", "");
  }

  private <T> SourceReadList getPostgresSourceId(
      OkHttpClient httpClient, String relativePath, T requestBody) throws IOException {
    RequestBody body = RequestBody.create(Jsons.serialize(requestBody), JSON_CONTENT);
    Request request = new Request.Builder().post(body).url(SERVER_URL + relativePath).build();
    try (Response response = httpClient.newCall(request).execute()) {
      System.out.println(response);
      return Jsons.deserialize(response.body().string(), SourceReadList.class);
    }
  }
}
