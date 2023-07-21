/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.Collection;
import java.util.Optional;

/**
 * TODO these are not in the right place, they probably belongs in a base library but to avoid
 * having to publish a bunch of connectors I'm putting it here temporarily
 *
 */
public class CollectionUtils {

  /**
   * Pass in a collection and search term to determine whether any of the values match ignoring case
   *
   * @param collection the collection of values
   * @param search the value to look for
   * @return whether the value matches anything in the collection
   */
  public static boolean containsIgnoreCase(final Collection<String> collection, final String search) {
    return matchingKey(collection, search).isPresent();
  }

  /**
   * Convenience method for when you need to check an entire collection for membership in another
   * collection.
   *
   * @param searchCollection the collection you want to check membership in
   * @param searchTerms the keys you're looking for
   * @return whether all searchTerms are in the searchCollection
   */
  public static boolean containsAllIgnoreCase(final Collection<String> searchCollection, final Collection<String> searchTerms) {
    return searchTerms.stream().allMatch(term -> containsIgnoreCase(searchCollection, term));
  }

  /**
   * From a collection of strings, return an entry which matches the search term ignoring case
   *
   * @param collection the collection to search
   * @param search the key you're looking for
   * @return an Optional value which might contain the key that matches the search
   */
  public static Optional<String> matchingKey(final Collection<String> collection, final String search) {
    if (collection.contains(search)) {
      return Optional.of(search);
    }
    return collection.stream().filter(s -> s.equalsIgnoreCase(search)).findFirst();
  }

}
