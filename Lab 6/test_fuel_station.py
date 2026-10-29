import pytest
from fuel_station import fuel_bill, pump_allowed, session_status

# Example test cases:
def test_within_covered_litres():
    assert fuel_bill("regular", 8, "silver") == 0

def test_pump_allowed():
    assert pump_allowed(30, 1, False) is True

# Write the rest of the test cases so that the code is 90-100% covered.


# ---------- fuel_bill ----------
def test_unknown_grade():
    with pytest.raises(ValueError):
        fuel_bill("kerosene", 10, "silver")


def test_negative_litres():
    with pytest.raises(ValueError):
        fuel_bill("regular", -1, "silver")


def test_gold_regular_bonus_covered():
    # covered = 10 + 5 = 15, so 15 litres is free
    assert fuel_bill("regular", 15, "gold") == 0


def test_regular_extra_rate():
    # extra = 10, rate = 105
    assert fuel_bill("regular", 20, "silver") == 1050


def test_diesel_extra_rate():
    # extra = 10, rate = 90
    assert fuel_bill("diesel", 30, "silver") == 900


def test_bulk_discount_gold():
    # covered = 15, extra = 31, rate = 105 - 6 - 4 = 95
    assert fuel_bill("regular", 46, "gold") == 31 * 95


# ---------- pump_allowed ----------
def test_pump_fleet():
    assert pump_allowed(150, 5, True) is True


def test_pump_too_many_litres():
    assert pump_allowed(61, 1, False) is False


def test_pump_too_many_containers():
    assert pump_allowed(30, 2, False) is False


# ---------- session_status ----------
def test_session_active():
    assert session_status(100, True, False) == "active"


def test_session_warning():
    assert session_status(50, True, False) == "warning"


def test_session_timed_out():
    assert session_status(10, False, True) == "timed_out"