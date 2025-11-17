"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal, List

# Writing assistant schemas

class Document(BaseModel):
    """
    Documents created by the user
    Collection name: "document"
    """
    title: str = Field(..., description="Document title")
    content: str = Field("", description="Full document text")
    language: str = Field("en", description="Language code")

class Edit(BaseModel):
    """
    Transformation/edit events applied to text
    Collection name: "edit"
    """
    document_id: Optional[str] = Field(None, description="Related document id")
    mode: Literal[
        "clarity",
        "formal",
        "concise",
        "expand",
        "summarize",
        "bulletize"
    ]
    input_text: str
    output_text: str

# Example schemas (kept for reference; not used by the app but useful for testing)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    category: str
    in_stock: bool = True

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
