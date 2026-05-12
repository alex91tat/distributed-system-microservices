from sqlmodel import SQLModel, Session, create_engine, select

from movie_service.models import Movie

DATABASE_URL = "sqlite:///movies.db"

# The core connection to the database
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def seed_movies() -> None:
    """
    Inserts a default set of movies into the database if it is empty.
    """
    with Session(engine) as session:
        existing = session.exec(select(Movie)).first()
        if existing:
            return

        movies = [
            Movie(id=1, title="Inception", description="A thief who enters the dreams of others.", genre="Sci-Fi", release_year=2010),
            Movie(id=2, title="Interstellar", description="A team of explorers travel through a wormhole.", genre="Sci-Fi", release_year=2014),
            Movie(id=3, title="The Dark Knight", description="Batman faces the Joker in Gotham City.", genre="Action", release_year=2008),
            Movie(id=4, title="Pulp Fiction", description="The lives of criminals intertwine.", genre="Crime", release_year=1994),
            Movie(id=5, title="The Matrix", description="A hacker discovers the true nature of reality.", genre="Sci-Fi", release_year=1999),
            Movie(id=6, title="Forrest Gump", description="The life of a man with a low IQ but good heart.", genre="Drama", release_year=1994),
            Movie(id=7, title="The Shawshank Redemption", description="Two imprisoned men bond over years.", genre="Drama", release_year=1994),
            Movie(id=8, title="The Godfather", description="The aging patriarch of a crime dynasty.", genre="Crime", release_year=1972),
            Movie(id=9, title="Fight Club", description="An insomniac and a soap salesman form an underground club.", genre="Drama", release_year=1999),
            Movie(id=10, title="Goodfellas", description="The story of Henry Hill and his life in the mob.", genre="Crime", release_year=1990),
        ]

        session.add_all(movies)
        session.commit()


def get_session():
    """
    Dependency function for FastAPI.
    Yields a database session that is automatically closed after each request.
    This is used with FastAPI's dependency injection system.
    """
    with Session(engine) as session:
        yield session