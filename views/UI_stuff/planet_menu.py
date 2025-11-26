import arcade
import arcade.gui


class GenericMenu:
    """
    A generic menu window with a title bar and close button. Content area to be filled by subclasses.
    To use, subclass and override setup_content() to populate the content_frame.
    Ensure to call open_window() to show the menu and enable the manager. Then call draw() in your view's draw() method,
    and update() in your view's on_update() method (or once monthly/daily if preferred).
    """

    # This should always exist in the view or persistent UI, and is activated when needed, which opens the window
    # with the relevant object updating the content.
    def __init__(self, asset_manager=None):
        self.manager = arcade.gui.UIManager()
        self.asset_manager = asset_manager

        self.root = arcade.gui.UIAnchorLayout()
        self.manager.add(self.root)
        self.window = arcade.gui.UIAnchorLayout(size_hint=(0.7, 0.7))
        self.window.with_background(color=arcade.color.DARK_SLATE_GRAY)  # Can probably delete this
        self.root.add(self.window)

        self.top_bar = arcade.gui.UIAnchorLayout(size_hint=(1, 0.08))
        self.top_bar.with_background(color=arcade.color.DARK_BLUE_GRAY)
        self.title_label = arcade.gui.UILabel(text="Menu Title", font_size=18)
        self.close_button = arcade.gui.UIFlatButton(text="X", size_hint=(0.08, 0.8))
        self.close_button.on_click = self.close_window

        self.top_bar.add(self.title_label, anchor_x="center")
        self.top_bar.add(self.close_button, anchor_x="right")
        self.window.add(self.top_bar, anchor_y="top")

        self.content_frame = arcade.gui.UIAnchorLayout(size_hint=(1, 0.92))
        self.content_frame.with_background(color=arcade.color.LIGHT_GRAY)
        self.window.add(self.content_frame, anchor_y="bottom")

        # List of content widgets that need daily updates
        self.short_term_updatable_content = []  # List of content widgets that are specific to current tab and must be cleared on tab switch
        self.long_term_updatable_content = []  # List of content widgets that persist across tabs, and should never be cleared

        #self.setup_content() # Populate content_frame
        # I'm realizing the above line may be better called when opening the window with specific data, allowing the menu to be created before data exists.

    def setup_content(self):
        """
        To be overridden by subclasses to populate content_frame. Does nothing on its own.
        Add widgets/layouts to self.content_frame here, which is an anchor layout filling most of the window.
        """
        pass

    def draw(self):
        if self.manager._enabled:
            self.manager.draw()

    def on_daily_update(self):
        if self.manager._enabled: # This doesn't necessarily need to be implemented unless there are performance issues. 
            #updating every frame is probably fine for most cases.
            pass  # To be overridden by subclasses

    def open_window(self):
        self.manager.enable()

    def close_window(self, event=None):
        # Hide or destroy the menu (implementation depends on your view system)
        self.manager.disable()
        # Optionally: remove from parent, or set a flag
        # You can expand this as needed
        pass


class PlanetMenu(GenericMenu):
    """
    A menu window for displaying and managing a planet/colony.
    Inherits from GenericMenu. Overrides setup_content() to create tabs and content areas.
    Call set_planet(colony) to set the current colony to display.
    All content must be added to the content_frame defined in GenericMenu. (and probably cleared first)
    """

    def __init__(self, persistent_ui, asset_manager):
        super().__init__(asset_manager)
        self.planet = None  # Will be set to a Colony
        self.nation = None  # Does nothing for now, but could be useful

        self.persistent_ui = persistent_ui
        self.asset_manager = asset_manager

        self.current_tab = None

        # Utilities 
        # RGBA: (R, G, B, A), where A is 0 (fully transparent) to 255 (fully opaque)
        self.semi_transparent_bg = (30, 30, 30, 180)  # Dark gray, mostly opaque

        self.grid = arcade.gui.UIGridLayout(size_hint=(1, 1), row_count=3, column_count=4)
        self.grid.with_background(color=arcade.color.CHARCOAL)
        self.content_frame.add(self.grid)

        tabs = arcade.gui.UIButtonRow()
        tabs.add_button("Summary")
        tabs.add_button("Economy")

        @tabs.event("on_action")
        def on_click_tab(event):
            print("Tab clicked:", event.action)
            if event.action == "Summary":
                print("Switching to Summary tab")
                self.show_summary_tab()
            elif event.action == "Economy":
                print("Switching to Economy tab")
                self.show_economy_tab()
        self.content_frame.add(tabs, anchor_x="left", anchor_y="bottom", align_y=-50)

    def box1(self):
        # --- Box 1 --- Primary planet art and info with governor portrait and name
        box1 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Primary planet art and info
        #climate = self.planet.planet.climate if self.planet and self.planet.planet else "not_implemented"
        climate = self.planet.planet.climate if self.planet else "continental"
        print(f"Planet climate for menu: {climate}")
        climate_background = self.asset_manager.ui_art.get(climate, self.asset_manager.ui_art["default"])
        box1.with_background(texture=climate_background)
        box1.with_border()

        stats_box = arcade.gui.UIBoxLayout(vertical=False, size_hint=(1, 0.1), space_between=50)  # Key stats
        stats_box.with_padding(all=10)
        stats_box.with_background(color=self.semi_transparent_bg)
        self.gdp_label = arcade.gui.UILabel(text=f"GDP: {self.planet.local_bls.statistics.get('gdp', 'N/A')}")
        self.population_label = arcade.gui.UILabel(
            text=f"Population: {self.planet.local_bls.statistics.get('population', 'N/A')}")
        self.stability_label = arcade.gui.UILabel(
            text=f"Stability: {self.planet.local_bls.statistics.get('stability', 'N/A')}")
        self.unemployment_label = arcade.gui.UILabel(
            text=f"Unemployment: {self.planet.local_bls.statistics.get('unemployment_rate', 'N/A')}%")

        stats_box.add(self.gdp_label)
        stats_box.add(self.population_label)
        stats_box.add(self.stability_label)
        stats_box.add(self.unemployment_label)
        box1.add(stats_box, anchor_y="bottom")
        self.grid.add(box1, row=0, column=0, column_span=3)


    def open_window(self, colony):
        self.planet = colony
        self.title_label.text = getattr(colony, 'name', 'Planet')
        self.show_summary_tab()
        self.manager.enable()

    def show_summary_tab(self):
        self.grid.clear()  # Clear previous content
        self.current_tab = "Summary"
        self.short_term_updatable_content.clear()

        # --- Box 1 --- Primary planet art and info with governor portrait and name
        self.box1()
        climate = self.planet.planet.climate if self.planet else "continental"

        # --- Box 2 --- Buildings overview
        box2 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Buildings overview
        box2.with_border()
        self.grid.add(box2, row=1, column=0, column_span=2, row_span=2)

        urban_box = arcade.gui.UIAnchorLayout(size_hint=(1, 0.5))  # Urban buildings
        urban_box.with_border()
        urban_label = arcade.gui.UILabel(text="Urban Buildings")
        urban_buildings = arcade.gui.UIBoxLayout(vertical=False, size_hint=(1, 0.9), space_between=10)
        urban_buildings.with_padding(all=100)
        # --- Urban buildings grid ---
        urban_building_list = []
        if self.planet and self.planet.buildings:
            # only do the first 6 urban buildings for now 
            for building in self.planet.buildings:
                if building.geography == "Urban":
                    urban_building_list.append(building)
            for building in urban_building_list[:7]:
                urban_button = BuildingWidget(self, building, self.asset_manager, size=100)
                urban_buildings.add(urban_button)

        urban_box.add(urban_label, anchor_y="top")
        urban_box.add(urban_buildings, anchor_x="center", anchor_y="center")
        box2.add(urban_box, anchor_y="top")

        rural_box = arcade.gui.UIAnchorLayout(size_hint=(1, 0.5))  # Rural buildings
        rural_box.with_border()
        rural_label = arcade.gui.UILabel(text="Rural Buildings")
        rural_buildings = arcade.gui.UIBoxLayout(vertical=False, size_hint=(1, 0.9), space_between=10)
        rural_buildings.with_padding(all=100)
        # --- Rural buildings grid ---
        rural_buildings_list = []
        if self.planet and self.planet.buildings:
            for building in self.planet.buildings:
                if building.geography == "Rural":
                    rural_buildings_list.append(building)
            for building in rural_buildings_list[:7]:
                rural_widget_button = BuildingWidget(self, building, self.asset_manager, size=100)
                rural_buildings.add(rural_widget_button)

        rural_box.add(rural_label, anchor_y="top")
        rural_box.add(rural_buildings, anchor_y="center", anchor_x="center")
        box2.add(rural_box, anchor_y="bottom")

        # --- Box 3 --- Celestial body info
        box3 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # celestial body info
        box3.with_border()
        box3.with_background(
            texture=self.asset_manager.ui_art.get("solar_system_background", self.asset_manager.ui_art["default"]))
        self.grid.add(box3, row=0, column=3)

        planet_info = arcade.gui.UIBoxLayout(vertical=True, size_hint=(0.5, 1), space_between=10, anchor_y="center")
        planet_label = arcade.gui.UILabel(text="Planet Summary", bold=True)
        climate_label = arcade.gui.UILabel(text=f"{'Climate'}: {climate}")
        habitability_label = arcade.gui.UILabel(text="Habitability: 100%")
        year_label = arcade.gui.UILabel(text="Year Founded: TBD")

        planet_info.add(planet_label)
        planet_info.add(climate_label)
        planet_info.add(habitability_label)
        planet_info.add(year_label)
        box3.add(planet_info, anchor_x="left")

        planet_sprite_box = arcade.gui.UIAnchorLayout(size_hint=(0.5, 1))
        #planet_sprite = PlanetSprite() # Placeholder for a sprite or image widget
        #planet_sprite_box.add(planet_sprite)
        box3.add(planet_sprite_box, anchor_x="right")

        # --- Box 4 --- Local market info

        # Import MarketGoodWidget
        from views.UI_stuff.market_gui import MarketGoodWidget
        # End import

        box4 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Local market info
        box4.with_border()
        self.grid.add(box4, row=1, column=2, row_span=2)

        frame = arcade.gui.UIBoxLayout(vertical=True, size_hint=(1, 1))
        box4.add(frame)

        # Box 4a - expensive goods
        box4a = arcade.gui.UIBoxLayout(vertical=True, size_hint=(1, 0.5), space_between=2)
        box4a.with_border(color=arcade.color.STEEL_BLUE)
        expensive_market_label = arcade.gui.UILabel(text="Expensive Goods")
        box4a.add(expensive_market_label)
        for good in self.planet.local_market.get_expensive_goods(number=5):
            #good_label = arcade.gui.UILabel(text=f"{good.name}: ${good.current_price}")
            #box4a.add(good_label)
            expensive_good_widget = MarketGoodWidget(good, self.asset_manager)
            box4a.add(expensive_good_widget)
            self.short_term_updatable_content.append(expensive_good_widget)

        # Box 4b - cheap goods
        box4b = arcade.gui.UIBoxLayout(vertical=True, size_hint=(1, 0.5), space_between=2, align="bottom")
        box4b.with_border(color=arcade.color.STEEL_BLUE)
        cheap_market_label = arcade.gui.UILabel(text="Cheap Goods")
        box4b.add(cheap_market_label)
        for good in self.planet.local_market.get_cheap_goods(number=5):
            #good_label = arcade.gui.UILabel(text=f"{good.name}: ${good.current_price}")
            #box4b.add(good_label)
            cheap_good_widget = MarketGoodWidget(good, self.asset_manager)
            box4b.add(cheap_good_widget)
            self.short_term_updatable_content.append(cheap_good_widget)

        market_label = arcade.gui.UILabel(text="Local Market")
        frame.add(market_label, anchor_y="top")
        frame.add(box4a, anchor_y="top")
        frame.add(box4b, anchor_y="bottom")

        # --- Box 5 --- Build queue
        box5 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Build queue
        box5.with_border()
        self.grid.add(box5, row=1, column=3, row_span=2)

        build_queue_label = arcade.gui.UILabel(text="Build Queue")
        box5.add(build_queue_label, anchor_y="top")


    def show_economy_tab(self):
        self.grid.clear()  # Clear previous content
        self.current_tab = "Economy"
        self.short_term_updatable_content.clear()

        self.grid = arcade.gui.UIGridLayout(size_hint=(1, 1), row_count=3, column_count=4)
        self.grid.with_background(color=arcade.color.CHARCOAL)

        # --- Box 1 --- Planet art and overview
        self.box1()

        # --- Box 2 --- Pie chart of economy sectors
        box2 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # pie chart of economy sectors
        box2.with_border()
        # Add stuff here later
        self.grid.add(box2, row=0, column=3) # Add completed box to grid

        # Box 3, 4, and 5 will be a building grid of urban, rural, and government buildings respectively

        # --- Box 3 --- Urban buildings
        box3 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Urban buildings
        box3.with_border()
        # --- Urban buildings grid ---
        urban_buildings_grid = BuildingGrid(self, "Urban", self.asset_manager)
        box3.add(urban_buildings_grid, anchor_x="center", anchor_y="center")
        self.grid.add(box3, row=1, column=0, row_span=2)

        # --- Box 4 --- Rural buildings
        box4 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Rural buildings
        box4.with_border()
        # --- Rural buildings grid ---
        rural_buildings_grid = BuildingGrid(self, "Rural", self.asset_manager)
        box4.add(rural_buildings_grid, anchor_x="center", anchor_y="center")
        self.grid.add(box4, row=1, column=1, row_span=2)

        # --- Box 5 --- Government buildings
        box5 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Government buildings
        box5.with_border()
        # --- Government buildings grid ---
        self.grid.add(box5, row=1, column=2, row_span=2)

        # --- Box 6 --- More charts and graphs of economy ---
        box6 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # More charts and stats of economy
        box6.with_border()
        # Add stuff here later
        self.grid.add(box6, row=1, column=3, row_span=2)

        # add completed grid to content frame for display
        self.content_frame.add(self.grid)

    def on_daily_update(self):
        if self.manager._enabled: # This doesn't necessarily need to be implemented unless there are performance issues. 
            for content in self.short_term_updatable_content:
                content.on_daily_update()
            for content in self.long_term_updatable_content:
                content.on_daily_update()

        if self.current_tab == "Summary":
            self.gdp_label.text = f"GDP: {self.planet.local_bls.statistics.get('gdp', 'N/A')}"
            self.population_label.text = f"Population: {self.planet.local_bls.statistics.get('population', 'N/A')}"
            self.stability_label.text = f"Stability: {self.planet.local_bls.statistics.get('stability', 'N/A')}"
            self.unemployment_label.text = f"Unemployment: {self.planet.local_bls.statistics.get('unemployment_rate', 'N/A')}%"

            

class BuildingWidget(arcade.gui.UITextureButton):
    def __init__(self, planet_menu, building, asset_manager, size=80):
        # Get the building icon texture
        texture = asset_manager.building_icons.get(building.name, asset_manager.building_icons["default"])
        super().__init__(texture=texture, width=size, height=size)
        self.planet_menu = planet_menu
        self.persistent_ui = planet_menu.persistent_ui
        self.building = building
        self.asset_manager = asset_manager

        # Overlay labels
        self.level_label = arcade.gui.UILabel(
            text=f"L{building.levels}", font_size=10, text_color=arcade.color.WHITE, 
        )
        self.level_label.with_background(color=arcade.color.CHARCOAL)
        self.productivity_label = arcade.gui.UILabel(
            text=f"${building.productivity}/w", font_size=10, text_color=arcade.color.WHITE, 
        )
        self.productivity_label.with_background(color=arcade.color.CHARCOAL)
        self.profit_label = arcade.gui.UILabel(
            text=f"${building.profit}", font_size=10, text_color=arcade.color.WHITE, 
        )
        self.profit_label.with_background(color=arcade.color.CHARCOAL)

        # Add overlays (positions: top-left, top-right, bottom-center)
        self.add(self.level_label, anchor_x="left", anchor_y="top", align_x=2, align_y=-2)
        self.add(self.productivity_label, anchor_x="right", anchor_y="top", align_x=-2, align_y=-2)
        self.add(self.profit_label, anchor_x="center", anchor_y="bottom", align_y=2)

        @self.event("on_click")
        def on_click_building(event, persistent_ui=self.persistent_ui, building=building):
            persistent_ui.show_building_gui(building)
            print(f"Clicked on {building.geography} building: {building.name}")


    def on_update(self, dt):
        # Update labels in case building stats changed
        self.level_label.text = f"L{self.building.levels}"
        self.productivity_label.text = f"${self.building.productivity}/w"
        self.profit_label.text = f"${self.building.profit}"


class DetailedBuildingWidget(arcade.gui.UIAnchorLayout):
    _restrict_child_size = True
    """A detailed building widget that's a blend of Stellaris economy tab and Victoria's building grid."""
    def __init__(self, planet_menu, building, asset_manager, width=100, height=200):
        super().__init__(width=width, height=height)
        self.width = width
        self.height = height
        self.planet_menu = planet_menu
        self.building = building
        self.asset_manager = asset_manager
        #self.with_background(color=arcade.color.DARK_SLATE_GRAY)
        self.with_background(color=arcade.color.COOL_BLACK)
        #self.with_border()
        self.root = arcade.gui.UIBoxLayout(size_hint=(1, 1))
        self.add(self.root, anchor_x="center", anchor_y="center")
        #self.root.with_background(color=arcade.color.SMOKY_BLACK)

        # name label
        self.name_label = arcade.gui.UILabel(text=building.name, font_size=12)
        self.root.add(self.name_label, anchor_x="center")

        # icon button
        texture = asset_manager.building_icons.get(building.name, asset_manager.building_icons["default"])
        self.button = arcade.gui.UITextureButton(texture=texture, width=width, height=(height / 2))
        self.root.add(self.button, anchor_x="center")

        self.level_label = arcade.gui.UILabel(
            text=f"L{building.levels}", font_size=10, text_color=arcade.color.WHITE,
        )
        self.level_label.with_background(color=arcade.color.CHARCOAL)

        self.productivity_label = arcade.gui.UILabel(
            text=f"${building.productivity}/w", font_size=10, text_color=arcade.color.WHITE,
        )
        self.productivity_label.with_background(color=arcade.color.CHARCOAL)

        # Add overlays to icon (positions: top-left, top-right, bottom-center)
        self.button.add(self.level_label, anchor_x="left", anchor_y="top", align_x=2, align_y=-2)
        self.button.add(self.productivity_label, anchor_x="right", anchor_y="top", align_x=-2, align_y=-2)

        self.workforce_bar = Progressbar2(
            value=building.staffing, width=width * 0.8, height=15, color=arcade.color.BLUE_SAPPHIRE,
        )
        self.root.add(self.workforce_bar, anchor_x="center")
        # TODO: add the numbers as text over the bar: current / max workforce

        #self.cash_reserves_bar = Progressbar2(
        #    value=building.cash_reserves, width=width * 0.8, height=15, color=arcade.color.GREEN,
        #)
        #self.root.add(self.cash_reserves_bar, anchor_x="center")
        # TODO: add the numbers as text over the bar: current / max cash reserves


        self.profit_label = arcade.gui.UILabel(
            text=f"Profit: \n ${building.profit}", font_size=10, text_color=arcade.color.WHITE, multiline=True, size_hint=(1, None),
        )
        self.root.add(self.profit_label, anchor_x="center")
        self.profit_label.with_border(color=arcade.color.STEEL_BLUE, width=1)

        profit_per_level = building.profit / building.levels if building.levels > 0 else 0
        self.profit_per_level_label = arcade.gui.UILabel(
            text=f"Prof/Lvl: \n ${profit_per_level:.2f}", font_size=10, text_color=arcade.color.WHITE, multiline=True, size_hint=(1, None),
        )
        self.root.add(self.profit_per_level_label, anchor_x="center")
        self.profit_per_level_label.with_border(color=arcade.color.STEEL_BLUE, width=1)

class DynamicGridLayout(arcade.gui.UIBoxLayout):
    """
    A dynamic grid layout: specify columns, add widgets, and it auto-creates rows as needed.
    Example: grid = DynamicGridLayout(columns=3)
    """
    def __init__(self, columns=3, vertical_spacing=2, horizontal_spacing=2, **kwargs):
        super().__init__(vertical=True, space_between=vertical_spacing, size_hint=(1, 1), **kwargs)
        self.columns = columns
        self.horizontal_spacing = horizontal_spacing
        self._current_row = None
        self._col_count = 0

    def add_to_building_grid(self, widget):
        """Add a widget to the grid, creating new rows as needed."""
        if self._current_row is None or self._col_count >= self.columns:
            # Start a new row
            min_row_height = max(widget.height, 100)
            self._current_row = arcade.gui.UIBoxLayout(
                vertical=False, space_between=self.horizontal_spacing, size_hint=(1, None), height=min_row_height
            )
            super().add(self._current_row)
            #self.with_border()
            self._col_count = 0
        self._current_row.add(widget)
        self._col_count += 1
        self.fit_content()

    def clear(self):
        super().clear()
        self._current_row = None
        self._col_count = 0


class BuildingGrid(DynamicGridLayout):
    """A grid layout to display all detailed building widgets of a given type (urban, rural, government)."""
    def __init__(self, planet_menu, building_type, asset_manager):
        super().__init__(columns=3)
        self.planet_menu = planet_menu
        self.building_type = building_type  # "Urban", "Rural", or "Government"
        self.buildings = [b for b in planet_menu.planet.buildings if b.geography == building_type]
        self.asset_manager = asset_manager
        self.with_background(color=arcade.color.DARK_SLATE_GRAY)
        self.construct_building_button = arcade.gui.UIFlatButton(text="Add Urban Building", size_hint=(1, 1), multiline=True)
        self.construct_building_button.with_background(color=arcade.color.BLACK)

        for building in self.buildings:
            widget = DetailedBuildingWidget(planet_menu, building, asset_manager)
            self.add_to_building_grid(widget)

        self.add_to_building_grid(self.construct_building_button)  # Add construct button after each building for demo


class PlanetInterface:
    """Deprecated: A UI manager for the planet menu, handling opening, closing, and tab switching."""

    def __init__(self, model):
        self.model = model
        self.planet = None  # Will be set to a Colony
        self.nation = None
        self.manager = arcade.gui.UIManager()
        self.current_tab = "Summary"

        # Main window (centered, half screen)
        self.window = arcade.gui.UIAnchorLayout(size_hint=(0.5, 0.7))
        self.manager.add(self.window)

        # Layout for the whole menu
        self.layout = arcade.gui.UIBoxLayout(vertical=True, size_hint=(1, 1))
        self.layout.with_background(color=arcade.color.DARK_SLATE_GRAY)
        self.window.add(self.layout)

        # Top bar (planet name, type, close button)
        self.top_bar = arcade.gui.UIBoxLayout(vertical=False, size_hint=(1, 0.08))
        self.planet_label = arcade.gui.UILabel(text="Planet Name", font_size=18)
        self.planet_type_label = arcade.gui.UILabel(text="Type", font_size=14)
        self.close_button = arcade.gui.UIFlatButton(text="X", width=30)
        self.close_button.on_click = self.close_menu
        self.top_bar.add(self.planet_label)
        self.top_bar.add(self.planet_type_label)
        self.top_bar.add(self.close_button)
        self.layout.add(self.top_bar)

        # Tab buttons
        self.tab_bar = arcade.gui.UIBoxLayout(vertical=False, size_hint=(1, 0.07))
        self.summary_tab_btn = arcade.gui.UIFlatButton(text="Summary", width=100)
        self.summary_tab_btn.on_click = lambda event: self.switch_tab("Summary")
        self.buildings_tab_btn = arcade.gui.UIFlatButton(text="Buildings", width=100)
        self.buildings_tab_btn.on_click = lambda event: self.switch_tab("Buildings")
        self.population_tab_btn = arcade.gui.UIFlatButton(text="Population", width=100)
        self.population_tab_btn.on_click = lambda event: self.switch_tab("Population")
        self.tab_bar.add(self.summary_tab_btn)
        self.tab_bar.add(self.buildings_tab_btn)
        self.tab_bar.add(self.population_tab_btn)
        self.layout.add(self.tab_bar)

        # Main content area (changes with tab)
        self.content_frame = arcade.gui.UIAnchorLayout(size_hint=(1, 0.85))
        self.content_frame.with_background(color=arcade.color.LIGHT_GRAY)
        self.layout.add(self.content_frame)

        self.update_content()

    def close_menu(self, event=None):
        # Hide or destroy the menu (implementation depends on your view system)
        self.manager.disable()
        # Optionally: remove from parent, or set a flag
        # You can expand this as needed
        pass

    def switch_tab(self, tab):
        self.current_tab = tab
        self.update_content()

    def update_content(self):
        self.content_frame.clear()
        if self.current_tab == "Summary":
            self.show_summary_tab()
        elif self.current_tab == "Buildings":
            self.show_buildings_tab()
        elif self.current_tab == "Population":
            self.show_population_tab()

    def show_summary_tab(self):
        # Example: show key stats for the colony
        box = arcade.gui.UIBoxLayout(vertical=True, size_hint=(1, 1))
        if self.planet:
            box.add(arcade.gui.UILabel(text=f"Population: {self.planet.total_population}"))
            box.add(arcade.gui.UILabel(text=f"Stability: {self.planet.stability}"))
            box.add(arcade.gui.UILabel(text=f"Buildings: {len(self.planet.buildings)}"))
        else:
            box.add(arcade.gui.UILabel(text="No planet selected."))
        self.content_frame.add(box)

    def show_buildings_tab(self):
        # Example: show a list of buildings
        box = arcade.gui.UIBoxLayout(vertical=True, size_hint=(1, 1))
        if self.planet and self.planet.buildings:
            for building in self.planet.buildings:
                box.add(arcade.gui.UILabel(text=f"{building.name} (Level {building.levels})"))
        else:
            box.add(arcade.gui.UILabel(text="No buildings present."))
        self.content_frame.add(box)

    def show_population_tab(self):
        # Example: show a list of pops
        box = arcade.gui.UIBoxLayout(vertical=True, size_hint=(1, 1))
        if self.planet and self.planet.pops:
            for pop in self.planet.pops:
                job = pop.current_job.profession if pop.current_job else "Unemployed"
                box.add(arcade.gui.UILabel(text=f"Pop Size: {pop.size} | Job: {job}"))
        else:
            box.add(arcade.gui.UILabel(text="No pops present."))
        self.content_frame.add(box)

    def buildings_tab(self):
        pass

    def population_tab(self):
        pass

    def set_planet(self, colony):
        self.planet = colony
        # Update top bar labels
        self.planet_label.text = getattr(colony, 'name', 'Planet')
        self.planet_type_label.text = getattr(getattr(colony, 'planet', None), 'type', 'Type')
        self.current_tab = "Summary"
        self.manager.enable()
        self.update_content()

    def draw(self):
        if self.manager._enabled:
            self.manager.draw()


################################### GUI CONSTRUCTS ###################################
# stupid circular imports. gotta fix later

class ProgressBar1(arcade.gui.UIWidget):
    """A custom progress bar widget.

    A UIWidget is a basic building block for GUI elements. It is a rectangle with a
    background color and can have children.

    To create a custom progress bar, we create a UIWidget with a black background,
    set a border and add a `do_render` method to draw the actual progress bar.

    """

    value = arcade.gui.Property(0.0)
    """The fill level of the progress bar. A value between 0 and 1."""

    def __init__(
        self,
        *,
        value: float = 1.0,
        width=100,
        height=20,
        color = arcade.color.GREEN,
    ) -> None:
        super().__init__(
            width=width,
            height=height,
            size_hint=None,  # disable size hint, so it just uses the size given
        )
        self.with_background(color=arcade.uicolor.GRAY_CONCRETE)
        self.with_border(color=arcade.uicolor.BLACK)

        self.value = value
        self.color = color

        # trigger a render when the value changes
        arcade.gui.bind(self, "value", self.trigger_render)

    def do_render(self, surface: arcade.gui.Surface) -> None:
        """Draw the actual progress bar."""
        # this will set the viewport to the size of the widget
        # so that 0,0 is the bottom left corner of the widget content
        self.prepare_render(surface)

        # Draw the actual bar
        arcade.draw_lbwh_rectangle_filled(
            0,
            0,
            self.content_width * self.value,
            self.content_height,
            self.color,
        )

class Progressbar2(arcade.gui.UIAnchorLayout):
    value = arcade.gui.Property(0.0)

    def __init__(
            self,
            value: float = 1.0,
            width=100,
            height=20,
            color=arcade.color.GREEN,
    ) -> None:
        super().__init__(
            width=width,
            height=height,
            size_hint=None,  # disable size hint, so it just uses the size given
        )
        self.with_background(color=arcade.uicolor.GRAY_CONCRETE)
        self.with_border(color=arcade.uicolor.BLACK)

        self._bar = arcade.gui.UISpace(
            color=color,
            size_hint=(value, 1),
        )
        self.add(
            self._bar,
            anchor_x="left",
            anchor_y="top",
        )
        self.value = value

        # update the bar when the value changes
        arcade.gui.bind(self, "value", self._update_bar)

    def _update_bar(self):
        self._bar.size_hint = (self.value, 1)
        self._bar.visible = self.value > 0


class BuildingGUI(GenericMenu):
    """
    GUI for displaying building information and management options.
    For the first draft, this will simply imitate Victora 3's building UI.
    """

    def __init__(self, persistent_ui, asset_manager, *args, **kwargs):
        super().__init__(asset_manager, *args, **kwargs)
        print("BuildingGUI initialized")
        self.building = None
        self.persistent_ui = persistent_ui
        self.asset_manager = asset_manager
        self.content_frame.with_background(color=arcade.color.DARK_SLATE_GRAY)
        self.window.size_hint = (0.3, 0.6)
        self.window.center_x = 600

        self.info_column = arcade.gui.UIBoxLayout(size_hint=(1, 1), vertical=True, space_between=10)
        self.content_frame.add(self.info_column)

    def setup_content(self):
        self.info_column.clear()
        # Building Name
        self.title_label.text = self.building.name

        # --- Box 1: --- Icon, Cash reseves, staffing, and productivity ---
        box1 = arcade.gui.UIAnchorLayout(size_hint=(1, 0.2))
        box1.with_background(color=arcade.color.DARK_BLUE_GRAY)
        box1.with_border()

        icon_texture = self.asset_manager.building_icons.get(self.building.name,
                                                             self.asset_manager.building_icons["default"])
        building_icon = arcade.gui.UIImage(texture=icon_texture, width=64, height=64)
        self.staffing_bar = Progressbar2(value=self.building.staffing)
        #self.cash_reserves_bar = Progressbar2(value=self.building.cash_reserves)
        productivity_chart = arcade.gui.UILabel(text=f"Productivity: {self.building.productivity}", font_size=14)
        box1.add(building_icon, anchor_x="left", anchor_y="center", align_x=10)
        box1.add(self.staffing_bar, anchor_x="center", anchor_y="center")
        #box1.add(self.cash_reserves_bar, anchor_x="center", anchor_y="center")
        box1.add(productivity_chart, anchor_x="right", anchor_y="center", align_x=-10)
        self.info_column.add(box1)

        # --- Box 2: --- Production Process ---
        box2 = arcade.gui.UIBoxLayout(size_hint=(1, 0.4), vertical=False)
        box2.with_background(color=arcade.color.DARK_BLUE_GRAY)
        box2.with_border()

        #production_label = arcade.gui.UILabel(text="Production Process:", font_size=16)

        # Input Goods and Wages
        input_box = arcade.gui.UIBoxLayout(size_hint=(0.5, 1), vertical=True, space_between=5)
        input_label = arcade.gui.UILabel(text="Inputs:", font_size=14)
        input_box.add(input_label)
        for input_good, amount in self.building.inputs.items():
            good_icon = self.asset_manager.resource_icons.get(input_good, self.asset_manager.resource_icons["default"])
            good_widget = arcade.gui.UIBoxLayout(size_hint=(1, 0.2), vertical=False, space_between=5)
            good_widget.with_border()
            icon_image = arcade.gui.UIImage(texture=good_icon, width=32, height=32)
            #good_name = arcade.gui.UILabel(text=f"{input_good}: {amount} for ${cost}", font_size=12)
            good_widget.add(icon_image)
            #good_widget.add(good_name)
            input_box.add(good_widget)
        wages_label = arcade.gui.UILabel(text=f"Wages per cycle: ${self.building.balance_sheet["expenses"]["wages"]:.2f}",
                                         font_size=12)
        input_box.add(wages_label)

        # Output Goods
        output_box = arcade.gui.UIBoxLayout(size_hint=(0.5, 1), vertical=True, space_between=5)
        output_label = arcade.gui.UILabel(text="Outputs:", font_size=14)
        output_box.add(output_label)
        for output_good, amount in self.building.outputs.items():
            good_icon = self.asset_manager.resource_icons.get(output_good, self.asset_manager.resource_icons["default"])
            good_widget = arcade.gui.UIBoxLayout(size_hint=(1, 0.2), vertical=False, space_between=5)
            good_widget.with_border()
            icon_image = arcade.gui.UIImage(texture=good_icon, width=32, height=32)
            good_name = arcade.gui.UILabel(text=f"{output_good}: {amount}", font_size=12)
            good_widget.add(icon_image)
            good_widget.add(good_name)
            output_box.add(good_widget)
        balance_label = arcade.gui.UILabel(text=f"Profit per cycle: ${self.building.profit}", font_size=12)
        output_box.add(balance_label)
        #throughput_label = arcade.gui.UILabel(text=f"Throughput: {self.building.get_throughput():.1f} units/cycle", font_size=12)
        #output_box.add(throughput_label)

        box2.add(input_box)
        box2.add(output_box)
        #box2.add(production_label, anchor_x="center", anchor_y="top", align_y=-10)
        self.info_column.add(box2)

        # --- Box 3: --- Ownership and Upgrades ---
        box3 = arcade.gui.UIBoxLayout(size_hint=(1, 0.2), vertical=False, space_between=10)
        box3.with_background(color=arcade.color.DARK_BLUE_GRAY)
        box3.with_border()

        #owner_label = arcade.gui.UILabel(text=f"Owner: {self.building.owner.name}", font_size=14)
        #upgrade_label = arcade.gui.UILabel(text=f"Upgrades: {len(self.building.upgrades)}/{self.building.max_upgrades}", font_size=14)
        #box3.add(owner_label)
        #box3.add(upgrade_label)
        self.info_column.add(box3)

    def on_daily_update(self):
        if self.manager.enable and self.building:
            pass  # For future daily updates if needed

    def open_window(self, building):
        self.building = building
        self.title_label.text = f"Building: {building.name}"
        self.setup_content()
        self.manager.enable()
