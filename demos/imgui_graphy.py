import arcade
import random
import numpy as np
from imgui_bundle import imgui, implot
#from imgui_bundle.python_backends.pyglet_backend import PygletRenderer
from imgui_bundle.python_backends import pyglet_backend

class StellarisClone(arcade.Window):
    def __init__(self):
        super().__init__(1000, 700, "Economy Simulator", resizable=True)
        
        # 1. Setup ImGui
        imgui.create_context()
        implot.create_context() # Important: ImPlot needs its own context!
        self.imgui_renderer = pyglet_backend.create_renderer(self)

        # 2. Fake Market Data
        self.time_steps = list(range(100))
        self.grain_prices = [20.0]
        for _ in range(99):
            # Simple random walk to simulate market fluctuation
            self.grain_prices.append(self.grain_prices[-1] + random.uniform(-1, 1))

    def on_draw(self):
        self.clear()
        
        # --- Draw Game World (The "Map") ---
        arcade.draw_text("Space Map (Arcade)", 400, 350, arcade.color.DARK_GRAY, 20)
        arcade.draw_circle_outline(500, 350, 200, arcade.color.BATTLESHIP_GREY)

        # --- Draw UI (ImGui) ---
        imgui.new_frame()

        # Window for the Ledger
        imgui.begin("Galactic Market")
        imgui.text("Current Commodity: Grain")

        # Convert lists to numpy arrays for plotting
        xs = np.array(self.time_steps)
        ys = np.array(self.grain_prices)
        
        # Victoria 3 style graph using ImPlot
        if implot.begin_plot("Price History"):
            # Arguments: Label, X-axis list, Y-axis list
            implot.plot_line("Market Value", ys)
            implot.end_plot()
            
        if imgui.button("Buy Grain"):
            print("Trade executed!")
            self.grain_prices.append(self.grain_prices[-1] + random.uniform(-1, 1))

            
        imgui.end()
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

if __name__ == "__main__":
    game = StellarisClone()
    arcade.run()