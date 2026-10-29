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
    with pytest.raises(ValueError, match="unknown fuel grade"):
        fuel_bill("kerosene", 10, "silver")


def test_negative_litres():
    with pytest.raises(ValueError, match="invalid litres"):
        fuel_bill("regular", -1, "silver")


def test_zero_litres():
    assert fuel_bill("regular", 0, "silver") == 0


def test_exactly_covered_litres():
    # extra == 0 boundary
    assert fuel_bill("premium", 15, "silver") == 0


def test_gold_regular_bonus_covered():
    # covered = 10 + 5 = 15
    assert fuel_bill("regular", 15, "gold") == 0


def test_gold_premium_bonus_covered():
    # covered = 15 + 5 = 20
    assert fuel_bill("premium", 20, "gold") == 0


def test_gold_diesel_gets_no_bonus():
    # covered stays 20, extra = 10, rate = 90
    assert fuel_bill("diesel", 30, "gold") == 900


def test_silver_regular_no_bonus():
    # extra = 10, rate = 105
    assert fuel_bill("regular", 20, "silver") == 1050


def test_diesel_extra_rate():
    assert fuel_bill("diesel", 30, "silver") == 900


def test_extra_exactly_30_no_bulk_discount():
    # extra = 30 (not > 30), rate stays 105
    assert fuel_bill("regular", 40, "silver") == 30 * 105


def test_bulk_discount_regular_non_gold():
    # extra = 31, rate = 105 - 6 = 99
    assert fuel_bill("regular", 41, "silver") == 31 * 99


def test_bulk_discount_premium_non_gold():
    # covered = 15, extra = 31, rate = 99
    assert fuel_bill("premium", 46, "silver") == 31 * 99


def test_bulk_discount_regular_gold():
    # covered = 15, extra = 31, rate = 105 - 6 - 4 = 95
    assert fuel_bill("regular", 46, "gold") == 31 * 95


def test_bulk_discount_diesel_non_gold():
    # covered = 20, extra = 31, rate = 90 - 6 = 84
    assert fuel_bill("diesel", 51, "silver") == 31 * 84


def test_bulk_discount_diesel_gold():
    # covered = 20, extra = 31, rate = 90 - 6 - 4 = 80
    assert fuel_bill("diesel", 51, "gold") == 31 * 80


# ---------- pump_allowed ----------
def test_pump_fleet_within_limit():
    assert pump_allowed(150, 5, True) is True


def test_pump_fleet_at_limit():
    assert pump_allowed(200, 5, True) is True


def test_pump_fleet_over_limit():
    assert pump_allowed(201, 1, True) is False


def test_pump_non_fleet_over_60_litres():
    assert pump_allowed(61, 1, False) is False


def test_pump_non_fleet_at_60_litres():
    assert pump_allowed(60, 1, False) is True


def test_pump_non_fleet_too_many_containers():
    assert pump_allowed(30, 2, False) is False


def test_pump_non_fleet_zero_containers():
    assert pump_allowed(30, 0, False) is True


# ---------- session_status ----------
# cutoff: card = 60, cash = 30, night adds 30

def test_session_card_day_active_at_cutoff():
    assert session_status(60, True, False) == "active"


def test_session_card_day_warning_upper():
    assert session_status(59, True, False) == "warning"


def test_session_card_day_warning_lower():
    assert session_status(45, True, False) == "warning"


def test_session_card_day_timed_out():
    assert session_status(44, True, False) == "timed_out"


def test_session_cash_day_active():
    assert session_status(30, False, False) == "active"


def test_session_cash_day_warning():
    assert session_status(15, False, False) == "warning"


def test_session_cash_day_timed_out():
    assert session_status(14, False, False) == "timed_out"


def test_session_card_night_active():
    assert session_status(90, True, True) == "active"


def test_session_card_night_warning():
    assert session_status(75, True, True) == "warning"


def test_session_card_night_timed_out():
    assert session_status(74, True, True) == "timed_out"


def test_session_cash_night_active():
    assert session_status(60, False, True) == "active"


def test_session_cash_night_warning():
    assert session_status(45, False, True) == "warning"


def test_session_cash_night_timed_out():
    assert session_status(44, False, True) == "timed_out"