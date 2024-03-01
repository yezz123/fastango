from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal, TypeVar

from pydantic import TypeAdapter

T = TypeVar("T")


class TypeSerializer(TypeAdapter[T]):
    """
    A type adapter that can be used to serialize and deserialize Python objects to and from JSON.

    Args:
        TypeAdapter (TypeAdapter): The base type adapter class from which this class inherits.

    Returns:
        TypeSerializer: A type adapter that can be used to serialize and deserialize Python objects to and from JSON.
    """

    def __init__(self) -> None:
        """
        This method initializes the TypeSerializer class.
        """
        # we should call serialize  methods from the base class
        super().__init__(T)

    def serialize(
        self,
        obj: Any,
        *,
        validate: bool = True,
        from_attributes: bool | Literal["auto"] = True,
        **options: Any,
    ) -> bytes:
        """
        This method serializes a Python object to a JSON string.

        Args:
            obj (Any): The Python object to be serialized.
            validate (bool, optional): A flag that indicates whether the object should be validated before serialization. Defaults to True.
            from_attributes (bool | Literal[&quot;auto&quot;], optional): A flag that indicates whether the object should be serialized from its attributes.

        Returns:
            bytes: The JSON string that represents the serialized object.
        """
        if validate:
            if from_attributes == "auto":
                from_attributes = not isinstance(obj, Mapping) or (
                    isinstance(obj, Sequence)
                    and all(isinstance(el, Mapping) for el in obj)
                )
            obj = self.validate_python(obj, from_attributes=from_attributes)
        return self.dump_json(obj, **options)
