from datetime import datetime, timedelta
from typing import List, Tuple


class DatetimeRangeTracker:

    """
    A class used to track copied datetime ranges.

    It provides methods to add a copied date range, check if a
    given date range has been copied, get the date ranges that haven't been copied,
    and automatically merges contiguous date ranges when a new range is added.
    """

    copied_ranges: List[Tuple[datetime, datetime]]

    def __init__(self, copied_ranges: List[Tuple[datetime, datetime]] = None):
        self.copied_ranges = copied_ranges or []

    def mark_range_as_copied(self, start: datetime, end: datetime):
        """Inform the tracker that the input date range has been copied"""
        # TODO make this more efficient by adding to the correct place in the sorted list
        self.copied_ranges.append((start, end))
        self.copied_ranges.sort(key=lambda x: x[0])  # Always keep the list sorted
        self._merge_contiguous()

    def get_copied_ranges(self) -> List[Tuple[datetime, datetime]]:
        return self.copied_ranges

    def get_uncopied_ranges(
            self,
            start: datetime,
            end: datetime = None,
            preferred_range_size: timedelta = None,
            descending: bool = False
    ) -> List[Tuple[datetime, datetime]]:
        """
        Returns a list of date ranges within the given range that haven't been copied. The returned ranges will be at most as large as
        preferred_range_size. A range may be smaller than preferred_range_size if no adjacent uncopied range was found.

        :param end
        :param start
        :param preferred_range_size: the preferred size of the returned ranges
        @param descending:
        """
        uncopied_ranges = []
        current_start = start
        end = end or datetime.now()
        preferred_range_size = preferred_range_size or timedelta(days=10_000)

        for copied_start, copied_end in self.copied_ranges:
            if current_start < copied_start:
                # There's a gap between current_start and copied_start
                while copied_start - current_start > preferred_range_size:
                    uncopied_ranges.append((current_start, current_start + preferred_range_size))
                    current_start += preferred_range_size
                uncopied_ranges.append((current_start, copied_start))
            if copied_end > current_start:
                # Move the current_start pointer
                current_start = copied_end

        # Check if there's still uncopied range after the last copied range
        while end - current_start > preferred_range_size:
            uncopied_ranges.append((current_start, current_start + preferred_range_size))
            current_start += preferred_range_size

        if current_start < end:
            uncopied_ranges.append((current_start, end))

        if descending:
            uncopied_ranges = reversed(uncopied_ranges)

        return uncopied_ranges

    def _merge_contiguous(self):
        merged = []
        for start, end in self.copied_ranges:
            if not merged or merged[-1][1] < start:
                # If merged is empty or the last interval does not overlap with start,
                # append a new interval.
                merged.append((start, end))
            else:
                # Otherwise, there is overlap, so we merge the current and previous intervals.
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))

        self.copied_ranges = merged
