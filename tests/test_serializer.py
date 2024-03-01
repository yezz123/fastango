import pytest

from fastango.serializer import TypeSerializer


class TestTypeSerializer:
    @pytest.fixture
    def type_serializer(self):
        return TypeSerializer()

    def test_serialize_valid(self, type_serializer):
        obj = {"key": "value"}
        serialized_data = type_serializer.serialize(obj)
        assert isinstance(serialized_data, bytes)

    def test_serialize_auto_detection(self, type_serializer):
        # Define a sample object where auto-detection should be used
        obj = [{"key1": "value1"}, {"key2": "value2"}]  # List of dictionaries

        # Call the serialize method with from_attributes="auto"
        serialized_data = type_serializer.serialize(obj, from_attributes="auto")

        # Assert that serialized_data is of type bytes
        assert isinstance(serialized_data, bytes)
