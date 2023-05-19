/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.xmin;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
  "num_wraparound",
  "xmin_xid_value",
  "xmin_raw_value",
})
public class XminStatus {

  // The number of wraparounds the source DB has undergone. (These are the epoch bits in the xmin
  // snapshot).
  @JsonProperty("num_wraparound")
  @JsonPropertyDescription("Number of times the xmin has wrapped around")
  private long numWraparound;
  // The 32-bit xmin value associated with the xmin snapshot. This is the value that is ultimately
  // written and recorded on every row.
  @JsonProperty("xmin_xid_value")
  @JsonPropertyDescription("The XID value associated with the xmin")
  private long xminXidValue;
  // The raw value of the xmin snapshot (which is a combination of 1 and 2). If no wraparound has
  // occurred, this should be the same as 2.
  @JsonProperty("xmin_raw_value")
  @JsonPropertyDescription("The XID value associated with the xmin")
  private long xminRawValue;

  @JsonProperty("num_wraparound")
  public long getNumWraparound() {
    return this.numWraparound;
  }

  @JsonProperty("num_wraparound")
  public void setNumWraparound(final long numWraparound) {
    this.numWraparound = numWraparound;
  }

  public XminStatus withNumWraparound(final long numWraparound) {
    this.numWraparound = numWraparound;
    return this;
  }

  @JsonProperty("xmin_xid_value")
  public long getXminXidValue() {
    return this.xminXidValue;
  }

  @JsonProperty("xmin_xid_value")
  public void setXminXidValue(final long xminXidValue) {
    this.xminXidValue = xminXidValue;
  }

  public XminStatus withXminXidValue(final long xminXidValue) {
    this.xminXidValue = xminXidValue;
    return this;
  }

  @JsonProperty("xmin_raw_value")
  public long getXminRawValue() {
    return this.xminRawValue;
  }

  @JsonProperty("xmin_raw_value")
  public void setXminRawValue(final long xminRawValue) {
    this.xminRawValue = xminRawValue;
  }

  public XminStatus withXminRawValue(final long xminRawValue) {
    this.xminRawValue = xminRawValue;
    return this;
  }

}
