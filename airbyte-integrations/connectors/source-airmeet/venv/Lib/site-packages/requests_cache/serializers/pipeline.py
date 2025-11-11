"""Classes for building complex serializers from a sequence of stages.

.. automodsumm:: requests_cache.serializers.pipeline
   :classes-only:
   :nosignatures:
"""

from typing import Any, Callable, Optional, Sequence, Union

from ..models import CachedResponse


class Stage:
    """A single stage in a serializer pipeline. This wraps serialization steps with consistent
    ``dumps()`` and ``loads()`` methods

    Args:
        obj: Serializer object or module, if applicable
        dumps: Serialization function, or name of method on ``obj``
        loads: Deserialization function, or name of method on ``obj``
    """

    def __init__(
        self,
        obj: Any = None,
        dumps: Union[str, Callable] = 'dumps',
        loads: Union[str, Callable] = 'loads',
    ):
        self.obj = obj
        self.dumps = getattr(obj, dumps) if isinstance(dumps, str) else dumps
        self.loads = getattr(obj, loads) if isinstance(loads, str) else loads


class SerializerPipeline:
    """A pipeline of stages chained together to serialize and deserialize response objects.

    Note: Typically, the first stage should be a :py:class:`.CattrStage`, since this does the
    majority of the non-format-specific work to unstructure a response object into a dict (and
    vice versa).

    Args:
        stages: A sequence of :py:class:`Stage` objects, or any objects with ``dumps()`` and
            ``loads()`` methods
        is_binary: Indicates whether the serialized content is binary
    """

    def __init__(self, stages: Sequence, name: Optional[str] = None, is_binary: bool = False):
        self.is_binary = is_binary
        self.stages = stages
        self.dump_stages = [stage.dumps for stage in stages]
        self.load_stages = [stage.loads for stage in reversed(stages)]
        self.name = name

    def dumps(self, value) -> Union[str, bytes]:
        for step in self.dump_stages:
            value = step(value)
        return value

    def loads(self, value) -> CachedResponse:
        for step in self.load_stages:
            value = step(value)
        return value

    def set_decode_content(self, decode_content: bool):
        """Set decode_content, if the pipeline contains a CattrStage or compatible object"""
        for stage in self.stages:
            if hasattr(stage, 'decode_content'):
                stage.decode_content = decode_content

    def __str__(self) -> str:
        return f'SerializerPipeline(name={self.name}, n_stages={len(self.dump_stages)})'
