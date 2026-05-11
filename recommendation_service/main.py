import os
import random
import time

from fastapi import FastAPI, HTTPException

# FastAPI() creates the application instance
app = FastAPI(title="Recommendation Service")

MOVIE_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

def maybe_chaos() -> None:
    """
    Reads CHAOS_MODE from environment variables at runtime.
    If enabled, randomly triggers one of two failure modes:
    - Sleep 3-10 seconds (network jitter)
    - Raise HTTP 503 (partial failure)
    """
    chaos = os.environ.get("CHAOS_MODE", "false").lower() == "true"
    if not chaos:
        return

    # 50/50 chance between the two failure modes
    if random.random() < 0.5:
        # Network jitter
        delay = random.uniform(3, 10)
        time.sleep(delay)
    else:
        # Partial failure 
        raise HTTPException(
            status_code=503,
            detail="Recommendation Service unavailable (chaos mode)"
        )
    

@app.get("/recommendations")
def get_recommendations() -> dict[str, list[int]]:
    maybe_chaos()
    return {"recommended_ids" : MOVIE_IDS}