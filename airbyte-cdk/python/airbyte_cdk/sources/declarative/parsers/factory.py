#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import copy
import enum
import importlib
from typing import Any, List, Literal, Mapping, Type, Union, get_args, get_origin, get_type_hints

from airbyte_cdk.sources.declarative.create_partial import OPTIONS_STR, create
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.parsers.class_types_registry import CLASS_TYPES_REGISTRY
from airbyte_cdk.sources.declarative.parsers.default_implementation_registry import DEFAULT_IMPLEMENTATIONS_REGISTRY
from airbyte_cdk.sources.declarative.types import Config

ComponentDefinition: Union[Literal, Mapping, List]


class DeclarativeComponentFactory:
    """
    Instantiates objects from a Mapping[str, Any] defining the object to create.

    If the component is a literal, then it is returned as is:
    ```
    3
    ```
    will result in
    ```
    3
    ```

    If the component is a mapping with a "class_name" field,
    an object of type "class_name" will be instantiated by passing the mapping's other fields to the constructor
    ```
    {
      "class_name": "fully_qualified.class_name",
      "a_parameter: 3,
      "another_parameter: "hello"
    }
    ```
    will result in
    ```
    fully_qualified.class_name(a_parameter=3, another_parameter="helo"
    ```

    If the component definition is a mapping with a "type" field,
    the factory will lookup the `CLASS_TYPES_REGISTRY` and replace the "type" field by "class_name" -> CLASS_TYPES_REGISTRY[type]
    and instantiate the object from the resulting mapping

    If the component definition is a mapping with neither a "class_name" nor a "type" field,
    the factory will do a best-effort attempt at inferring the component type by looking up the parent object's constructor type hints.
    If the type hint is an interface present in `DEFAULT_IMPLEMENTATIONS_REGISTRY`,
    then the factory will create an object of it's default implementation.

    If the component definition is a list, then the factory will iterate over the elements of the list,
    instantiate its subcomponents, and return a list of instantiated objects.

    If the component has subcomponents, the factory will create the subcomponents before instantiating the top level object
    ```
    {
      "type": TopLevel
      "param":
        {
          "type": "ParamType"
          "k": "v"
        }
    }
    ```
    will result in
    ```
    TopLevel(param=ParamType(k="v"))
    ```

    Parameters can be passed down from a parent component to its subcomponents using the $options key.
    This can be used to avoid repetitions.
    ```
    outer:
      $options:
        MyKey: MyValue
      inner:
       k2: v2
    ```
    This the example above, if both outer and inner are types with a "MyKey" field, both of them will evaluate to "MyValue".

    The value can also be used for string interpolation:
    ```
    outer:
      $options:
        MyKey: MyValue
      inner:
       k2: "MyKey is {{ options.MyKey }}"
    ```
    In this example, outer.inner.k2 will evaluate to "MyValue"

    """

    def __init__(self):
        self._interpolator = JinjaInterpolation()

    def create_component(self, component_definition: ComponentDefinition, config: Config):
        """
        Create a component defined by `component_definition`.

        This method will also traverse and instantiate its subcomponents if needed.
        :param component_definition: The definition of the object to create.
        :param config: Connector's config
        :return: The object to create
        """
        kwargs = copy.deepcopy(component_definition)
        if "class_name" in kwargs:
            class_name = kwargs.pop("class_name")
        elif "type" in kwargs:
            class_name = CLASS_TYPES_REGISTRY[kwargs.pop("type")]
        else:
            raise ValueError(f"Failed to create component because it has no class_name or type. Definition: {component_definition}")
        return self.build(class_name, config, **kwargs)

    def build(self, class_or_class_name: Union[str, Type], config, **kwargs):
        if isinstance(class_or_class_name, str):
            class_ = self._get_class_from_fully_qualified_class_name(class_or_class_name)
        else:
            class_ = class_or_class_name

        # create components in options before propagating them
        if OPTIONS_STR in kwargs:
            kwargs[OPTIONS_STR] = {k: self._create_subcomponent(k, v, kwargs, config, class_) for k, v in kwargs[OPTIONS_STR].items()}

        updated_kwargs = {k: self._create_subcomponent(k, v, kwargs, config, class_) for k, v in kwargs.items()}
        return create(class_, config=config, **updated_kwargs)

    @staticmethod
    def _get_class_from_fully_qualified_class_name(class_name: str):
        split = class_name.split(".")
        module = ".".join(split[:-1])
        class_name = split[-1]
        return getattr(importlib.import_module(module), class_name)

    @staticmethod
    def _merge_dicts(d1, d2):
        return {**d1, **d2}

    def _create_subcomponent(self, key, definition, kwargs, config, parent_class):
        """
        There are 5 ways to define a component.
        1. dict with "class_name" field -> create an object of type "class_name"
        2. dict with "type" field -> lookup the `CLASS_TYPES_REGISTRY` to find the type of object and create an object of that type
        3. a dict with a type that can be inferred. If the parent class's constructor has type hints, we can infer the type of the object to create by looking up the `DEFAULT_IMPLEMENTATIONS_REGISTRY` map
        4. list: loop over the list and create objects for its items
        5. anything else -> return as is
        """
        if self.is_object_definition_with_class_name(definition):
            # propagate kwargs to inner objects
            definition[OPTIONS_STR] = self._merge_dicts(kwargs.get(OPTIONS_STR, dict()), definition.get(OPTIONS_STR, dict()))
            return self.create_component(definition, config)()
        elif self.is_object_definition_with_type(definition):
            # If type is set instead of class_name, get the class_name from the CLASS_TYPES_REGISTRY
            definition[OPTIONS_STR] = self._merge_dicts(kwargs.get(OPTIONS_STR, dict()), definition.get(OPTIONS_STR, dict()))
            object_type = definition.pop("type")
            class_name = CLASS_TYPES_REGISTRY[object_type]
            definition["class_name"] = class_name
            return self.create_component(definition, config)()
        elif isinstance(definition, dict):
            # Try to infer object type
            expected_type = self.get_default_type(key, parent_class)
            # if there is an expected type, and it's not a builtin type, then instantiate it
            # We don't have to instantiate builtin types (eg string and dict) because definition is already going to be of that type
            if expected_type and not self._is_builtin_type(expected_type):
                definition["class_name"] = expected_type
                definition[OPTIONS_STR] = self._merge_dicts(kwargs.get(OPTIONS_STR, dict()), definition.get(OPTIONS_STR, dict()))
                return self.create_component(definition, config)()
            else:
                return definition
        elif isinstance(definition, list):
            return [
                self._create_subcomponent(
                    key, sub, self._merge_dicts(kwargs.get(OPTIONS_STR, dict()), self._get_subcomponent_options(sub)), config, parent_class
                )
                for sub in definition
            ]
        else:
            expected_type = self.get_default_type(key, parent_class)
            if expected_type and not isinstance(definition, expected_type):
                # call __init__(definition) if definition is not a dict and is not of the expected type
                # for instance, to turn a string into an InterpolatedString
                options = kwargs.get(OPTIONS_STR, {})
                try:
                    # enums can't accept options
                    if issubclass(expected_type, enum.Enum):
                        return expected_type(definition)
                    else:
                        return expected_type(definition, options=options)
                except Exception as e:
                    raise Exception(f"failed to instantiate type {expected_type}. {e}")
            else:
                return definition

    @staticmethod
    def is_object_definition_with_class_name(definition):
        return isinstance(definition, dict) and "class_name" in definition

    @staticmethod
    def is_object_definition_with_type(definition):
        return isinstance(definition, dict) and "type" in definition

    @staticmethod
    def get_default_type(parameter_name, parent_class):
        type_hints = get_type_hints(parent_class.__init__)
        interface = type_hints.get(parameter_name)
        while True:
            origin = get_origin(interface)
            if origin:
                # Unnest types until we reach the raw type
                # List[T] -> T
                # Optional[List[T]] -> T
                args = get_args(interface)
                interface = args[0]
            else:
                break

        expected_type = DEFAULT_IMPLEMENTATIONS_REGISTRY.get(interface)

        if expected_type:
            return expected_type
        else:
            return interface

    @staticmethod
    def _get_subcomponent_options(sub: Any):
        if isinstance(sub, dict):
            return sub.get(OPTIONS_STR, {})
        else:
            return {}

    @staticmethod
    def _is_builtin_type(cls) -> bool:
        if not cls:
            return False
        return cls.__module__ == "builtins"
