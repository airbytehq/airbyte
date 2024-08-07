/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import java.util.*

/**
 * TODO these are not in the right place, they probably belongs in a base library but to avoid
 * having to publish a bunch of connectors I'm putting it here temporarily
 */
object CollectionUtils {
    /**
     * Pass in a collection and search term to determine whether any of the values match ignoring
     * case
     *
     * @param collection the collection of values
     * @param search the value to look for
     * @return whether the value matches anything in the collection
     */
    @JvmStatic
    fun containsIgnoreCase(collection: Collection<String>, search: String): Boolean {
        return matchingKey(collection, search).isPresent
    }

    /**
     * Convenience method for when you need to check an entire collection for membership in another
     * collection.
     *
     * @param searchCollection the collection you want to check membership in
     * @param searchTerms the keys you're looking for
     * @return whether all searchTerms are in the searchCollection
     */
    @JvmStatic
    fun containsAllIgnoreCase(
        searchCollection: Collection<String>,
        searchTerms: Collection<String>
    ): Boolean {
        require(!searchTerms.isEmpty()) {
            // There isn't a good behavior for an empty collection. Without this check, an empty
            // collection
            // would always return
            // true, but it feels misleading to say that the searchCollection does "contain all"
            // when
            // searchTerms is empty
            "Search Terms collection may not be empty"
        }
        return searchTerms.all { term: String -> containsIgnoreCase(searchCollection, term) }
    }

    /**
     * From a collection of strings, return an entry which matches the search term ignoring case
     *
     * @param collection the collection to search
     * @param search the key you're looking for
     * @return an Optional value which might contain the key that matches the search
     */
    @JvmStatic
    fun matchingKey(collection: Collection<String>, search: String): Optional<String> {
        if (collection.contains(search)) {
            return Optional.of(search)
        }
        return Optional.ofNullable(collection.firstOrNull { it.equals(search, ignoreCase = true) })
    }
}
