import arcade
import arcade.gui


#from views.UI_stuff.building_gui import BuildingGUI

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

    def update(self):
        pass

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

    def open_window(self, colony):
        self.planet = colony
        self.title_label.text = getattr(colony, 'name', 'Planet')
        self.show_summary_tab()
        self.manager.enable()

    def show_summary_tab(self):
        self.content_frame.clear()  # Clear previous content
        grid = arcade.gui.UIGridLayout(size_hint=(1, 1), row_count=3, column_count=4, )
        grid.with_background(color=arcade.color.CHARCOAL)

        # --- Box 1 --- Primary planet art and info with governor portrait and name
        box1 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Primary planet art and info
        #climate = self.planet.planet.climate if self.planet and self.planet.planet else "not_implemented"
        climate = self.planet.planet.climate if self.planet else "continental"
        print(f"Planet climate for menu: {climate}")
        climate_background = self.asset_manager.ui_art.get(climate, self.asset_manager.ui_art["default"])
        box1.with_background(texture=climate_background)
        box1.with_border()
        grid.add(box1, row=0, column=0, column_span=3)

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

        # --- Box 2 --- Buildings overview
        box2 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Buildings overview
        box2.with_border()
        grid.add(box2, row=1, column=0, column_span=2, row_span=2)

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
                urban_buildings.add(BuildingWidget(self, building, self.asset_manager, size=100))

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
                rural_buildings.add(BuildingWidget(self, building, self.asset_manager, size=100))

        rural_box.add(rural_label, anchor_y="top")
        rural_box.add(rural_buildings, anchor_y="center", anchor_x="center")
        box2.add(rural_box, anchor_y="bottom")

        # --- Box 3 --- Celestial body info
        box3 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # celestial body info
        box3.with_border()
        box3.with_background(
            texture=self.asset_manager.ui_art.get("solar_system_background", self.asset_manager.ui_art["default"]))
        grid.add(box3, row=0, column=3)

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
        box4 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Local market info
        box4.with_border()
        grid.add(box4, row=1, column=2, row_span=2)

        market_label = arcade.gui.UILabel(text="Local Market")
        box4.add(market_label, anchor_y="top")

        # --- Box 5 --- Build queue
        box5 = arcade.gui.UIAnchorLayout(size_hint=(1, 1))  # Build queue
        box5.with_border()
        grid.add(box5, row=1, column=3, row_span=2)

        build_queue_label = arcade.gui.UILabel(text="Build Queue")
        box5.add(build_queue_label, anchor_y="top")

        self.content_frame.add(grid)

    def on_daily_update(self):
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
        def on_click_building(event):
            print(f"Building {self.building.name} clicked!")
            self.planet_menu.content_frame.clear()
            building_gui = BuildingGUI(self.asset_manager)
            building_gui.open_window(self.building)

    def on_update(self, dt):
        # Update labels in case building stats changed
        self.level_label.text = f"L{self.building.levels}"
        self.productivity_label.text = f"${self.building.productivity}/w"
        self.profit_label.text = f"${self.building.profit}"


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

    def __init__(self, asset_manager, *args, **kwargs):
        super().__init__(asset_manager=asset_manager, *args, **kwargs)
        print("BuildingGUI initialized")
        self.building = None
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
        if self.manager.enabled and self.building:
            pass  # For future daily updates if needed

    def open_window(self, building):
        self.building = building
        self.title_label.text = f"Building: {building.name}"
        self.setup_content()
        self.manager.enable()
