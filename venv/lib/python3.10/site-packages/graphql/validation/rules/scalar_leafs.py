from typing import Any

from ...error import GraphQLError
from ...language import FieldNode
from ...type import get_named_type, is_leaf_type
from . import ValidationRule

__all__ = ["ScalarLeafsRule"]


class ScalarLeafsRule(ValidationRule):
    """Scalar leafs

    A GraphQL document is valid only if all leaf fields (fields without sub selections)
    are of scalar or enum types.
    """

    def enter_field(self, node: FieldNode, *_args: Any) -> None:
        type_ = self.context.get_type()
        if type_:
            selection_set = node.selection_set
            if is_leaf_type(get_named_type(type_)):
                if selection_set:
                    field_name = node.name.value
                    self.report_error(
                        GraphQLError(
                            f"Field '{field_name}' must not have a selection"
                            f" since type '{type_}' has no subfields.",
                            selection_set,
                        )
                    )
            elif not selection_set:
                field_name = node.name.value
                self.report_error(
                    GraphQLError(
                        f"Field '{field_name}' of type '{type_}'"
                        " must have a selection of subfields."
                        f" Did you mean '{field_name} {{ ... }}'?",
                        node,
                    )
                )
