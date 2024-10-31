import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import numpy as np

class CircleVisualization:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualisasi Lingkaran")
        self.center_x = tk.DoubleVar(value=0.0)
        self.center_y = tk.DoubleVar(value=0.0)
        self.radius = tk.DoubleVar(value=5.0)
        self.radius_entry_var = tk.StringVar(value=str(self.radius.get()))
        self.pi_value = np.pi
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.create_controls()
        self.create_canvas()
        self.update_circle()  

    def create_controls(self):
        ttk.Label(self.control_frame, text="Titik Tengah X:").pack(pady=5)
        self.center_x_entry = ttk.Entry(
            self.control_frame,
            textvariable=self.center_x
        )
        self.center_x_entry.pack(pady=5)
        ttk.Label(self.control_frame, text="Titik Tengah Y:").pack(pady=5)
        self.center_y_entry = ttk.Entry(
            self.control_frame,
            textvariable=self.center_y
        )
        self.center_y_entry.pack(pady=5)
        ttk.Label(self.control_frame, text="Radius:").pack(pady=5)
        self.radius_slider = ttk.Scale(
            self.control_frame,
            from_=1,
            to=100,
            orient='horizontal',
            variable=self.radius,
            command=self.on_radius_slider_change
        )
        self.radius_slider.pack(pady=5)
        self.radius_entry = ttk.Entry(
            self.control_frame,
            textvariable=self.radius_entry_var
        )
        self.radius_entry.pack(pady=5)
        self.radius_entry.bind("<Return>", self.on_radius_entry_change)
        self.update_button = ttk.Button(
            self.control_frame,
            text="Perbarui Lingkaran",
            command=self.update_circle
        )
        self.update_button.pack(pady=10)
        self.radius_label = ttk.Label(
            self.control_frame,
            text=f"Radius: {self.radius.get():.2f}"
        )
        self.radius_label.pack(pady=5)
        self.diameter_label = ttk.Label(
            self.control_frame,
            text=f"Diameter: {self.get_diameter():.2f}"
        )
        self.diameter_label.pack(pady=5)
        self.circumference_label = ttk.Label(
            self.control_frame,
            text=f"Keliling: {self.get_circumference():.2f}"
        )
        self.circumference_label.pack(pady=5)
        self.pi_ratio_label = ttk.Label(
            self.control_frame,
            text=f"Rasio Pi (Keliling/Diameter): {self.get_pi_ratio():.5f}"
        )
        self.pi_ratio_label.pack(pady=5)

    def create_canvas(self):
        self.figure, self.ax = plt.subplots(figsize=(6, 6))
        self.ax.set_xlim(-15, 15)
        self.ax.set_ylim(-15, 15)
        self.ax.set_aspect('equal')
        self.ax.axhline(0, color='black', lw=1)
        self.ax.axvline(0, color='black', lw=1)
        self.ax.grid(True)
        self.circle_patch = plt.Circle(
            (self.center_x.get(), self.center_y.get()),
            radius=self.radius.get(),
            fill=False,
            lw=2
        )
        self.ax.add_patch(self.circle_patch)
        self.pi_segment = Wedge(
            center=(self.center_x.get(), self.center_y.get()),
            r=self.radius.get(),
            theta1=0,
            theta2=(self.get_pi_ratio() / np.pi) * 360,
            width=0.05,
            facecolor='orange',
            alpha=0.5
        )
        self.ax.add_patch(self.pi_segment)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.canvas_frame)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)

    def get_diameter(self):
        return self.radius.get() * 2

    def get_circumference(self):
        return self.pi_value * self.get_diameter()

    def get_pi_ratio(self):
        return self.get_circumference() / self.get_diameter()

    def update_texts(self):
        self.radius_label.config(
            text=f"Radius: {self.radius.get():.2f}"
        )
        self.diameter_label.config(
            text=f"Diameter: {self.get_diameter():.2f}"
        )
        self.circumference_label.config(
            text=f"Keliling: {self.get_circumference():.2f}"
        )
        self.pi_ratio_label.config(
            text=f"Rasio Pi (Keliling/Diameter): {self.get_pi_ratio():.5f}"
        )
        self.radius_entry_var.set(f"{self.radius.get():.2f}")

    def update_circle(self):
        center_x = self.center_x.get()
        center_y = self.center_y.get()
        radius = self.radius.get()
        self.circle_patch.center = (center_x, center_y)
        self.circle_patch.set_radius(radius)
        color_value = min(1.0, radius / 10)
        self.circle_patch.set_edgecolor((1 - color_value, 0, color_value))
        self.pi_segment.center = (center_x, center_y)
        self.pi_segment.set_radius(radius)
        self.pi_segment.theta2 = (self.get_pi_ratio() / np.pi) * 360
        self.update_texts()
        self.canvas.draw()

    def on_radius_slider_change(self, event):
        self.radius_entry_var.set(f"{self.radius.get():.2f}")
        self.update_texts()
        self.update_circle()

    def on_radius_entry_change(self, event):
        try:
            value = float(self.radius_entry_var.get())
            if 1 <= value <= 10:
                self.radius.set(value)
                self.radius_slider.set(value)
                self.update_texts()
                self.update_circle()
            else:
                self.radius_entry_var.set(f"{self.radius.get():.2f}")
        except ValueError:
            self.radius_entry_var.set(f"{self.radius.get():.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CircleVisualization(root)
    root.mainloop()
