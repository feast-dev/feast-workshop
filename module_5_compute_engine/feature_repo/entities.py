from feast import (
    Entity,
    ValueType,
)

customer = Entity(
    name="customer",
    join_keys=["O_CUSTKEY"],
    value_type=ValueType.INT64,
    description="Custoemr id",
)
