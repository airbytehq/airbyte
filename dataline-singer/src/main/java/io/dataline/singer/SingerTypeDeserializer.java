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

package io.dataline.singer;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.ObjectCodec;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.exc.MismatchedInputException;
import com.fasterxml.jackson.databind.type.ArrayType;
import com.fasterxml.jackson.databind.type.SimpleType;
import io.dataline.commons.json.Jsons;
import java.io.IOException;
import java.util.Collections;
import java.util.List;

public class SingerTypeDeserializer extends JsonDeserializer<List<SingerType>> {

  @Override
  public List<SingerType> deserialize(JsonParser p, DeserializationContext ctxt) throws IOException {
    ObjectCodec oc = p.getCodec();
    JsonNode node = oc.readTree(p);
    if (node.isArray()) {
      return Jsons.object(node, new TypeReference<>() {});
    } else if (node.isTextual()) {
      return Collections.singletonList(Jsons.object(node, SingerType.class));
    }
    throw MismatchedInputException.from(
        p,
        ArrayType.construct(SimpleType.constructUnsafe(SingerType.class), null),
        String.format("Cannot deserialize instance of `%s` out of %s token", "List<SingerType>", node.getNodeType()));
  }

}
