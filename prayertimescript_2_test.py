from prayertimescript_2 import find_time_difference
from prayertimescript_2 import find_time_until_prayer
import pytest
from prayertimescript_2 import check_for_next_prayer

def test_time_difference_less_than_hour():

    current_time = 1330
    prayer_time = 1360

    time_difference = find_time_difference(prayer_time, current_time)

    assert time_difference == 30


def test_time_difference_hour():

    current_time = 1330
    prayer_time = 1430

    time_difference = find_time_difference(prayer_time, current_time)

    assert time_difference == 60


def test_time_difference_more_than_an_hour():

    current_time = 1330
    prayer_time = 1500

    time_difference = find_time_difference(prayer_time,current_time)

    assert time_difference == 130


def test_time_difference_more_than_two_hours():

    current_time = 1330
    prayer_time = 1600

    time_difference = find_time_difference(prayer_time, current_time)

    assert time_difference == 230

def test_time_difference_less_than_ten_minutes():

    current_time = 1125
    prayer_time = 1130

    time_difference = find_time_difference(prayer_time, current_time)

    assert time_difference == 5

def test_time_until_prayer_over_an_hour():

    time_difference = 400

    time_until_prayer = find_time_until_prayer(time_difference)

    assert time_until_prayer == 14400


def test_time_until_prayer_less_than_hour():

    time_difference = 60

    time_until_prayer = find_time_until_prayer(time_difference)

    assert time_until_prayer == 3600







