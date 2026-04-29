#!/usr/bin/env python3
"""Focused tests for Google Fit sleep extraction helpers."""

import unittest
from datetime import datetime, timezone

import fitness_tracker


def sleep_point(start_ms, end_ms, stage):
    return {
        "startTimeNanos": str(start_ms * 1_000_000),
        "endTimeNanos": str(end_ms * 1_000_000),
        "value": [{"intVal": stage}],
    }


class SleepExtractionTests(unittest.TestCase):
    def test_parse_sleep_data_counts_only_sleep_stages(self):
        hour = 60 * 60 * 1000
        points = [
            sleep_point(0, hour, 1),          # Awake during sleep cycle.
            sleep_point(hour, 3 * hour, 4),   # Light sleep.
            sleep_point(3 * hour, 4 * hour, 3),  # Out of bed.
            sleep_point(4 * hour, 5 * hour, 6),  # REM.
        ]

        self.assertEqual(fitness_tracker.parse_sleep_data(points), 3.0)

    def test_parse_sleep_data_merges_overlapping_segments(self):
        hour = 60 * 60 * 1000
        points = [
            sleep_point(0, 2 * hour, 2),
            sleep_point(hour, 3 * hour, 5),
        ]

        self.assertEqual(fitness_tracker.parse_sleep_data(points), 3.0)

    def test_sleep_hours_by_day_uses_session_end_date(self):
        original_list = fitness_tracker.list_sleep_sessions
        original_aggregate = fitness_tracker.aggregate_sleep_session
        try:
            fitness_tracker.list_sleep_sessions = lambda *_: [
                {
                    "startTimeMillis": "1704153600000",
                    "endTimeMillis": "1704178800000",
                }
            ]
            fitness_tracker.aggregate_sleep_session = lambda *_: 7.0

            result = fitness_tracker.get_sleep_hours_by_day(
                "token",
                datetime(2024, 1, 2, tzinfo=timezone.utc),
                datetime(2024, 1, 3, tzinfo=timezone.utc),
            )

            self.assertEqual(result, {"2024-01-02": 7.0})
        finally:
            fitness_tracker.list_sleep_sessions = original_list
            fitness_tracker.aggregate_sleep_session = original_aggregate


if __name__ == "__main__":
    unittest.main()
