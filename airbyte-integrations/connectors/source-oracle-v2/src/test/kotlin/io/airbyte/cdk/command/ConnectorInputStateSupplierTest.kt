package io.airbyte.cdk.command

import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST, "source"], rebuildContext = true)
class ConnectorInputStateSupplierTest {

    @Inject lateinit var supplier: ConnectorInputStateSupplier

    @Test
    fun testEmpty() {
        Assertions.assertEquals(listOf<AirbyteStateMessage>(), supplier.get())
    }

    @Test
    @Property(name = "airbyte.connector.state.json", value = VANILLA_STATES)
    fun testVanilla() {
        val states = listOf<AirbyteStateMessage>(
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(AirbyteStreamState()
                    .withStreamDescriptor(StreamDescriptor()
                        .withNamespace("foo")
                        .withName("bar"))
                    .withStreamState(Jsons.emptyObject()))
                .withSourceStats(AirbyteStateStats()
                    .withRecordCount(123.0)),
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(AirbyteStreamState()
                    .withStreamDescriptor(StreamDescriptor()
                        .withNamespace("foo")
                        .withName("baz"))
                    .withStreamState(Jsons.emptyObject()))
                .withSourceStats(AirbyteStateStats()
                    .withRecordCount(456.0)))
        Assertions.assertEquals(Jsons.deserialize(VANILLA_STATES), Jsons.jsonNode(states))
        Assertions.assertEquals(states, supplier.get())
    }

    @Test
    @Property(name = "airbyte.connector.state.json", value = STREAM_DUPLICATES)
    fun testStreamStatesDuplicates() {
        val dedupedState = AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(AirbyteStreamState()
                .withStreamDescriptor(StreamDescriptor()
                    .withNamespace("foo")
                    .withName("bar"))
                .withStreamState(Jsons.emptyObject()))
            .withSourceStats(AirbyteStateStats()
                .withRecordCount(456.0))
        Assertions.assertEquals(listOf(dedupedState), supplier.get())
    }

    @Test
    @Property(name = "airbyte.connector.state.json", value = STREAM_MIXED_DUPLICATES)
    fun testStreamStatesMixedDuplicates() {
        Assertions.assertEquals(1, supplier.get().size)
        Assertions.assertEquals(AirbyteStateMessage.AirbyteStateType.STREAM, supplier.get().first().type)
    }

    @Test
    @Property(name = "airbyte.connector.state.json", value = GLOBAL_DUPLICATES)
    fun testGlobalStatesDuplicates() {
        val dedupedState = AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
            .withGlobal(AirbyteGlobalState()
                .withSharedState(Jsons.emptyObject())
                .withStreamStates(listOf(
                    AirbyteStreamState()
                        .withStreamDescriptor(StreamDescriptor()
                            .withNamespace("foo")
                            .withName("quux"))
                        .withStreamState(Jsons.emptyObject()),
                    AirbyteStreamState()
                        .withStreamDescriptor(StreamDescriptor()
                            .withNamespace("foo")
                            .withName("test"))
                        .withStreamState(Jsons.emptyObject()))))
            .withSourceStats(AirbyteStateStats()
                .withRecordCount(789.0))
        Assertions.assertEquals(listOf(dedupedState), supplier.get())
    }

    @Test
    @Property(name = "airbyte.connector.state.json", value = GLOBAL_MIXED_DUPLICATES)
    fun testGlobalStatesMixedDuplicates() {
        Assertions.assertEquals(1, supplier.get().size)
        Assertions.assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, supplier.get().first().type)
    }
}

const val VANILLA_STATES = """
[
  {
    "type": "STREAM",
    "stream": {
      "stream_descriptor": {
        "name": "bar",
        "namespace": "foo"
      },
      "stream_state": {}
    },
    "sourceStats": {
      "recordCount": 123.0
    }
  },
  {
    "type": "STREAM",
    "stream": {
      "stream_descriptor": {
        "name": "baz",
        "namespace": "foo"
      },
      "stream_state": {}
    },
    "sourceStats": {
      "recordCount": 456.0
    }
  }
]
"""

const val STREAM_DUPLICATES = """
[
  {
    "type": "STREAM",
    "stream": {
      "stream_descriptor": {
        "name": "bar",
        "namespace": "foo"
      },
      "stream_state": {}
    },
    "sourceStats": {
      "recordCount": 123.0
    }
  },
  {
    "type": "STREAM",
    "stream": {
      "stream_descriptor": {
        "name": "bar",
        "namespace": "foo"
      },
      "stream_state": {}
    },
    "sourceStats": {
      "recordCount": 456.0
    }
  }
]
"""

const val GLOBAL_DUPLICATES = """
[
  {
    "type": "GLOBAL",
    "global": {
      "shared_state": {},
      "stream_states": [
        {
          "stream_descriptor": {
            "name": "bar",
            "namespace": "foo"
          },
          "stream_state": {}
        },
        {
          "stream_descriptor": {
            "name": "baz",
            "namespace": "foo"
          },
          "stream_state": {}
        }
      ]
    },
    "sourceStats": {
      "recordCount": 654.0
    }
  },
  {
    "type": "GLOBAL",
    "global": {
      "shared_state": {},
      "stream_states": [
        {
          "stream_descriptor": {
            "name": "quux",
            "namespace": "foo"
          },
          "stream_state": {}
        },
        {
          "stream_descriptor": {
            "name": "test",
            "namespace": "foo"
          },
          "stream_state": {}
        }
      ]
    },
    "sourceStats": {
      "recordCount": 789.0
    }
  }
]
"""


const val GLOBAL_MIXED_DUPLICATES = """
[
  {
    "type": "GLOBAL",
    "global": {
      "shared_state": {},
      "stream_states": [
        {
          "stream_descriptor": {
            "name": "bar",
            "namespace": "foo"
          },
          "stream_state": {}
        },
        {
          "stream_descriptor": {
            "name": "baz",
            "namespace": "foo"
          },
          "stream_state": {}
        }
      ]
    },
    "sourceStats": {
      "recordCount": 654.0
    }
  },
  {
    "type": "STREAM",
    "stream": {
      "stream_descriptor": {
        "name": "bar",
        "namespace": "foo"
      },
      "stream_state": {}
    },
    "sourceStats": {
      "recordCount": 123.0
    }
  }
]
"""

const val STREAM_MIXED_DUPLICATES = """
[
  {
    "type": "STREAM",
    "stream": {
      "stream_descriptor": {
        "name": "bar",
        "namespace": "foo"
      },
      "stream_state": {}
    },
    "sourceStats": {
      "recordCount": 123.0
    }
  },
  {
    "type": "GLOBAL",
    "global": {
      "shared_state": {},
      "stream_states": [
        {
          "stream_descriptor": {
            "name": "bar",
            "namespace": "foo"
          },
          "stream_state": {}
        },
        {
          "stream_descriptor": {
            "name": "baz",
            "namespace": "foo"
          },
          "stream_state": {}
        }
      ]
    },
    "sourceStats": {
      "recordCount": 654.0
    }
  }
]
"""
