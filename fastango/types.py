from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Protocol, TypedDict, TypeVar

if TYPE_CHECKING:
    from pydantic.type_adapter import IncEx

Entity = TypeVar("Entity", bound=Any)
Action = Literal["create", "list", "retrieve", "update", "destroy", "partial_update"]


class SerializerOptions(TypedDict, total=False):
    validate: bool
    from_attributes: bool | Literal["auto"]
    indent: int | None
    include: IncEx | None
    exclude: IncEx | None
    by_alias: bool
    exclude_unset: bool
    exclude_defaults: bool
    exclude_none: bool
    round_trip: bool
    warnings: bool


class Repository(Protocol[Entity]):
    def retrieve(self, *args, **kwargs) -> Entity | None: ...

    def create(self, entity: Entity, **kwargs) -> Entity | None: ...

    def update(self, entity: Entity, **kwargs) -> Entity | None: ...

    def delete(self, *args, **kwargs) -> None: ...

    def list(self, *args, **kwargs) -> list[Entity]: ...


class AsyncRepository(Protocol[Entity]):
    async def retrieve(self, *args, **kwargs) -> Entity | None: ...

    async def create(self, entity: Entity, **kwargs) -> Entity | None: ...

    async def update(self, entity: Entity, **kwargs) -> Entity | None: ...

    async def delete(self, *args, **kwargs) -> None: ...

    async def list(self, *args, **kwargs) -> list[Entity]: ...
