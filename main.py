import tkinter as tk
from tkinter import ttk, font as tkFont # Import font
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import numpy as np

class CircleVisualization:
    """
    A Tkinter application for visualizing a circle and its properties,
    allowing users to interactively change its center coordinates and radius.
    The application demonstrates geometric concepts like diameter, circumference,
    and the ratio Pi, with smooth animations for radius changes.
    """
    # --- Color Palette and Font ---
    BG_COLOR = "#F0F0F0"
    TEXT_COLOR = "#333333"
    ACCENT_COLOR = "#007ACC"
    ACCENT_LIGHT_FILL = "#E6F2FF" # Light shade for circle fill (optional)
    PI_SEGMENT_COLOR = "#005C99" # Darker shade of accent for Pi segment
    FONT_FAMILY = "Arial"
    FONT_SIZE = 10

    def __init__(self, root):
        self.root = root
        self.root.title("Visualisasi Lingkaran")
        self.root.configure(bg=self.BG_COLOR)

        # --- Define Font ---
        self.default_font = tkFont.Font(family=self.FONT_FAMILY, size=self.FONT_SIZE)

        # --- Style ttk Widgets ---
        style = ttk.Style()
        style.theme_use('clam') # Using a theme that allows more customization

        style.configure("TFrame", background=self.BG_COLOR)
        style.configure(
            "TLabel",
            foreground=self.TEXT_COLOR,
            background=self.BG_COLOR,
            font=self.default_font
        )
        style.configure(
            "TButton",
            foreground="white", # Button text color
            background=self.ACCENT_COLOR,
            font=self.default_font,
            padding=5
        )
        style.map(
            "TButton",
            background=[('active', '#005C99')] # Darker shade when active/pressed
        )
        style.configure(
            "TEntry",
            fieldbackground="white", # Entry field background
            foreground=self.TEXT_COLOR,
            insertcolor=self.TEXT_COLOR, # Cursor color
            font=self.default_font
        )
        # For TScale, horizontal and vertical styles might need separate configuration
        style.configure("Horizontal.TScale", background=self.BG_COLOR)


        self.center_x = tk.DoubleVar(value=0.0)
        self.center_y = tk.DoubleVar(value=0.0)
        self.radius = tk.DoubleVar(value=5.0) # This will store the TARGET radius
        self.radius_entry_var = tk.StringVar(value=str(self.radius.get()))
        self.pi_value = np.pi

        # --- Animation Attributes ---
        self.current_display_radius = tk.DoubleVar(value=self.radius.get()) # Actual displayed radius
        self.is_animating_radius = False
        self.animation_job_id = None
        self.ANIMATION_DELAY_MS = 15 # ms between animation frames
        self.ANIMATION_STEP_SIZE = 0.05 # Multiplier for change per frame (e.g., 5% of remaining difference)
        self.ANIMATION_THRESHOLD = 0.01 # If difference is less than this, snap to target

        self.control_frame = ttk.Frame(self.root, style="TFrame")
        self.control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas_frame = ttk.Frame(self.root, style="TFrame")
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_controls()
        self.create_canvas()
        self.update_circle()

    def create_controls(self):
        # Group for Input Controls
        input_controls_frame = ttk.Frame(self.control_frame, style="TFrame")
        input_controls_frame.pack(fill=tk.X, pady=(0,5)) # Add some padding below the group

        ttk.Label(input_controls_frame, text="Titik Tengah X:").pack(pady=(5,2), anchor=tk.W)
        self.center_x_entry = ttk.Entry(
            input_controls_frame,
            textvariable=self.center_x,
            font=self.default_font
        )
        self.center_x_entry.pack(pady=(0,5), fill=tk.X, padx=2)
        
        ttk.Label(input_controls_frame, text="Titik Tengah Y:").pack(pady=(5,2), anchor=tk.W)
        self.center_y_entry = ttk.Entry(
            input_controls_frame,
            textvariable=self.center_y,
            font=self.default_font
        )
        self.center_y_entry.pack(pady=(0,5), fill=tk.X, padx=2)
        
        ttk.Label(input_controls_frame, text="Radius:").pack(pady=(5,2), anchor=tk.W)
        self.radius_slider = ttk.Scale(
            input_controls_frame,
            from_=1,
            to=100,
            orient='horizontal',
            variable=self.radius,
            command=self.on_radius_control_changed,
            style="Horizontal.TScale"
        )
        self.radius_slider.pack(pady=(0,5), fill=tk.X, padx=2)
        
        self.radius_entry = ttk.Entry(
            input_controls_frame,
            textvariable=self.radius_entry_var,
            font=self.default_font
        )
        self.radius_entry.pack(pady=(0,10), fill=tk.X, padx=2) # More padding after radius entry
        self.radius_entry.bind("<Return>", self.on_radius_entry_submitted)
        
        # Update Button - Centered
        button_frame = ttk.Frame(self.control_frame, style="TFrame")
        button_frame.pack(fill=tk.X, pady=5)
        self.update_button = ttk.Button(
            button_frame,
            text="Perbarui Lingkaran",
            command=self.on_update_button_pressed,
            style="TButton"
        )
        self.update_button.pack(pady=(5,10)) # pady for the button itself

        # Separator
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # Group for Calculated Values
        calculated_values_frame = ttk.Frame(self.control_frame, style="TFrame")
        calculated_values_frame.pack(fill=tk.X, pady=(5,0))

        self.radius_label = ttk.Label(
            calculated_values_frame,
            text=f"Radius: {self.radius.get():.2f}"
        )
        self.radius_label.pack(pady=3, anchor=tk.W)
        
        self.diameter_label = ttk.Label(
            calculated_values_frame,
            text=f"Diameter: {self.get_diameter():.2f}"
        )
        self.diameter_label.pack(pady=3, anchor=tk.W)
        
        self.circumference_label = ttk.Label(
            calculated_values_frame,
            text=f"Keliling: {self.get_circumference():.2f}"
        )
        self.circumference_label.pack(pady=3, anchor=tk.W)
        
        self.pi_ratio_label = ttk.Label(
            calculated_values_frame,
            text=f"Rasio Pi (Keliling/Diameter): {self.get_pi_ratio():.5f}"
        )
        self.pi_ratio_label.pack(pady=3, anchor=tk.W)

    def create_canvas(self):
        self.figure, self.ax = plt.subplots(figsize=(6, 6))
        self.figure.patch.set_facecolor(self.BG_COLOR) # Figure background
        self.ax.set_facecolor(self.BG_COLOR) # Axes background

        self.ax.set_xlim(-15, 15)
        self.ax.set_ylim(-15, 15)
        self.ax.set_aspect('equal')
        
        # Axis and grid colors
        axis_color = self.TEXT_COLOR # Or a slightly lighter gray
        grid_color = '#CCCCCC' # Light gray for grid
        self.ax.axhline(0, color=axis_color, lw=0.8)
        self.ax.axvline(0, color=axis_color, lw=0.8)
        self.ax.grid(True, color=grid_color, linestyle='--', linewidth=0.5)

        # Tick label colors
        self.ax.tick_params(axis='x', colors=self.TEXT_COLOR)
        self.ax.tick_params(axis='y', colors=self.TEXT_COLOR)

        # Spine colors (borders of the plot)
        for spine in self.ax.spines.values():
            spine.set_edgecolor(axis_color)

        self.circle_patch = plt.Circle(
            (self.center_x.get(), self.center_y.get()),
            radius=self.radius.get(),
            fill=False, # Keeping fill transparent for now, can use ACCENT_LIGHT_FILL
            # edgecolor=self.ACCENT_COLOR, # Initial edge color, will be updated
            lw=2
        )
        self.ax.add_patch(self.circle_patch)
        
        self.pi_segment = Wedge(
            center=(self.center_x.get(), self.center_y.get()),
            r=self.current_display_radius.get(), # Use current_display_radius for initial setup
            theta1=0,
            theta2=(self.get_pi_ratio(self.current_display_radius.get()) / np.pi) * 360,
            width=0.05 * self.current_display_radius.get(), # Make width relative to display radius
            facecolor=self.PI_SEGMENT_COLOR,
            alpha=0.7 # Slightly more opaque
        )
        self.ax.add_patch(self.pi_segment)
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(bg=self.BG_COLOR)
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Style the toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.canvas_frame, pack_toolbar=False)
        self.toolbar.configure(background=self.BG_COLOR)
        for button in self.toolbar.winfo_children():
            button.configure(bg=self.BG_COLOR)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)

    def get_diameter(self, radius_val=None):
        """Calculates diameter based on a given radius or the current target radius."""
        if radius_val is None:
            radius_val = self.radius.get() # Use target radius if no specific value provided
        return radius_val * 2

    def get_circumference(self, radius_val=None):
        """Calculates circumference based on a given radius or the current target radius."""
        if radius_val is None:
            radius_val = self.radius.get() # Use target radius
        return self.pi_value * self.get_diameter(radius_val)

    def get_pi_ratio(self, radius_val=None):
        """Calculates the ratio of circumference to diameter (Pi) for a given radius or the current target radius."""
        if radius_val is None:
            radius_val = self.radius.get() # Use target radius
        diameter = self.get_diameter(radius_val)
        if diameter == 0:
            return 0 # Avoid division by zero, effectively Pi is undefined or 0 for a point
        return self.get_circumference(radius_val) / diameter

    def update_texts(self):
        target_radius = self.radius.get()
        self.radius_label.config(
            text=f"Radius: {target_radius:.2f}"
        )
        self.diameter_label.config(
            text=f"Diameter: {self.get_diameter(target_radius):.2f}"
        )
        self.circumference_label.config(
            text=f"Keliling: {self.get_circumference(target_radius):.2f}"
        )
        self.pi_ratio_label.config(
            text=f"Rasio Pi (Keliling/Diameter): {self.get_pi_ratio(target_radius):.5f}"
        )
        # Update radius_entry_var only if not focused, to prevent issues while typing
        if self.root.focus_get() != self.radius_entry:
            self.radius_entry_var.set(f"{target_radius:.2f}")

    def _set_controls_state(self, state):
        """Enable or disable radius controls. state can be 'normal' or 'disabled'."""
        self.radius_slider.configure(state=state)
        self.radius_entry.configure(state=state)

    def _perform_radius_animation_step(self):
        if self.animation_job_id: # Clear previous job
            self.root.after_cancel(self.animation_job_id)
            self.animation_job_id = None

        target_r = self.radius.get()
        current_r = self.current_display_radius.get()
        difference = target_r - current_r

        if abs(difference) < self.ANIMATION_THRESHOLD:
            new_r = target_r
            self.is_animating_radius = False
            self._set_controls_state(tk.NORMAL)
        else:
            new_r = current_r + difference * self.ANIMATION_STEP_SIZE
            self.is_animating_radius = True
            self._set_controls_state(tk.DISABLED)
        
        self.current_display_radius.set(new_r)
        
        # Update visual components with current_display_radius
        self.circle_patch.set_radius(new_r)
        self.pi_segment.set_radius(new_r)
        self.pi_segment.set_width(max(0.01, 0.05 * new_r))
        # Pi segment's angle (theta2) should ideally reflect the definition of Pi based on the
        # *target* radius, ensuring it visually represents the goal state of Pi calculation.
        self.pi_segment.theta2 = (self.get_pi_ratio(target_r) / np.pi) * 360

        # Update plot limits based on the currently displayed radius
        self._update_plot_limits(new_r)
        self.canvas.draw_idle()

        if self.is_animating_radius:
            self.animation_job_id = self.root.after(self.ANIMATION_DELAY_MS, self._perform_radius_animation_step)
        else: # Animation finished
            self.current_display_radius.set(target_r) # Ensure it's exactly the target
            # Final update of texts to ensure entry var is also correct
            self.radius_entry_var.set(f"{target_r:.2f}")


    def start_radius_animation(self):
        # self.radius already holds the target radius from slider/entry
        self.update_texts() # Update labels to show target radius
        
        if self.animation_job_id: # If an animation is scheduled, cancel it
            self.root.after_cancel(self.animation_job_id)
            self.animation_job_id = None
            
        # If not already animating towards the same target, or if it's a new target
        if not self.is_animating_radius or abs(self.current_display_radius.get() - self.radius.get()) > self.ANIMATION_THRESHOLD :
            self.is_animating_radius = True
            self._set_controls_state(tk.DISABLED)
            self._perform_radius_animation_step()


    def on_radius_control_changed(self, event=None):
        """Called when slider value changes."""
        new_target_radius = self.radius.get()
        if new_target_radius < 1:
            new_target_radius = 1
            self.radius.set(new_target_radius) # Correct the tk.DoubleVar
        
        self.radius_entry_var.set(f"{new_target_radius:.2f}") # Sync entry field
        self.start_radius_animation()

    def on_radius_entry_submitted(self, event=None):
        """Called when Return is pressed in radius entry or focus is lost after change."""
        try:
            value = float(self.radius_entry_var.get())
            if 1 <= value <= 100:
                if abs(self.radius.get() - value) > self.ANIMATION_THRESHOLD: # Only if value actually changed significantly
                    self.radius.set(value)
                    # self.radius_slider.set(value) # Slider already bound to self.radius
                    self.start_radius_animation()
                else: # Value is close enough to current target, just ensure sync
                    self.radius.set(value) # Ensure self.radius is set
                    self.radius_entry_var.set(f"{value:.2f}") # Format correctly
            else: # Value out of range, reset entry to current target radius
                self.radius_entry_var.set(f"{self.radius.get():.2f}")
        except ValueError: # Invalid input
            self.radius_entry_var.set(f"{self.radius.get():.2f}")

    def on_update_button_pressed(self, event=None):
        """
        Handles the 'Perbarui Lingkaran' button press.
        This action instantly updates the circle to the values specified in the
        X, Y, and Radius input fields, cancelling any ongoing radius animation.
        """
        if self.is_animating_radius and self.animation_job_id:
            self.root.after_cancel(self.animation_job_id)
            self.is_animating_radius = False
            self._set_controls_state(tk.NORMAL)
            self.animation_job_id = None

        # Update target radius from entry, then current_display_radius
        try:
            entry_radius = float(self.radius_entry_var.get())
            if 1 <= entry_radius <= 100:
                self.radius.set(entry_radius)
            else: # Reset to current valid if out of bounds
                self.radius_entry_var.set(f"{self.radius.get():.2f}")
        except ValueError: # Reset to current valid if error
            self.radius_entry_var.set(f"{self.radius.get():.2f}")

        self.current_display_radius.set(self.radius.get()) # Snap display radius to target
        
        self.update_texts() # Ensure all text fields are synced to final values
        self.update_circle_visuals(use_current_display_radius=True) # Full visual update

    def _update_plot_limits(self, for_radius):
        """
        Adjusts the plot limits dynamically to ensure the circle (with 'for_radius')
        remains visible with adequate padding.
        """
        center_x = self.center_x.get()
        center_y = self.center_y.get()
        
        # Define desired padding around the circle
        padding_factor = 0.5 # 50% of radius as padding
        static_padding = 5   # Additional static padding units
        
        effective_padding = for_radius * padding_factor + static_padding
        
        target_xlim_min = center_x - for_radius - effective_padding
        target_xlim_max = center_x + for_radius + effective_padding
        target_ylim_min = center_y - for_radius - effective_padding
        target_ylim_max = center_y + for_radius + effective_padding

        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()

        # Update limits only if there's a significant difference to avoid minor adjustments
        # and potential visual jitter. A threshold of 1 unit is used here.
        if (abs(current_xlim[0] - target_xlim_min) > 1 or \
            abs(current_xlim[1] - target_xlim_max) > 1 or \
            abs(current_ylim[0] - target_ylim_min) > 1 or \
            abs(current_ylim[1] - target_ylim_max) > 1):
            self.ax.set_xlim(target_xlim_min, target_xlim_max)
            self.ax.set_ylim(target_ylim_min, target_ylim_max)

    def update_circle_visuals(self, use_current_display_radius=False):
        """
        Updates all visual aspects of the circle and the Pi segment on the canvas.
        This includes position, radius, color, and the Pi segment's geometry.
        It can use either the target radius or the current display radius for sizing.
        """
        center_x = self.center_x.get()
        center_y = self.center_y.get()
        
        # Determine which radius to use for this update
        radius_to_use = self.current_display_radius.get() if use_current_display_radius else self.radius.get()

        # Update circle properties
        self.circle_patch.center = (center_x, center_y)
        self.circle_patch.set_radius(radius_to_use)
        self.circle_patch.set_edgecolor(self.ACCENT_COLOR)
        self.circle_patch.set_fill(False)

        # Update Pi segment properties
        self.pi_segment.center = (center_x, center_y)
        self.pi_segment.set_radius(radius_to_use)
        # Pi segment's angle should reflect the definition of Pi, so use target radius for ratio
        self.pi_segment.theta2 = (self.get_pi_ratio(self.radius.get()) / np.pi) * 360
        self.pi_segment.set_width(max(0.01, 0.05 * radius_to_use))
        self.pi_segment.set_facecolor(self.PI_SEGMENT_COLOR)

        self._update_plot_limits(radius_to_use)
        
        # Do not call update_texts here as it might conflict with animation text updates
        # self.update_texts() 
        self.canvas.draw_idle() # Use draw_idle for potentially smoother rendering in Tkinter

    def update_circle(self):
        """
        Performs an immediate update of the circle to reflect the current target radius
        (self.radius). This method is used for initial setup and for updates
        that should not be animated (e.g., direct changes to X, Y coordinates if
        such controls were added without their own animation logic).
        It cancels any ongoing radius animation.
        """
        if self.is_animating_radius and self.animation_job_id: # Stop any ongoing animation
            self.root.after_cancel(self.animation_job_id) # type: ignore
            self.is_animating_radius = False
            self._set_controls_state(tk.NORMAL)

        self.current_display_radius.set(self.radius.get()) # Sync display radius to target
        self.update_texts() # Update all text labels to reflect the target state.
        self.update_circle_visuals(use_current_display_radius=True) # Update visuals to current_display_radius


if __name__ == "__main__":
    root = tk.Tk()
    # It's good practice to set the initial size of the window
    root.geometry("900x700") 
    app = CircleVisualization(root)
    root.mainloop()
