from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str
    description: str | None = None
    needs_refrigeration: bool = False

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    category_id: int

    class Config:
        from_attributes = True