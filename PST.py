import tkinter as tk
from tkinter import messagebox, SOLID, SUNKEN
from tkinter import *
from tkinter import font as tkFont
import re

# Function to check password strength
def pass_strength():

    ip = entry.get().strip() # Get the input from the entry field

    minimum_length = 12 # Minimum length for the password
    # Check for uppercase, lowercase, numeric, and special characters
    # Using regex to check for character types
    # Using re.search to find at least one occurrence of each character type
    uppercase = bool(re.search(r'[A-Z]', ip))
    lowercase = bool(re.search(r'[a-z]', ip))
    numeric = bool(re.search(r'\d', ip))
    special_character = bool(re.search(r'[^a-zA-Z0-9]', ip))
    weak_password = False


#    """   Patterns to identify weak passwords:
#     1. Three or more identical consecutive characters (e.g., 'aaa', '111').
#     2. Common ascending letter sequences of 3+ characters (e.g., 'abc', 'xyz').
#     3. Common descending letter sequences of 3+ characters (e.g., 'cba', 'zyx').
#     4. Common ascending digit sequences of 3+ characters (e.g., '123', '789').
#     5. Common descending digit sequences of 3+ characters (e.g., '321', '987').
#  """
    identical_pass= r"(.)\1{2,}"
    ascending_letter_pass = r"abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz"
    descending_letters_pass = r"cba|edc|fed|gfe|ihg|kji|mlk|onm|qpo|tsr|vut|xwv|zyx"
    ascending_digits_pass = r"012|123|234|345|456|567|678|789"
    descending_digits_pass = r"210|321|432|543|654|765|876|987"

    # Check the length of the password:

    # If the password is less than the minimum length or empty, show an error
    if len(ip) < minimum_length and ip !="":        
        print("Minimum password should be atleast 12 characters long")
        messagebox.showerror("Length Error", "Password should be atleast 12 characters long")
        weak_password = True

    # Check for empty input or missing all character types
    elif ( ip == "" or (uppercase is False and lowercase is False and numeric is False and special_character is False)):    
        print("invalid password")
        messagebox.showerror("Input Error", "Please enter a valid password.")
        weak_password = True

    #----Check for missing uppercase, lowercase, numeric, or special characters----
    elif uppercase is not True:
        print("Password should contain atleast 1 uppercase character")
        messagebox.showerror( "Uppercase Input Error", "Password should contain at least 1 uppercase character.")
        weak_password = True

    elif lowercase is not True:
        print("Password should contain atleast 1 lowercase character")
        messagebox.showerror( "Lowercase Input Error", "Password should contain at least 1 lowercase character.")
        weak_password = True

    elif numeric is not True:
        print("Password should contain atleast 1 numeric character")
        messagebox.showerror( "Numeric Input Error", "Password should contain at least 1 numeric character.")
        weak_password = True

    elif special_character is not True:
        print("Password should contain atleast 1 special character")
        messagebox.showerror( "Special character Input Error", "Password should contain at least 1 special character.")
        weak_password = True

    # If the password meets all criteria, check for weak patterns
    # If all checks pass, the password is accepted
    else: 
        print("Password accepted")

        # ---Check for weak password:----
        
        # Identical consecutive characters
        if re.search(identical_pass,ip,re.IGNORECASE):
            weak_password=True           
            result.config(
                text="Weak Password: Repeated characters detected",
                fg="#D32F2F",  # Material Red 700
                bg="#FFF3F3",  # Light red background
                font=(result_font.actual('family'), 14, 'bold')
            )            
            messagebox.showwarning( "Weak Pattern Detected", "Your password contains repeated characters (e.g., 'aaa', '111'). Please avoid such patterns.")

        # Ascending letter sequences
        elif re.search(ascending_letter_pass,ip,re.IGNORECASE):
            weak_password=True           
            result.config(
                text="Weak Password: Ascending letter sequence",
                fg="#D32F2F",
                bg="#FFF3F3",
                font=(result_font.actual('family'), 14, 'bold')
            )     
            messagebox.showwarning("Weak Pattern Detected", "Your password contains an ascending letter sequence (e.g., 'abc', 'xyz'). Please avoid such patterns.")

        # Descending letter sequences
        elif re.search(descending_letters_pass,ip,re.IGNORECASE):
            weak_password=True           
            result.config(
                text="Weak Password: Descending letter sequence",
                fg="#D32F2F",
                bg="#FFF3F3",
                font=(result_font.actual('family'), 14, 'bold')
            )           
            messagebox.showwarning("Weak Pattern Detected", "Your password contains a descending letter sequence (e.g., 'cba', 'zyx'). Please avoid such patterns.")

        # Ascending digit sequences
        elif re.search(ascending_digits_pass,ip,re.IGNORECASE):
            weak_password=True           
            result.config(  
                text="Weak Password: Ascending digit sequence",
                fg="#D32F2F",
                bg="#FFF3F3",
                font=(result_font.actual('family'), 14, 'bold')
            )            
            messagebox.showwarning("Weak Pattern Detected", "Your password contains an ascending digit sequence (e.g., '123', '789'). Please avoid such patterns.")
       
        # Descending digit sequences
        elif re.search(descending_digits_pass,ip,re.IGNORECASE):
            weak_password=True           
            result.config(
                text="Weak Password: Descending digit sequence",
                fg="#D32F2F",
                bg="#FFF3F3",
                font=(result_font.actual('family'), 14, 'bold')
            )            
            messagebox.showwarning("Weak Pattern Detected", "Your password contains a descending digit sequence (e.g., '321', '987'). Please avoid such patterns.")

        # If no weak patterns are found, the password is strong
        else:
            weak_password = False
            result.config(
                text="Strong Password",
                fg="#388E3C",  # Material Green 700
                bg="#E8F5E9", # Light green background
                font=(result_font.actual('family'), 14, 'bold')
            )
    print("Is it a weak password:", weak_password) 

    
# Function to reset the entry field and result label
# This function clears the entry field and resets the result label
def inital_state():
    entry.delete(0, tk.END)
    result.config(
        text="",
        fg="black",
        bg="#F0F0F0",
        font=(result_font.actual('family'), 12, 'bold')
    )

# --- Tooltip Helper Class ---
class ToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 30
        y = y + self.widget.winfo_rooty() + 30
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify='left',
            background="#ffffe0", relief='solid', borderwidth=1,
            font=("Arial", 10)
        )
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


# Main function to run the application
if __name__ == "__main__":
    root = tk.Tk()  # This function initializes the Tkinter window and sets up the layout      

    root.title("Password Strength Tester") # Set the title of the window
    root.geometry("700x500") # Set the initial size of the window
    root.resizable(False, False) # Disable resizing of the window
    root.configure(bg="#F0F0F0")  # Set a light grey background for the root window

     # --- Define Custom Fonts ---
    # This gives you more control over typography
    heading_font = tkFont.Font(family="Helvetica Neue", size=24, weight="bold") 
    label_font = tkFont.Font(family="Arial", size=14) 
    entry_font = tkFont.Font(family="Arial", size=14)  
    button_font = tkFont.Font(family="Arial", size=12, weight="bold") 
    result_font = tkFont.Font(family="Arial", size=12, weight="bold")
    reset_font = tkFont.Font(family="Arial", size=12, weight="bold")

    # --- Main Container Frame (for overall padding and centering) ---
    # This frame will hold all other frames and widgets, providing a consistent padding and background
    # It uses a light grey background to create a clean and modern look.

    # A central frame helps to group everything and center it within the root window.
    main_frame = tk.Frame(root, padx=40, pady=40, bg="#F0F0F0")  # Padding around the main frame 
    main_frame.pack(expand=True, fill="both") # Allow it to fill the root window and expand

    # --- Heading Section ---

    heading_frame = tk.Frame(main_frame, bg="#E0E0E0", bd=2, relief=SUNKEN) # Softer border, light grey background
    heading_frame.pack(pady=(0, 30), fill="x") # Add padding only at the bottom, fill horizontally

    # Heading label with a larger font, centered in the heading frame
    # This label serves as the title for the application, using a bold font for emphasis.
    # It uses a slightly darker grey for the text to contrast with the heading frame background.    
    heading_label = tk.Label(
        heading_frame,
        text="Password Strength Analyzer",
        font=heading_font,
        bg="#E0E0E0", 
        fg="#333333" 
    )
    heading_label.pack(pady=20, expand=True, fill="both") # Center the text within the heading frame

    # --- Input and Button Section ---
    # This section contains the input field for the password and buttons for checking strength and resetting.
    # It uses a light grey background to match the main frame, providing a cohesive look.
    input_button_frame = tk.Frame(main_frame, bg="#F0F0F0") # Match main_frame background
    input_button_frame.pack(pady=(0, 20)) # Add some space below the heading

    # Label for password input
    # This label prompts the user to enter their password, using a medium grey text color for readability.
    # It is centered above the entry field to guide the user.
    # The label uses a slightly larger font for better visibility.        
    password_label = tk.Label(
        input_button_frame,
        text="Enter Your Password:",
        font=label_font,
        bg="#F0F0F0", # Match frame background
        fg="#555555" # Medium grey text
    )
    password_label.pack(pady=(0, 10), anchor="center") # Add padding below, center it

    # Tooltip for password requirements
    password_requirements = (
        "Password Requirements:\n"
        "• At least 12 characters long\n"
        "• At least 1 uppercase letter (A-Z)\n"
        "• At least 1 lowercase letter (a-z)\n"
        "• At least 1 digit (0-9)\n"
        "• At least 1 special character (!, @, #, etc.)\n"
        "• Avoid common sequences (e.g., 'abc', '123')\n"
        "• Avoid repeated characters (e.g., 'aaa', '111')"
    )   
              
    # Password entry field
    # This entry field allows the user to input their password.
    # It uses a slightly larger font for better readability and has a softer border for a modern
    entry = tk.Entry(
        input_button_frame,
        bd=2, # Softer border for the entry field
        width=35, # Slightly wider entry field
        font=entry_font,
        show="*" # Hide characters for password input
    )
    entry.pack(pady=(0, 10), anchor="center") # Add more padding below, center it

    # Tooltip for the password entry field
    # This tooltip provides the user with information about the password requirements.
    ToolTip(password_label, password_requirements)
    ToolTip(entry, password_requirements) 
    
    # Function to toggle password visibility
    def toggle_password():
        if show_var.get():
            entry.config(show="")  # Show password
        else:
            entry.config(show="*")  # Hide password

    # Checkbox for show/hide password
    show_var = tk.BooleanVar(value=False)
    show_password_cb = tk.Checkbutton(
        input_button_frame,
        text="Show Password",
        variable=show_var,
        command=toggle_password,
        bg="#F0F0F0",
        font=("Arial", 10)
    )
    show_password_cb.pack(anchor="center")
    
 # --- Button Frame to group Check and Reset buttons ---
    # This frame holds the buttons for checking password strength and resetting the input.
    button_frame = tk.Frame(main_frame, bg="#F0F0F0")
    button_frame.pack(pady=(0, 20)) # Padding below buttons

    # This frame is used to group the buttons together, providing a consistent look and feel.
    # It uses the same background color as the main frame to maintain a cohesive design.
    # Submit Button
    submit_button = tk.Button(
        button_frame, # Pack into the new button_frame
        text="Check Strength",
        command=pass_strength,
        font=button_font,
        bg="#4CAF50",
        fg="white",
        activebackground="#45A049",
        activeforeground="white",
        relief=tk.RAISED,
        bd=3
    )
    submit_button.pack(side=tk.LEFT, ipadx=20, ipady=10, padx=(0, 10)) # Keep a small padx between buttons


    # Reset Button
    reset = tk.Button(
        button_frame, # Pack into the new button_frame
        text="Reset",
        command=inital_state,
        font=reset_font,
        bg="#4CAF50",
        fg="white",
        activebackground="#45A049",
        activeforeground="white",
        relief=tk.RAISED,
        bd=3
    )
    reset.pack(side=tk.RIGHT, ipadx=20, ipady=10) # Keep a small padx between buttons

    # Result Label - placed after buttons
    # This label displays the result of the password strength check.
    # It uses a bold font to highlight the result and is centered below the buttons.
    result = tk.Label(
        main_frame, # Pack directly into main_frame
        text = "",
        font=result_font,
        bg="#F0F0F0", # Ensure background matches main frame
        fg="black" # Default text color
    )
    result.pack(pady=(10,0), anchor="center") # Add padding above, center it


    # Start the Tkinter main loop to run the application
    # This function keeps the application running, waiting for user interactions.  
    root.mainloop()