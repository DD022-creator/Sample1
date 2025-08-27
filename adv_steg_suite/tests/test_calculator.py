# tests/test_calculator.py

import pytest

# Example class to test
class Calculator:
    def add(self, a, b):
        return a + b
    def subtract(self, a, b):
        return a - b

# Tests
def test_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_subtract():
    calc = Calculator()
    assert calc.subtract(5, 3) == 2
