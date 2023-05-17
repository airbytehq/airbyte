package io.airbyte.integrations.source.jdbc.iblt;

import java.io.Serializable;
import java.nio.charset.Charset;
import java.util.Arrays;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class InvertibleBloomFilter implements Serializable {
  private static final Logger LOGGER = LoggerFactory.getLogger(InvertibleBloomFilter.class);
  private final int numHashes = 3; // number of hash functions
  private final int ibfSize = 1000; //the size of IBF is d*1.5(d,size of the set difference) that are required to successfully decode the IBF
  private final BFEntry[] BFEntrys;

  private final Function<byte[], Integer>[] hashFunctions;

  public BFEntry[] getBFEntrys() {
    final BFEntry[] filteredEntries = Arrays.stream(BFEntrys)
        .sequential()
        .filter(bfEntry -> bfEntry.getCountValue() > 0 )
        .toArray(BFEntry[]::new);
    LOGGER.info("Getting bf entries of size {} " + filteredEntries.length);
    return filteredEntries;
  }

  static final Charset charset = Charset.forName("UTF-8");

  public InvertibleBloomFilter() {
    this.BFEntrys = new BFEntry[ibfSize]; // how to create a array of the inner class when the BFEntry is a inner class ?
    for(int i=0; i<BFEntrys.length; i++) {
      BFEntrys[i] = new BFEntry().withIndexValue(i);
    }

    this.hashFunctions = new Function[numHashes];
    for (int i = 0; i < numHashes; i++) {
      hashFunctions[i] = createHashFunction(i);
    }
  }

  // Constructs a bloom filter out of existing state
  public void addEntries(final BFEntry[] entryList) {
    LOGGER.info("adding entries from previous run. Size of entry list: " + entryList.length);
    for (final BFEntry oldEntry : entryList) {
      final int index = oldEntry.getIndexValue();
      final BFEntry newEntry = BFEntrys[index];
      newEntry.setCountValue(oldEntry.getCountValue());
      newEntry.setKeyAggValue(oldEntry.getKeyAggValue());
      newEntry.setValueAggValue(oldEntry.getValueAggValue());
    }
  }

  public void insert(final String key, final String value) {
    LOGGER.info("Inserting into the bloom filter. Key, value : {}, {}", key, value);
    final byte[] keyVal = key.getBytes(charset);
    final int[] hashes = genHashes(keyVal);
    for (final int hash : hashes) {
      final int idx = Math.abs(hash % ibfSize);
      BFEntrys[idx].insert(key, value);
    }
  }

  // Currently, not used. ListEntries also is not used.
  public void delete(final String key, final String value) {
    final byte[] keyVal = key.getBytes(charset);
    final int[] hashes = genHashes(keyVal);
    for (final int hash : hashes) {
      final int idx = Math.abs(hash % ibfSize);
      BFEntrys[idx].delete(key, value);
    }
  }

  public String getValue(final String key) {
    LOGGER.info("Getting key from the bloom filter {}", key);
    final byte[] keyVal = key.getBytes(charset);
    final int[] hashes = genHashes(keyVal);
    for (final int hash : hashes) {
      final BFEntry BFEntry = BFEntrys[Math.abs(hash % ibfSize)];
      if (BFEntry.isPure()) {
        return BFEntry.getValueAggValue();
      }
    }
    return null;
  }

  // Returns true if we can determine the value, otherwise returns false.
  public boolean contains(final String key) {
    LOGGER.info("Checking if key exists in bloom filter: {}", key);
    final byte[] keyVal = key.getBytes(charset);
    final int[] hashes = genHashes(keyVal);
    for (final int hash : hashes) {
      final BFEntry BFEntry = BFEntrys[Math.abs(hash % ibfSize)];
      if (BFEntry == null || BFEntry.getCountValue() == 0) {
        return false;
      } else if (BFEntry.isPure()) {
        return true;
      }
    }
    return false;
  }

  private Function<byte[], Integer> createHashFunction(final int seed) {
    return element -> {
      int hash = 17;
      hash = 31 * hash + element.hashCode();
      hash = 31 * hash + seed;
      return hash;
    };
  }

  public int[] genHashes(final byte[] data) {
    final int[] result = new int[numHashes];
    for (int i = 0; i < numHashes; i++) {
      result[i] = hashFunctions[i].apply(data);
    }
    return result;
  }
}