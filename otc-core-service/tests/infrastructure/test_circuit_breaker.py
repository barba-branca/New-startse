import pytest
import time
from ...src.infrastructure.circuit_breaker import CircuitBreaker

def test_circuit_breaker_opens_after_failures():
    # Arrange
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    
    def failing_func():
        raise Exception("Service Down")
    
    # Act
    # 1st failure
    with pytest.raises(Exception):
        breaker.call(failing_func)
    assert breaker.state == "CLOSED"
    
    # 2nd failure
    with pytest.raises(Exception):
        breaker.call(failing_func)
    
    # Assert
    assert breaker.state == "OPEN"
    with pytest.raises(Exception, match="Circuit Breaker OPEN"):
        breaker.call(failing_func)

def test_circuit_breaker_recovers_after_timeout():
    # Arrange
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
    
    def failing_func():
        raise Exception("Service Down")
        
    def success_func():
        return "OK"
    
    # Act
    # Trip the breaker
    with pytest.raises(Exception):
        breaker.call(failing_func)
    assert breaker.state == "OPEN"
    
    # Wait for recovery timeout
    time.sleep(0.2)
    
    # Assert recovery to HALF-OPEN then CLOSED on success
    result = breaker.call(success_func)
    assert result == "OK"
    assert breaker.state == "CLOSED"
