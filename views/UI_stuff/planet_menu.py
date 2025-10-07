import arcade
import arcade.gui


class PlanetInterface:
    def __init__(self, model, nation):
        self.model = model
        self.planet = None  # Will be set to a Colony
        self.nation = nation
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
        self.update_content()

    def on_draw(self):
        self.manager.draw()

