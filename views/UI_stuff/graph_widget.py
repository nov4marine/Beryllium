import arcade
import arcade.gui

class GraphWidget(arcade.gui.UIAnchorLayout):
    """
    This is a chat gpt template for a line graph as a gui widget. After combing through it a bit, it is surprisingly 
    robust, and probably would work as-is. However, it can definitely be improved:
    1. subclassing for more flexibility 
    2. replace draw_text with text sprites or arcade.Text objects. 
    3. extend axis ticks into grid lines
    4. make the number of data points more flexible on both axes
    5. currently only supports linear scaling, and only line graphs (though to be fair, that's gonna be like 90% of use cases)
    Immediate TODO: draw_text -> arcade.Text objects
    """
    def __init__(self, width=320, height=180, title="Graph", y_label="", x_label="", max_points=100, *args, **kwargs):
        super().__init__(width=width, height=height, *args, **kwargs)
        self.width = width
        self.height = height
        self.title = title
        self.y_label = y_label
        self.x_label = x_label
        self.data_series = {}  # {name: [values]}
        self.colors = {}       # {name: (r, g, b)}
        self.max_points = max_points

        # Padding for axes and labels
        self.left_pad = 48
        self.right_pad = 16
        self.top_pad = 32
        self.bottom_pad = 32

    def add_series(self, name, color=(0, 200, 0)):
        self.data_series[name] = []
        self.colors[name] = color

    def add_point(self, name, value):
        if name in self.data_series:
            self.data_series[name].append(value)
            if len(self.data_series[name]) > self.max_points:
                self.data_series[name].pop(0)

    def _get_axis_bounds(self):
        # Find min/max for y axis across all series
        all_values = [v for values in self.data_series.values() for v in values]
        if not all_values:
            return 0, 1
        min_y = min(all_values)
        max_y = max(all_values)
        if min_y == max_y:
            min_y -= 1
            max_y += 1
        return min_y, max_y

    def on_draw(self):
        # Draw background
        arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, (30, 30, 30, 220))

        # Draw axes
        plot_left = self.left_pad
        plot_right = self.width - self.right_pad
        plot_top = self.height - self.top_pad
        plot_bottom = self.bottom_pad

        # Axes lines
        arcade.draw_line(plot_left, plot_bottom, plot_left, plot_top, arcade.color.LIGHT_GRAY, 2)
        arcade.draw_line(plot_left, plot_bottom, plot_right, plot_bottom, arcade.color.LIGHT_GRAY, 2)

        # Axis bounds
        min_y, max_y = self._get_axis_bounds()
        y_range = max_y - min_y if max_y != min_y else 1

        # Draw y-axis ticks and labels
        num_y_ticks = 5
        for i in range(num_y_ticks + 1):
            y_val = min_y + (y_range * i / num_y_ticks)
            y_pos = plot_bottom + (plot_top - plot_bottom) * i / num_y_ticks
            arcade.draw_line(plot_left - 5, y_pos, plot_left, y_pos, arcade.color.LIGHT_GRAY, 1)
            arcade.draw_text(f"{y_val:.1f}", plot_left - 10, y_pos - 8, arcade.color.LIGHT_GRAY, 10, anchor_x="right")

        # Draw x-axis ticks and labels
        max_len = max((len(values) for values in self.data_series.values()), default=0)
        num_x_ticks = min(10, max_len - 1) if max_len > 1 else 1
        for i in range(num_x_ticks + 1):
            if num_x_ticks == 0:
                continue
            x_idx = int(i * (self.max_points - 1) / num_x_ticks)
            x_pos = plot_left + (plot_right - plot_left) * i / num_x_ticks
            arcade.draw_line(x_pos, plot_bottom, x_pos, plot_bottom - 5, arcade.color.LIGHT_GRAY, 1)
            arcade.draw_text(f"{x_idx}", x_pos, plot_bottom - 20, arcade.color.LIGHT_GRAY, 10, anchor_x="center")

        # Draw data series
        for name, values in self.data_series.items():
            if len(values) < 2:
                continue
            color = self.colors[name]
            points = []
            for i, v in enumerate(values):
                x = plot_left + (plot_right - plot_left) * i / (self.max_points - 1)
                y = plot_bottom + (plot_top - plot_bottom) * ((v - min_y) / y_range if y_range else 0)
                points.append((x, y))
            arcade.draw_line_strip(points, color, 2)

        # Draw title and axis labels
        arcade.draw_text(self.title, self.width // 2, self.height - 20, arcade.color.WHITE, 14, anchor_x="center")
        if self.y_label:
            arcade.draw_text(self.y_label, 8, (plot_top + plot_bottom) // 2, arcade.color.LIGHT_GRAY, 12, anchor_x="left", anchor_y="center", rotation=90)
        if self.x_label:
            arcade.draw_text(self.x_label, (plot_left + plot_right) // 2, 8, arcade.color.LIGHT_GRAY, 12, anchor_x="center")

        # Optionally: draw legend
        legend_y = self.height - 18
        legend_x = plot_right - 10
        for name, color in self.colors.items():
            arcade.draw_rectangle_filled(legend_x, legend_y, 12, 12, color)
            arcade.draw_text(name, legend_x - 4, legend_y - 7, arcade.color.LIGHT_GRAY, 10, anchor_x="right")
            legend_y -= 16

    def draw(self):
        self.on_draw()

# Example usage:
# graph = GraphWidget(title="Mineral Price", y_label="Price", x_label="Month")
# graph.add_series("Minerals", color=(255, 215, 0))
# graph.add_point("Minerals", 10.5)
# self.content_frame.add(graph)
