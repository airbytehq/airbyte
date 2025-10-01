/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.lowcode

import io.airbyte.cdk.load.model.DeclarativeDestination
import io.airbyte.cdk.load.model.checker.Checker
import io.airbyte.cdk.load.model.checker.HttpRequestChecker
import io.airbyte.cdk.load.model.destination_import_mode.Insert as InsertModel
import io.airbyte.cdk.load.model.discover.CatalogOperation
import io.airbyte.cdk.load.model.discover.CompositeCatalogOperations
import io.airbyte.cdk.load.model.discover.StaticCatalogOperation
import io.airbyte.cdk.load.model.http.HttpMethod
import io.airbyte.cdk.load.model.http.HttpRequester
import io.airbyte.cdk.load.model.spec.Spec
import io.airbyte.cdk.util.Jsons

class ManifestBuilder {
    private var checker: Checker =
        HttpRequestChecker(
            HttpRequester(
                url = "https://any_url.com",
                method = HttpMethod.GET,
            )
        )
    private var spec: Spec =
        Spec(
            connectionSpecification = Jsons.objectNode(),
            advancedAuth = null,
        )
    private var discovery: CatalogOperation =
        CompositeCatalogOperations(
            operations =
                listOf<CatalogOperation>(
                    StaticCatalogOperation(
                        objectName = "test",
                        destinationImportMode = InsertModel,
                        schema = Jsons.objectNode()
                    ),
                )
        )

    fun withChecker(checker: Checker): ManifestBuilder {
        this.checker = checker
        return this
    }

    fun withSpec(spec: Spec): ManifestBuilder {
        this.spec = spec
        return this
    }

    fun withCatalogOperation(catalogOperation: CatalogOperation): ManifestBuilder {
        this.discovery = catalogOperation
        return this
    }

    fun build(): String {
        return Jsons.writeValueAsString(DeclarativeDestination(checker, spec, discovery))
    }
}
