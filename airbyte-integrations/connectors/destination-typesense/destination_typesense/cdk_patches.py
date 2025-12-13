# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""
Monkey-patch for airbyte-cdk to preserve additional properties in AirbyteStateMessage.

This fixes the "State message does not contain id" error that occurs with Airbyte 1.7+.
The platform attaches an 'id' field to state messages, but the Python CDK's dataclass
doesn't preserve it. This patch adds the same dynamic attribute handling used for
AirbyteStateBlob to AirbyteStateMessage.
"""

from dataclasses import InitVar, dataclass
from typing import Annotated, Any, Dict, Mapping, Optional

from serpyco_rs import CustomType, Serializer
from serpyco_rs.metadata import Alias


def apply_patches():
    """Apply monkey-patches to airbyte_cdk to preserve state message additional properties."""
    import airbyte_cdk.models.airbyte_protocol as protocol_module
    import airbyte_cdk.models.airbyte_protocol_serializers as serializers_module

    # Get references to existing classes we need
    AirbyteStateType = protocol_module.AirbyteStateType
    AirbyteStreamState = protocol_module.AirbyteStreamState
    AirbyteGlobalState = protocol_module.AirbyteGlobalState
    AirbyteStateStats = protocol_module.AirbyteStateStats
    AirbyteStateBlob = protocol_module.AirbyteStateBlob
    # IMPORTANT: Save reference to original AirbyteStateMessage BEFORE we replace it
    # This is needed because AirbyteMessage's type annotation still refers to this class
    OriginalAirbyteStateMessage = protocol_module.AirbyteStateMessage

    # Define patched AirbyteStateMessage that preserves additional properties
    @dataclass
    class PatchedAirbyteStateMessage:
        """
        State message that preserves additional properties (like 'id' from platform).
        Uses same pattern as AirbyteStateBlob for extra field preservation.
        """

        kwargs: InitVar[Mapping[str, Any]]

        type: Optional[AirbyteStateType] = None
        stream: Optional[AirbyteStreamState] = None
        global_: Annotated[AirbyteGlobalState | None, Alias("global")] = None
        data: Optional[Dict[str, Any]] = None
        sourceStats: Optional[AirbyteStateStats] = None
        destinationStats: Optional[AirbyteStateStats] = None

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            # Known fields that should be set as attributes
            self.type = kwargs.pop("type", None)
            self.stream = kwargs.pop("stream", None)
            self.global_ = kwargs.pop("global_", None) or kwargs.pop("global", None)
            self.data = kwargs.pop("data", None)
            self.sourceStats = kwargs.pop("sourceStats", None)
            self.destinationStats = kwargs.pop("destinationStats", None)
            # Store any additional properties (like 'id' from platform)
            self._additional_properties = kwargs

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, PatchedAirbyteStateMessage):
                return False
            return (
                self.type == other.type
                and self.stream == other.stream
                and self.global_ == other.global_
                and self.data == other.data
                and self.sourceStats == other.sourceStats
                and self.destinationStats == other.destinationStats
                and getattr(self, "_additional_properties", {}) == getattr(other, "_additional_properties", {})
            )

    # Replace in protocol module
    protocol_module.AirbyteStateMessage = PatchedAirbyteStateMessage

    # Also need to update the AirbyteMessage class's state field type hint
    # The dataclass is already defined, but we patch the class reference
    original_airbyte_message = protocol_module.AirbyteMessage

    # Create serializers with the patched class
    AirbyteStreamStateSerializer = Serializer(
        AirbyteStreamState, omit_none=True, custom_type_resolver=serializers_module.custom_type_resolver
    )
    AirbyteGlobalStateSerializer = Serializer(
        AirbyteGlobalState, omit_none=True, custom_type_resolver=serializers_module.custom_type_resolver
    )

    # Define custom serializer for patched AirbyteStateMessage
    class PatchedAirbyteStateMessageType(CustomType[PatchedAirbyteStateMessage, Dict[str, Any]]):
        """Custom serializer for AirbyteStateMessage that preserves additional properties like 'id'."""

        def serialize(self, value: PatchedAirbyteStateMessage) -> Dict[str, Any]:
            result: Dict[str, Any] = {}
            if value.type is not None:
                result["type"] = value.type.value if hasattr(value.type, "value") else value.type
            if value.stream is not None:
                result["stream"] = AirbyteStreamStateSerializer.dump(value.stream)
            if value.global_ is not None:
                result["global"] = AirbyteGlobalStateSerializer.dump(value.global_)
            if value.data is not None:
                result["data"] = value.data
            if value.sourceStats is not None:
                result["sourceStats"] = value.sourceStats.__dict__ if hasattr(value.sourceStats, "__dict__") else value.sourceStats
            if value.destinationStats is not None:
                result["destinationStats"] = (
                    value.destinationStats.__dict__ if hasattr(value.destinationStats, "__dict__") else value.destinationStats
                )
            # Include additional properties (like 'id' from platform)
            if hasattr(value, "_additional_properties"):
                result.update(value._additional_properties)
            return result

        def deserialize(self, value: Dict[str, Any]) -> PatchedAirbyteStateMessage:
            # Need to properly deserialize nested objects
            deserialized = dict(value)  # Copy to avoid mutating input
            if "stream" in deserialized and isinstance(deserialized["stream"], dict):
                deserialized["stream"] = AirbyteStreamStateSerializer.load(deserialized["stream"])
            if "global" in deserialized and isinstance(deserialized["global"], dict):
                deserialized["global_"] = AirbyteGlobalStateSerializer.load(deserialized.pop("global"))
            if "global_" in deserialized and isinstance(deserialized["global_"], dict):
                deserialized["global_"] = AirbyteGlobalStateSerializer.load(deserialized["global_"])
            # Convert type string to enum if needed
            if "type" in deserialized and isinstance(deserialized["type"], str):
                deserialized["type"] = AirbyteStateType(deserialized["type"])
            return PatchedAirbyteStateMessage(**deserialized)

        def get_json_schema(self) -> Dict[str, Any]:
            return {"type": "object", "additionalProperties": True}

    # Store original resolver
    original_resolver = serializers_module.custom_type_resolver

    # Create patched resolver that handles both AirbyteStateBlob and AirbyteStateMessage
    # IMPORTANT: Must check for BOTH original and patched AirbyteStateMessage because:
    # - AirbyteMessage's type annotation refers to OriginalAirbyteStateMessage
    # - New code might create PatchedAirbyteStateMessage instances
    def patched_custom_type_resolver(t: type) -> CustomType | None:
        if t is AirbyteStateBlob:
            return serializers_module.AirbyteStateBlobType()
        if t is PatchedAirbyteStateMessage or t is OriginalAirbyteStateMessage:
            return PatchedAirbyteStateMessageType()
        return None

    # Replace the resolver
    serializers_module.custom_type_resolver = patched_custom_type_resolver

    # Recreate serializers with patched resolver
    serializers_module.AirbyteStateMessageSerializer = Serializer(
        PatchedAirbyteStateMessage, omit_none=True, custom_type_resolver=patched_custom_type_resolver
    )
    serializers_module.AirbyteMessageSerializer = Serializer(
        original_airbyte_message, omit_none=True, custom_type_resolver=patched_custom_type_resolver
    )

    # Also update the imports in serializers_module
    serializers_module.AirbyteStateMessage = PatchedAirbyteStateMessage

    # CRITICAL: Also patch modules that have already imported AirbyteMessageSerializer
    # These modules imported the serializer at module load time, so they have stale references
    try:
        import airbyte_cdk.destinations.destination as dest_module

        dest_module.AirbyteMessageSerializer = serializers_module.AirbyteMessageSerializer
    except ImportError:
        pass

    try:
        import airbyte_cdk.entrypoint as entrypoint_module

        entrypoint_module.AirbyteMessageSerializer = serializers_module.AirbyteMessageSerializer
    except ImportError:
        pass

    try:
        import airbyte_cdk.models as models_module

        models_module.AirbyteMessageSerializer = serializers_module.AirbyteMessageSerializer
        models_module.AirbyteStateMessageSerializer = serializers_module.AirbyteStateMessageSerializer
    except ImportError:
        pass

    print("[cdk_patches] Applied AirbyteStateMessage patch for state-id preservation")


# Apply patches when this module is imported
apply_patches()
