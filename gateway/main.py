import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="API Gateway")

MOVIE_SERVICE_URL = "http://localhost:5001"


@app.get("/movie/{movie_id}")
async def get_movie(movie_id: int):
    """
    Forwards the request to Movie Service.
    """
    try:
        # Forward the request to Movie Service with a 5s timeout
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MOVIE_SERVICE_URL}/movie/{movie_id}",
                timeout=5.0
            )
        return response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Movie Service timed out"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Movie Service is unreachable"
        )


@app.get("/circuit-status")
async def get_circuit_status():
    """
    Forwards circuit breaker status request to Movie Service.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MOVIE_SERVICE_URL}/circuit-status",
                timeout=5.0
            )
        return response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Movie Service is unreachable"
        )
    

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <body style="font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px;">
            <h1>Movie Recommendation System</h1>
            <p>Click a movie to see its details and recommendations:</p>
            <ul>
                <li><a href="/ui/movie/1">Inception</a></li>
                <li><a href="/ui/movie/2">Interstellar</a></li>
                <li><a href="/ui/movie/3">The Dark Knight</a></li>
                <li><a href="/ui/movie/4">Pulp Fiction</a></li>
                <li><a href="/ui/movie/5">The Matrix</a></li>
                <li><a href="/ui/movie/6">Forrest Gump</a></li>
                <li><a href="/ui/movie/7">The Shawshank Redemption</a></li>
                <li><a href="/ui/movie/8">The Godfather</a></li>
                <li><a href="/ui/movie/9">Fight Club</a></li>
                <li><a href="/ui/movie/10">Goodfellas</a></li>
            </ul>
        </body>
    </html>
    """


@app.get("/ui/movie/{movie_id}", response_class=HTMLResponse)
async def get_movie_ui(movie_id: int):
    """
    Returns an HTML page for a movie.
    Even if Service B is down
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MOVIE_SERVICE_URL}/movie/{movie_id}",
                timeout=5.0
            )
        data = response.json()

        # Build recommendations HTML
        recommendations_html = ""
        for movie in data.get("recommended_movies", []):
            recommendations_html += f"""
                <li>
                    <a href="/ui/movie/{movie['id']}">
                        {movie['title']} ({movie['release_year']}) — {movie['genre']}
                    </a>
                </li>
            """

        return f"""
        <html>
            <body style="font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px;">
                <a href="/">Back to all movies</a>
                <h1>{data['title']} ({data['release_year']})</h1>
                <p><strong>Genre:</strong> {data['genre']}</p>
                <p><strong>Description:</strong> {data['description']}</p>
                <hr>
                <h2>Recommended Movies</h2>
                <ul>{recommendations_html}</ul>
                <hr>
                <p><a href="/circuit-status">Check Circuit Breaker Status</a></p>
            </body>
        </html>
        """

    except httpx.TimeoutException:
        return """
        <html>
            <body style="font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px;">
                <h1>Service Temporarily Unavailable</h1>
                <p>Please try again in a moment.</p>
                <a href="/">Back to all movies</a>
            </body>
        </html>
        """

    except httpx.RequestError:
        return """
        <html>
            <body style="font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px;">
                <h1>Service Temporarily Unavailable</h1>
                <p>Please try again in a moment.</p>
                <a href="/">Back to all movies</a>
            </body>
        </html>
        """