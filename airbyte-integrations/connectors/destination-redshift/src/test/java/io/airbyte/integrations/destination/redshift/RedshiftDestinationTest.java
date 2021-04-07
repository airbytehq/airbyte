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

package io.airbyte.integrations.destination.redshift;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.integrations.destination.redshift.RedshiftCopyDestination.RedshiftCopyDestinationConsumer;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("RedshiftDestination")
public class RedshiftDestinationTest {

  private static final ObjectMapper mapper = new ObjectMapper();

  @Test
  @DisplayName("When given S3 credentials should use COPY")
  public void useCopyStrategyTest() throws Exception {
    var copyMock = mock(RedshiftCopyDestination.class);
    when(copyMock.getConsumer(any(), any())).thenReturn(mock(RedshiftCopyDestinationConsumer.class));
    var insertMock = mock(RedshiftInsertDestination.class);
    var redshiftDest = new RedshiftDestination(copyMock, insertMock);

    var stubConfig = mapper.createObjectNode();
    stubConfig.put("s3_bucket_name", "fake-bucket");
    stubConfig.put("s3_bucket_region", "fake-region");
    stubConfig.put("access_key_id", "test");
    stubConfig.put("secret_access_key", "test key");
    var catalogMock = mock(ConfiguredAirbyteCatalog.class);

    redshiftDest.getConsumer(stubConfig, catalogMock);
    verify(copyMock, times(1)).getConsumer(any(), any());

  }

  @Test
  @DisplayName("When not given S3 credentials should use INSERT")
  public void useInsertStrategyTest() throws Exception {
    var copyMock = mock(RedshiftCopyDestination.class);
    var insertMock = mock(RedshiftInsertDestination.class);
    when(insertMock.getConsumer(any(), any())).thenReturn(mock(RedshiftCopyDestinationConsumer.class));
    var redshiftDest = new RedshiftDestination(copyMock, insertMock);

    var stubConfig = mapper.createObjectNode();
    var catalogMock = mock(ConfiguredAirbyteCatalog.class);

    redshiftDest.getConsumer(stubConfig, catalogMock);
    verify(insertMock, times(1)).getConsumer(any(), any());
  }

}
