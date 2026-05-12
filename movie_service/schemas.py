from sqlmodel import SQLModel

class MovieBase(SQLModel):
    """
    Shared fields between all movie schemas.
    Both the DB model and API responses share these fields.
    """
    title: str
    genre: str
    release_year: int


class MovieResponse(MovieBase):
    """
    What we return to the user when they request a single movie.
    Includes the recommended similar movies fetched from Service B.
    """
    id: int
    description: str
    recommended_movies: list["SimilarMovie"] = []



class SimilarMovie(SQLModel):
    """
    A simplified movie representation used inside recommendations.
    We don't need the full description when showing similar movies.
    """
    id: int
    title: str
    genre: str
    release_year: int