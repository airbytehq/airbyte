package io.airbyte.integrations.source.jdbc.iblt;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "index",
    "count",
    "key_agg",
    "value_agg",
})
public class BFEntry {
  @JsonProperty("index")
  @JsonPropertyDescription("index")
  private int index;

  @JsonProperty("count")
  @JsonPropertyDescription("Count")
  private long count;

  @JsonProperty("key_agg")
  @JsonPropertyDescription("The Key aggregate")
  private String keyAgg;

  @JsonProperty("value_agg")
  @JsonPropertyDescription("The Value aggregate")
  private String valueAgg;
  //private final String hashKeyAgg;

  @JsonProperty("index")
  public int getIndexValue() {
    return this.index;
  }

  @JsonProperty("count")
  public void setIndexValue(final int index) {
    this.index = index;
  }

  public BFEntry withIndexValue(final int index) {
    this.index = index;
    return this;
  }

  @JsonProperty("count")
  public long getCountValue() {
    return this.count;
  }

  @JsonProperty("count")
  public void setCountValue(final long count) {
    this.count = count;
  }

  public BFEntry withCountValue(final long count) {
    this.count = count;
    return this;
  }

  @JsonProperty("key_agg")
  public String getKeyAggValue() {
    return this.valueAgg;
  }

  @JsonProperty("value_agg")
  public void setKeyAggValue(final String keyAgg) {
    this.keyAgg = keyAgg;
  }

  public BFEntry withKeyAggValue(final String keyAgg) {
    this.keyAgg = keyAgg;
    return this;
  }


  @JsonProperty("value_agg")
  public String getValueAggValue() {
    return this.valueAgg;
  }

  @JsonProperty("value_agg")
  public void setValueAggValue(final String valueAgg) {
    this.valueAgg = valueAgg;
  }

  public BFEntry withValueAggValue(final String valueAgg) {
    this.valueAgg = valueAgg;
    return this;
  }

  public void insert(final String key, final String val) {
    if (count == 0) {
      keyAgg = key;
      valueAgg = val;
    } else {
      keyAgg = StringXORer.xorString(keyAgg, key);
      valueAgg = StringXORer.xorString(valueAgg, val);
    }
    count++;
  }

  public void delete(final String key, final String val) {
    keyAgg = StringXORer.xorString(keyAgg, key);
    valueAgg = StringXORer.xorString(valueAgg, val);
    count--;
  }

  public boolean isPure() {
    if ((count == -1 || count == 1))
      return true;
    return false;
  }
}
