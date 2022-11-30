package io.airbyte.integrations.standardtest.source;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;
import javax.annotation.Nullable;

public class TestDataUtils {

  public static List<String> getInsertTestDataAsOneTable(List<TestDataHolder> dataHolders, @Nullable List<String> filterNames, boolean noNullValues) {
    var filteredDataHolders = filterDataHolders(dataHolders, filterNames);

    var randomHolder = filteredDataHolders.stream().findFirst().get();
    var insertPatternSql = randomHolder.insertPatternSql;
    var nameSpace = randomHolder.nameSpace;

    Map<Integer, String> insertValues = initAllRecords(filteredDataHolders);
    filteredDataHolders.stream().sorted(Comparator.comparing(o -> o.testColumnName)).forEach(testDataHolder -> addValues(insertValues, testDataHolder.values, noNullValues));

    return insertValues.entrySet().stream().map(entry -> String.format(insertPatternSql, (nameSpace != null ? nameSpace + "." : "") + randomHolder.getNameWithTestPrefix(), entry.getKey(), entry.getValue())).toList();
  }

  private static Map<Integer, String> initAllRecords(List<TestDataHolder> dataHolders) {
    var max = dataHolders.stream().map(testDataHolder -> testDataHolder.values.size()).max(Comparator.comparingInt(value -> value));
    Map<Integer, String> records = new HashMap<>();
    for (int i = 1; i <= max.orElse(0); i++) {
      records.put(i, "");
    }
    return records;
  }

  private static void addValues(Map<Integer, String> insertValues, List<String> values, boolean noNullValues) {
    var valueIterator = values.iterator();
    AtomicReference<String> newValue = new AtomicReference<>(null);
    AtomicReference<String> previousValue = new AtomicReference<>(null);

    insertValues.entrySet().stream().sorted(Comparator.comparingInt(Entry::getKey)).forEachOrdered(entry -> {
      var existingValue = insertValues.get(entry.getKey());
      var isEmpty = existingValue.isEmpty();

      newValue.set(getValue(valueIterator, previousValue.get(), noNullValues));
      insertValues.put(entry.getKey(), existingValue + (!isEmpty ? ", " : "") + newValue.get());
      previousValue.set(newValue.get());
    });
  }

  private static String getValue(Iterator<String> iterator, String previousValue, boolean noNullValues) {
    String value;
    while (iterator.hasNext()) {
      value = iterator.next();
      if (noNullValues) {
        if (value != null && !value.equals("null")) {
          return value;
        }
      } else {
        return value;
      }
    }

    // If you are here, there is no acceptable value in the iterator left.
    if (noNullValues) {
      if (previousValue != null && !previousValue.equals("null")) {
        return previousValue;
      } else {
        throw new RuntimeException("Not null value is not found!");
      }
    } else {
      return "null";
    }
  }

  public static String getCreateTestDataAsOneTable(List<TestDataHolder> dataHolders, @Nullable List<String> filterNames) {
    var filteredDataHolders = filterDataHolders(dataHolders, filterNames);

    var randomHolder = filteredDataHolders.stream().findFirst().get();
    var createSql = randomHolder.createTablePatternSql;
    var nameSpace = randomHolder.nameSpace;
    var nameWithTestPrefix = randomHolder.getNameWithTestPrefix();
    var idColumnName = randomHolder.idColumnName;

    return String.format(createSql, (nameSpace != null ? nameSpace + "." : "") + nameWithTestPrefix, idColumnName, getAllColumns(filteredDataHolders),
        "");
  }

  private static List<TestDataHolder> filterDataHolders(List<TestDataHolder> dataHolders, List<String> filterNames) {
    var filtered = dataHolders.stream().filter(testDataHolder -> filterNames == null || filterNames.contains(testDataHolder.testColumnName)).toList();
    if (filtered.size() == 0) {
      throw new RuntimeException("At least one column should be left after filtering!");
    } else {
      return filtered;
    }
  }

  public static void makeColumnNameUnique(List<TestDataHolder> dataHolders) {
    List<TestDataHolder> newDataHolders = new ArrayList<>();
    dataHolders.forEach(testDataHolder -> {
      testDataHolder.setTestColumnName(testDataHolder.testColumnName + "_" + (newDataHolders.size()+1));
      newDataHolders.add(testDataHolder);
    });
  }

  private static String getAllColumns(List<TestDataHolder> dataHolders) {
    return dataHolders.stream().sorted(Comparator.comparing(o -> o.testColumnName)).map(testDataHolder -> testDataHolder.testColumnName + " " + testDataHolder.fullSourceDataType).collect(Collectors.joining(","));
  }
}
