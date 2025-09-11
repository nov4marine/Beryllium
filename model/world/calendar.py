
class Calendar:
    def __init__(self, start_day=1, start_month=1, start_year=2200):
        self.day = start_day
        self.month = start_month
        self.year = start_year

        # New Properties for time tracking
        self.time_per_game_day = 1  # 1 second in real time = in day in game
        self.time_since_last_update = 0.00

    def advance_day(self):
        self.day += 1
        if self.day > 30:
            self.day = 1
            self.month += 1
            if self.month > 12:
                self.month = 1
                self.year += 1

    def update(self, delta_time):
        """Process the real time for the calendar"""
        self.time_since_last_update += delta_time
        while self.time_since_last_update >= self.time_per_game_day:
            self.advance_day()
            self.time_since_last_update -= self.time_per_game_day

    def __str__(self):
        return f"Day {self.day}, Month {self.month}, Year {self.year}"
