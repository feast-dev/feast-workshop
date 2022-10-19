from feast import (
    Entity,
)

user = Entity(
    name="user",
    join_keys=["USER_ID"],
    description="user id",
)
