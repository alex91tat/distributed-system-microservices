from sqlmodel import SQLModel, Field

class Movie(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str = Field(index=True)
    description: str
    genre: str
    release_year: int