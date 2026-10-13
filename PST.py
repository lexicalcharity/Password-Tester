"""Password Strength Tester: a Tkinter GUI that checks passwords as you type."""

import threading
import tkinter as tk
from tkinter import font as tkFont
from tkinter import messagebox

import password_checker as checker

# --- Colours ---
BACKGROUND = "#F0F0F0"     # Light grey window background
HEADING_BACKGROUND = "#E0E0E0"
PASS_COLOUR = "#388E3C"    # Material Green 700
FAIL_COLOUR = "#D32F2F"    # Material Red 700
WARNING_COLOUR = "#F57C00" # Material Orange 700
MUTED_COLOUR = "#757575"   # Material Grey 600
# Rating -> (text colour, light background colour)
RATING_COLOURS = {
    "Weak": (FAIL_COLOUR, "#FFF3F3"),
    "Fair": (WARNING_COLOUR, "#FFF8E1"),
    "Good": ("#1976D2", "#E3F2FD"),   # Material Blue 700, light blue
    "Strong": (PASS_COLOUR, "#E8F5E9"),
}

# Text for the tooltip on the password field
PASSWORD_REQUIREMENTS = (
    "Password Requirements:\n"
    f"• At least {checker.MINIMUM_LENGTH} characters long\n"
    "• At least 1 uppercase letter (A-Z)\n"
    "• At least 1 lowercase letter (a-z)\n"
    "• At least 1 digit (0-9)\n"
    "• At least 1 special character (!, @, #, etc.)\n"
    f"  (passphrases of {checker.PASSPHRASE_LENGTH}+ characters can skip these four)\n"
    "• Avoid common sequences (e.g., 'abc', '123')\n"
    "• Avoid repeated characters (e.g., 'aaa', '111')\n"
    "• Avoid keyboard patterns (e.g., 'qwerty', 'asdf')\n"
    "• Avoid common passwords and words (e.g., 'P@ssw0rd')"
)


# Function to pick the first installed font from a list of preferences
# ('Helvetica Neue' is not available on Windows, so fall back to similar fonts)
def pick_font_family(preferences):
    installed = set(tkFont.families())
    for family in preferences:
        if family in installed:
            return family
    return "TkDefaultFont"


# --- Tooltip Helper Class ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        # Show the tooltip just below the widget
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify="left",
            background="#ffffe0", relief="solid", borderwidth=1,
            font=("Arial", 10)
        )
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


class PasswordTesterApp:
    METER_WIDTH = 420
    METER_HEIGHT = 14

    def __init__(self, root):
        self.root = root
        self.breach_thread = None  # Background breach lookup, if one is running
        self.breach_result = None  # (password checked, count or None on error)

        root.title("Password Strength Tester")
        root.geometry("700x720")  # Room for the checklist plus a few warnings
        root.minsize(560, 680)
        root.configure(bg=BACKGROUND)

        # --- Define Custom Fonts ---
        family = pick_font_family(["Segoe UI", "Helvetica Neue", "Helvetica", "Arial"])
        self.heading_font = tkFont.Font(family=family, size=24, weight="bold")
        self.label_font = tkFont.Font(family=family, size=14)
        self.entry_font = tkFont.Font(family=family, size=14)
        self.button_font = tkFont.Font(family=family, size=12, weight="bold")
        self.rating_font = tkFont.Font(family=family, size=14, weight="bold")
        self.small_font = tkFont.Font(family=family, size=11)

        self.build_layout()
        self.update_feedback()

    # --- Layout ---
    def build_layout(self):
        # A central frame groups everything and gives consistent padding
        main_frame = tk.Frame(self.root, padx=40, pady=30, bg=BACKGROUND)
        main_frame.pack(expand=True, fill="both")

        # --- Heading Section ---
        heading_frame = tk.Frame(main_frame, bg=HEADING_BACKGROUND, bd=2, relief=tk.SUNKEN)
        heading_frame.pack(pady=(0, 20), fill="x")
        tk.Label(
            heading_frame,
            text="Password Strength Analyzer",
            font=self.heading_font,
            bg=HEADING_BACKGROUND,
            fg="#333333"
        ).pack(pady=15, expand=True, fill="both")

        # --- Input Section ---
        password_label = tk.Label(
            main_frame,
            text="Enter Your Password:",
            font=self.label_font,
            bg=BACKGROUND,
            fg="#555555"
        )
        password_label.pack(pady=(0, 8))

        # Every change to the password updates the feedback straight away
        self.password_var = tk.StringVar()
        self.password_var.trace_add("write", lambda *args: self.update_feedback())
        self.entry = tk.Entry(
            main_frame,
            textvariable=self.password_var,
            bd=2,
            width=35,
            font=self.entry_font,
            show="*"  # Hide characters for password input
        )
        self.entry.pack(pady=(0, 8))
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda event: self.check_strength())  # Enter = Check Strength
        self.entry.bind("<Escape>", lambda event: self.reset())           # Esc = Reset

        ToolTip(password_label, PASSWORD_REQUIREMENTS)
        ToolTip(self.entry, PASSWORD_REQUIREMENTS)

        # Checkbox for show/hide password
        self.show_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            main_frame,
            text="Show Password",
            variable=self.show_var,
            command=self.toggle_password,
            bg=BACKGROUND,
            activebackground=BACKGROUND,
            font=self.small_font
        ).pack()

        # --- Strength Meter and Rating ---
        self.meter = tk.Canvas(
            main_frame,
            width=self.METER_WIDTH,
            height=self.METER_HEIGHT,
            bg="#DDDDDD",
            highlightthickness=0
        )
        self.meter.pack(pady=(15, 5))
        self.meter_bar = self.meter.create_rectangle(0, 0, 0, self.METER_HEIGHT, width=0)

        self.rating_label = tk.Label(main_frame, font=self.rating_font, bg=BACKGROUND, padx=10, pady=2)
        self.rating_label.pack(pady=(0, 10))

        # --- Requirements Checklist ---
        # One label per requirement, showing ✓ or ✗ (so it doesn't rely on colour alone)
        checklist_frame = tk.Frame(main_frame, bg=BACKGROUND)
        checklist_frame.pack()
        requirements, _ = checker.check_requirements("")
        self.checklist_labels = []
        for _ in requirements:
            label = tk.Label(checklist_frame, font=self.small_font, bg=BACKGROUND, anchor="w")
            label.pack(fill="x")
            self.checklist_labels.append(label)

        # --- Warnings about weak patterns ---
        self.warnings_label = tk.Label(
            main_frame,
            font=self.small_font,
            bg=BACKGROUND,
            fg=WARNING_COLOUR,
            wraplength=600,  # Wrap long warnings instead of cutting them off
            justify="center"
        )
        self.warnings_label.pack(pady=(8, 0))

        # --- Buttons ---
        button_frame = tk.Frame(main_frame, bg=BACKGROUND)
        button_frame.pack(pady=(15, 10))
        button_style = dict(font=self.button_font, fg="white", activeforeground="white", relief=tk.RAISED, bd=3)

        self.check_button = tk.Button(
            button_frame,
            text="Check Strength",
            command=self.check_strength,
            bg="#4CAF50",
            activebackground="#45A049",
            **button_style
        )
        self.check_button.pack(side=tk.LEFT, ipadx=20, ipady=8, padx=(0, 10))

        tk.Button(
            button_frame,
            text="Reset",
            command=self.reset,
            bg=MUTED_COLOUR,
            activebackground="#616161",
            **button_style
        ).pack(side=tk.LEFT, ipadx=20, ipady=8)

        # --- Breach check result ---
        self.breach_label = tk.Label(main_frame, font=self.small_font, bg=BACKGROUND, wraplength=600)
        self.breach_label.pack()

    # --- Behaviour ---
    def toggle_password(self):
        self.entry.config(show="" if self.show_var.get() else "*")

    # Function to refresh the meter, rating, checklist and warnings for the current password
    def update_feedback(self):
        password = self.password_var.get()
        evaluation = checker.evaluate(password)

        # Any earlier breach result was for a different password
        self.breach_label.config(text="")

        # Requirements checklist
        requirements = evaluation.requirements or checker.check_requirements("")[0]
        for label, (description, passed) in zip(self.checklist_labels, requirements):
            if password == "":
                label.config(text=f"•  {description}", fg=MUTED_COLOUR)
            elif evaluation.is_passphrase and description != requirements[0][0]:
                label.config(text=f"✓  {description} (not needed for passphrases)", fg=PASS_COLOUR)
            else:
                label.config(text=f"{'✓' if passed else '✗'}  {description}",
                             fg=PASS_COLOUR if passed else FAIL_COLOUR)

        # Meter and rating
        if evaluation.rating:
            fg, bg = RATING_COLOURS[evaluation.rating]
            fill_width = self.METER_WIDTH * evaluation.level / len(checker.RATINGS)
            self.meter.coords(self.meter_bar, 0, 0, fill_width, self.METER_HEIGHT)
            self.meter.itemconfig(self.meter_bar, fill=fg)

            if evaluation.is_common:
                rating_text = "Weak Password: Common password"
            elif not evaluation.meets_requirements:
                rating_text = "Weak Password: Requirements not met"
            else:
                rating_text = f"{evaluation.rating} Password (about {evaluation.bits:.0f} bits of entropy)"
            self.rating_label.config(text=rating_text, fg=fg, bg=bg)
        else:
            self.meter.coords(self.meter_bar, 0, 0, 0, self.METER_HEIGHT)
            self.rating_label.config(text="Start typing to see how strong your password is",
                                     fg=MUTED_COLOUR, bg=BACKGROUND)

        # Weak patterns
        self.warnings_label.config(text="\n".join(f"⚠ {warning}" for warning in evaluation.warnings))

    # Function to check the password against known data breaches (needs internet)
    def check_strength(self):
        password = self.password_var.get()
        if password == "":
            self.breach_label.config(text="Please enter a password first.", fg=FAIL_COLOUR)
            return
        if self.breach_thread:
            return  # A check is already running

        self.breach_label.config(text="Checking known data breaches...", fg=MUTED_COLOUR)
        self.check_button.config(state=tk.DISABLED)

        # Run the network lookup in the background so the window doesn't freeze
        def lookup():
            try:
                count = checker.check_breach(password)
            except OSError:
                count = None
            self.breach_result = (password, count)

        self.breach_result = None
        self.breach_thread = threading.Thread(target=lookup, daemon=True)
        self.breach_thread.start()
        self.root.after(100, self.show_breach_result)

    # Function to show the breach result once the background lookup finishes
    # (Tkinter widgets must only be updated from the main thread, so this polls)
    def show_breach_result(self):
        if self.breach_thread.is_alive():
            self.root.after(100, self.show_breach_result)
            return
        self.breach_thread = None
        self.check_button.config(state=tk.NORMAL)

        password, count = self.breach_result
        if password != self.password_var.get():
            return  # The password changed while checking, so the result is out of date

        if count is None:
            self.breach_label.config(
                text="Couldn't reach the breach database. Check your internet connection and try again.",
                fg=MUTED_COLOUR)
        elif count > 0:
            self.breach_label.config(
                text=f"✗ Found in {count:,} known data breaches. Do not use this password.",
                fg=FAIL_COLOUR)
            messagebox.showwarning(
                "Breached Password",
                f"This password has appeared {count:,} times in known data breaches.\n\n"
                "Attackers use these lists first, so please choose a different password.")
        else:
            self.breach_label.config(text="✓ Not found in any known data breaches.", fg=PASS_COLOUR)

    # Function to clear the password and all feedback
    def reset(self):
        self.password_var.set("")  # Also refreshes the feedback
        self.entry.focus_set()


# Main function to run the application
if __name__ == "__main__":
    root = tk.Tk()
    PasswordTesterApp(root)
    root.mainloop()
