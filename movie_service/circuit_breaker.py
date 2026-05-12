import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "CLOSED"
    HALF_OPEN = "HALF_OPEN"
    OPEN = "OPEN"


class CircuitBreaker:
    """
    Tracks failures when calling an external service and
    automatically stops sending requests when the service
    is considered unhealthy, preventing cascading failures.
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: float = 0


    def allow_request(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if enough time has passed to try again
            time_since_failure = time.time() - self.last_failure_time
            if time_since_failure >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                print(f"[CircuitBreaker] State: OPEN -> HALF_OPEN")
                return True

            return False

        if self.state == CircuitState.HALF_OPEN:
            return True

        return False

    def record_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            print(f"[CircuitBreaker] State: HALF_OPEN -> CLOSED")

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            print(f"[CircuitBreaker] State: HALF_OPEN -> OPEN")
            return

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(
                f"[CircuitBreaker] State: CLOSED -> OPEN "
                f"after {self.failure_count} failures"
            )

    @property
    def current_state(self) -> str:
        return self.state.value