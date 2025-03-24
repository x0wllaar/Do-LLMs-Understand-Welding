from pydantic import BaseModel, Field

class Acceptability(BaseModel):
    acceptable: bool = Field()