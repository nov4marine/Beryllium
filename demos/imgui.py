import arcade
from imgui_bundle import imgui
from imgui_bundle.python_backends import pyglet_backend

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "Arcade + ImGui")
        # Initialize ImGui
        imgui.create_context()
        # The PygletRenderer bridges Arcade's window with ImGui
        self.imgui_renderer = pyglet_backend.create_renderer(self)

        
        self.player_x = 400

    def on_draw(self):
        self.clear()
        
        # 1. Draw your game normally
        arcade.draw_circle_filled(self.player_x, 300, 20, arcade.color.BLUE)
        
        # 2. Start ImGui Frame
        imgui.new_frame()
        
        # 3. Define ImGui UI
        imgui.begin("Debug Menu")
        imgui.text("Move the player:")
        # imgui.slider_int returns (changed, value)
        changed, self.player_x = imgui.slider_int("Player X", self.player_x, 0, 800)
        if imgui.button("Reset Position"):
            self.player_x = 400
        imgui.end()
        
        # 4. Render ImGui to the screen
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

if __name__ == "__main__":
    game = MyGame()
    arcade.run()

