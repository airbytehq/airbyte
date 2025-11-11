import sys

if sys.version_info <= (3, 13):

    def subclasses(cls: type) -> list[type]:
        """A proxy for `cls.__subclasses__()` on older Pythons."""
        return cls.__subclasses__()

else:

    def subclasses(cls: type) -> list[type]:
        """A helper for getting subclasses of a class.

        Filters out duplicate subclasses of slot dataclasses and attrs classes.
        """
        return [
            cl
            for cl in cls.__subclasses__()
            if (
                not (
                    "__slots__" not in cl.__dict__
                    and hasattr(cls, "__dataclass_params__")
                    and cls.__dataclass_params__.slots
                )
                and not hasattr(cls, "__attrs_base_of_slotted__")
            )
        ]
