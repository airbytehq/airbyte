/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio

import io.airbyte.cdk.load.command.DestinationDiscoverCatalog
import io.airbyte.cdk.load.discover.DestinationDiscoverer
import io.airbyte.cdk.load.discoverer.operation.OperationProvider

class CustomerIoDiscoverer(private val operationProvider: OperationProvider) :
    DestinationDiscoverer<CustomerIoConfiguration> {
    override fun discover(config: CustomerIoConfiguration): DestinationDiscoverCatalog {
        return DestinationDiscoverCatalog(operationProvider.get())
        //        return DestinationDiscoverCatalog(
        //            listOf(
        //                DestinationOperation(
        //                    "person_identify",
        //                    Dedupe(emptyList(), emptyList()),
        //                    ObjectType(
        //                        properties =
        //                            linkedMapOf(
        //                                "person_email" to FieldType(StringType, false),
        //                            ),
        //                        additionalProperties = true,
        //                        required = listOf("person_email"),
        //                    ),
        //                    matchingKeys = emptyList<List<String>>()
        //                ),
        //                DestinationOperation(
        //                    "person_event",
        //                    Append,
        //                    ObjectType(
        //                        properties =
        //                            linkedMapOf(
        //                                "person_email" to FieldType(StringType, false),
        //                                "event_name" to FieldType(StringType, false),
        //                                "event_id" to FieldType(StringType, false),
        //                                "timestamp" to FieldType(IntegerType, false),
        //                            ),
        //                        additionalProperties = true,
        //                        required = listOf("person_email", "event_name"),
        //                    ),
        //                    matchingKeys = emptyList<List<String>>()
        //                )
        //            )
        //        )
    }
}
