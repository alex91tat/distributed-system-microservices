from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select

from movie_service.circuit_breaker import CircuitBreaker
from movie_service.database import create_db_and_tables, seed_movies, get_session
from movie_service.models import Movie
from movie_service.schemas import MovieResponse, SimilarMovie


# asynccontextmanager turns this function into a context manager
# Everything before yield runs on startup, everything after on shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_movies()
    yield


app = FastAPI(title="Movie Service", lifespan=lifespan)

# Created once at startup, shared across all requests
circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

RECOMMENDATION_SERVICE_URL = "http://localhost:5002/recommendations"

TRENDING_FALLBACK = [
    SimilarMovie(id=5, title="The Matrix", genre="Sci-Fi", release_year=1999),
    SimilarMovie(id=7, title="The Shawshank Redemption", genre="Drama", release_year=1994),
    SimilarMovie(id=8, title="The Godfather", genre="Crime", release_year=1972),
    SimilarMovie(id=9, title="Fight Club", genre="Drama", release_year=1999),
]


def get_recommendations_from_service_b() -> list[int]:
    """
    Calls Recommendation Service with 1.5s timeout.
    Uses the circuit breaker to decide whether to attempt the call.
    """
    if not circuit_breaker.allow_request():
        print("[MovieService] Circuit is OPEN, skipping Service B")
        return []

    try:
        response = httpx.get(RECOMMENDATION_SERVICE_URL, timeout=1.5)

        if response.status_code == 200:
            circuit_breaker.record_success()
            return response.json().get("recommended_ids", [])
        else:
            print(f"[MovieService] Service B returned {response.status_code}")
            circuit_breaker.record_failure()
            return []

    except httpx.TimeoutException:
        # Chaos mode jitter caused this, request took over 1.5s
        print("[MovieService] Service B timed out after 1.5s")
        circuit_breaker.record_failure()
        return []

    except httpx.RequestError:
        # Service B is completely unreachable (not running at all)
        print("[MovieService] Service B is unreachable")
        circuit_breaker.record_failure()
        return []
    


@app.get("/movie/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, session: Session = Depends(get_session)) -> MovieResponse:
    """
    Main endpoint. Returns a movie with its recommendations.
    Session is injected by FastAPI via Depends(get_session)
    FastAPI calls get_session(), passes the result here, cleans up after
    """
    movie = session.exec(select(Movie).where(Movie.id == movie_id)).first()
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")

    recommended_ids = get_recommendations_from_service_b()

    if not recommended_ids:
        print("[MovieService] Using trending fallback")
        recommended_movies = TRENDING_FALLBACK
    else:
        recommended_movies = []
        for rec_id in recommended_ids:
            if rec_id == movie_id:
                continue
            rec_movie = session.exec(
                select(Movie).where(Movie.id == rec_id)
            ).first()

            if rec_movie:
                recommended_movies.append(SimilarMovie(id=rec_movie.id,title=rec_movie.title,genre=rec_movie.genre,release_year=rec_movie.release_year))

    return MovieResponse(id=movie.id, title=movie.title, description=movie.description, 
                         genre=movie.genre, release_year=movie.release_year,recommended_movies=recommended_movies)


@app.get("/circuit-status")
def get_circuit_status() -> dict:
    """
    Monitoring endpoint shows the current circuit breaker state.
    """
    return {
        "state": circuit_breaker.current_state,
        "failure_count": circuit_breaker.failure_count,
        "failure_threshold": circuit_breaker.failure_threshold,
        "recovery_timeout": circuit_breaker.recovery_timeout,
    }