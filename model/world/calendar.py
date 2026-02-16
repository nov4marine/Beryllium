class Calendar:
    def __init__(self, game_model, start_day=1, start_month=1, start_year=2200):
        self.game_model = game_model

        self.day = start_day
        self.month = start_month
        self.year = start_year

        # New Properties for time tracking
        self.time_per_game_day = 1  # 1 second in real time = in day in game
        self.time_per_tick = 0.1  # Duration of each "live" tick in real time seconds
        self.time_since_last_update = 0.00
        self.time_since_gui_update = 0.00 # Separate timer for GUI updates while paused

        self.live_observers = [] # Observers that get notified every update tick
        self.daily_observers = []
        self.monthly_observers = []

        self.ui_observers = [] # UI elements that need to be updated regardless of pause.

        self.paused = False

    def toggle_pause(self):
        self.paused = not self.paused

    @property
    def current_date(self):
        date = self.__str__()
        return date

    def advance_day(self):
        self.day += 1
        # Notify daily observers
        for observer in self.daily_observers:
            observer.on_daily_update()
        if self.day > 30:
            self.day = 1
            self.month += 1
            # Notify monthly observers
            for observer in self.monthly_observers:
                observer.on_monthly_update()
            if self.month > 12:
                self.month = 1
                self.year += 1
        
        self.current_date = self.__str__()
        print(f"{self.current_date} ⚙️ Day Advanced.")

    def update(self, delta_time):
        """Process the real time for the calendar"""
        for observer in self.regular_observers:
            observer.on_update(delta_time)

        self.paused_update(delta_time)

        if not self.paused:
            self.time_since_last_update += delta_time
            while self.time_since_last_update >= self.time_per_game_day:
                self.advance_day()
                self.time_since_last_update -= self.time_per_game_day

    def paused_update(self, delta_time):
        """Update that runs even when the game is paused, for UI elements that need to update regardless."""
        if self.paused:
            self.time_since_gui_update += delta_time
            if self.time_since_gui_update >= 0.5: # Update UI every 0.5 seconds while paused, for things like animated sprites or whatever.
                self.time_since_gui_update -= 0.5
                for observer in self.ui_observers:
                    observer.on_daily_update()

    def __str__(self):
        return f"{self.day}.{self.month}.{self.year}"
    
    def add_ui_observer(self, observer):
        if observer not in self.ui_observers:
            self.ui_observers.append(observer)
    
    def add_daily_observer(self, observer):
        if observer not in self.daily_observers:
            self.daily_observers.append(observer)

    def add_monthly_observer(self, observer):
        if observer not in self.monthly_observers:
            self.monthly_observers.append(observer)

    def add_live_observer(self, observer):
        if observer not in self.live_observers:
            self.live_observers.append(observer)