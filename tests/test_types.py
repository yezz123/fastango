import pytest

from fastango.types import AsyncRepository, Entity, Repository


@pytest.fixture
def sync_repo():
    class SyncRepo(Repository[Entity]):
        def __init__(self):
            self.entities = []

        def retrieve(self, *args, **kwargs):
            pass

        def create(self, entity: Entity, **kwargs):
            self.entities.append(entity)
            return entity

        def update(self, entity: Entity, **kwargs):
            pass

        def delete(self, *args, **kwargs):
            pass

        def list(self, *args, **kwargs):
            return self.entities

    return SyncRepo()


@pytest.fixture
def async_repo():
    class AsyncRepo(AsyncRepository[Entity]):
        def __init__(self):
            self.entities = []

        async def retrieve(self, *args, **kwargs):
            pass

        async def create(self, entity: Entity, **kwargs):
            self.entities.append(entity)
            return entity

        async def update(self, entity: Entity, **kwargs):
            pass

        async def delete(self, *args, **kwargs):
            pass

        async def list(self, *args, **kwargs):
            return self.entities

    return AsyncRepo()


def test_sync_repository_create(sync_repo):
    entity = {"id": 1, "name": "Test Entity"}
    created_entity = sync_repo.create(entity)
    assert created_entity == entity
    assert len(sync_repo.list()) == 1


@pytest.mark.asyncio
async def test_async_repository_create(async_repo):
    entity = {"id": 1, "name": "Test Entity"}
    created_entity = await async_repo.create(entity)
    assert created_entity == entity
    assert len(await async_repo.list()) == 1
