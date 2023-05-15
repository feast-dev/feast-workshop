from feast import (
    Entity,
    ValueType,
)

driver = Entity(
    name="driver",
    join_keys=["driver_id"],
    value_type=ValueType.INT64,
    description="driver id"
)