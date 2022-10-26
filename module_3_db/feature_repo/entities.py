from feast import (
    Entity,
)

user = Entity(
    name="user",
    join_keys=["user_id"],
    description="user id",
)
