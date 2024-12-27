from pydantic import BaseModel


class BaseMetadata(BaseModel):
    indexes: list[str]

class BaseSchema(BaseModel):
    metadata: BaseMetadata