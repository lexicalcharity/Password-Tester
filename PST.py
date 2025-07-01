import tkinter as tk
from tkinter import messagebox, SOLID, SUNKEN
from tkinter import *
from tkinter import font as tkFont
import re


def pass_strength():

    ip = entry.get()

    minimum_length = 12
    uppercase = bool(re.search(r'[A-Z]', ip))
    lowercase = bool(re.search(r'[a-z]', ip))
    numeric = bool(re.search(r'\d', ip))
    special_character = bool(re.search(r'[^a-zA-Z0-9]', ip))
    weak_password = False


#    """   Patterns checked:
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


            
    #print(uppercase, lowercase, numeric)
    if len(ip) < minimum_length and ip !="":
        print("Minimum password should be atleast 12 characters long")
        messagebox.showerror("Error", "Password should be atleast 12 characters long")
        weak_password = True
        #result.config(text="Weak Password", fg="red")

    elif ( ip == "" or (uppercase is False and lowercase is False and numeric is False and special_character is False)):
        print("invalid password")
        messagebox.showerror("Error", "Invalid Password")
        weak_password = True


    elif uppercase is not True:
        print("Password should contain atleast 1 uppercase character")
        messagebox.showerror( "Error", "Should have atleast 1 uppercase character")
        weak_password = True
        #result.config(text="Weak Password", fg="red")


    elif lowercase is not True:
        print("Password should contain atleast 1 lowercase character")
        messagebox.showerror( "Error", "Should have atleast 1 lowercase character")
        weak_password = True
        #result.config(text="Weak Password", fg="red")


    elif numeric is not True:
        print("Password should contain atleast 1 numeric character")
        messagebox.showerror( "Error", "Should have atleast 1 numeric character")
        weak_password = True
        #result.config(text="Weak Password", fg="red")

    elif special_character is not True:
        print("Password should contain atleast 1 special character")
        messagebox.showerror( "Error", "Should have atleast 1 special character")
        weak_password = True
        #result.config(text="Weak Password", fg="red")


    else: 
        print("Password accepted")
        if re.search(identical_pass,ip,re.IGNORECASE):
            weak_password=True           
            result.config(text="Weak Password", fg="Red")
            messagebox.showwarning( "Weak Password", "Pattern recognized")



        elif re.search(ascending_letter_pass,ip,re.IGNORECASE):
            weak_password=True           
            result.config(text="Weak Password", fg="Red")
            messagebox.showwarning( "Weak Password", "Pattern recognized")


        elif re.search(descending_letters_pass,ip,re.IGNORECASE):
            weak_password=True           
            result.config(text="Weak Password", fg="Red")
            messagebox.showwarning( "Weak Password", "Pattern recognized")

        elif re.search(ascending_digits_pass,ip,re.IGNORECASE):
            weak_password=True           
            result.config(text="Weak Password", fg="Red")
            messagebox.showwarning( "Weak Password", "Pattern recognized")

        elif re.search(descending_digits_pass,ip,re.IGNORECASE):
            weak_password=True           
            result.config(text="Weak Password", fg="Red")  
            messagebox.showwarning( "Weak Password", "Pattern recognized")
      
        else:
            weak_password = False
            result.config(text="Strong Password", fg="Green")



    print("Is it a weak password:", weak_password) 

    
#reset Gui to Intial state

def inital_state():
    entry.delete(0, tk.END)
    result.config(text="", fg="Green")







if __name__ == "__main__":
    root = tk.Tk()
    root.title("Password Strength Tester")
    root.geometry("700x500")
    root.resizable(False, False)
     # --- Define Custom Fonts ---
    # This gives you more control over typography
    heading_font = tkFont.Font(family="Helvetica Neue", size=24, weight="bold")
    label_font = tkFont.Font(family="Arial", size=14)
    entry_font = tkFont.Font(family="Consolas", size=14) # Monospaced font for entry looks good
    button_font = tkFont.Font(family="Arial", size=12, weight="bold")
    result_font = tkFont.Font(family="Arial", size=12, weight="bold")
    reset_font = tkFont.Font(family="Arial", size=12, weight="bold")

    # --- Main Container Frame (for overall padding and centering) ---
    # A central frame helps to group everything and center it within the root window.
    main_frame = tk.Frame(root, padx=40, pady=40, bg="#F0F0F0") # Light grey background for the main area
    main_frame.pack(expand=True, fill="both") # Allow it to fill the root window and expand

    # --- Heading Section ---
    heading_frame = tk.Frame(main_frame, bg="#E0E0E0", bd=2, relief=SUNKEN) # Softer border, light grey background
    heading_frame.pack(pady=(0, 30), fill="x") # Add padding only at the bottom, fill horizontally

    heading_label = tk.Label(
        heading_frame,
        text="Password Strength Analyzer",
        font=heading_font,
        bg="#E0E0E0", # Match frame background
        fg="#333333" # Darker text color
    )
    heading_label.pack(pady=20, expand=True, fill="both") # Center the text within the heading frame

    # --- Input and Button Section ---
    input_button_frame = tk.Frame(main_frame, bg="#F0F0F0") # Match main_frame background
    input_button_frame.pack(pady=(0, 20)) # Add some space below the heading

    # Label for password input
    password_label = tk.Label(
        input_button_frame,
        text="Enter Your Password:",
        font=label_font,
        bg="#F0F0F0", # Match frame background
        fg="#555555" # Medium grey text
    )
    password_label.pack(pady=(0, 10), anchor="center") # Add padding below, center it

    # Password entry field
    entry = tk.Entry(
        input_button_frame,
        bd=2, # Softer border for the entry field
        width=35, # Slightly wider entry field
        font=entry_font,
        #show="*" # Hide characters for password input
    )
    entry.pack(pady=(0, 20), anchor="center") # Add more padding below, center it
    
 # --- Button Frame to group Check and Reset buttons ---
    button_frame = tk.Frame(main_frame, bg="#F0F0F0")
    button_frame.pack(pady=(0, 20)) # Padding below buttons

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
    reset.pack(side=tk.RIGHT, ipadx=20, ipady=10)

    # Result Label - placed after buttons
    result = tk.Label(
        main_frame, # Pack directly into main_frame
        text = "",
        font=result_font,
        bg="#F0F0F0", # Ensure background matches main frame
        fg="black" # Default text color
    )
    result.pack(pady=(10,0), anchor="center") # Add padding above, center it


    # # Submit Button
    # submit_button = tk.Button(
    #     input_button_frame,
    #     text="Check Strength",
    #     command=pass_strength,
    #     font=button_font,
    #     bg="#4CAF50", # Material design green for primary action
    #     fg="white", # White text for contrast
    #     activebackground="#45A049", # Darker green when pressed
    #     activeforeground="white",
    #     relief=tk.RAISED, # Raised button effect
    #     bd=3 # Border for button
    # )
    # submit_button.pack(side=tk.LEFT, ipadx=20, ipady=10, padx=(0, 10))

    # reset = tk.Button( 
    #     input_button_frame,
    #     text="Reset",
    #     command=inital_state,
    #     font=reset_font,
    #     bg="#4CAF50", # Material design green for primary action
    #     fg="white", # White text for contrast
    #     activebackground="#45A049", # Darker green when pressed
    #     activeforeground="white",
    #     relief=tk.RAISED, # Raised button effect
    #     bd=3 # Border for button
    # )
    # reset.pack(side=tk.RIGHT, ipadx=20, ipady=10) 

    # #reset.pack(side=RIGHT,ipadx=15, ipady=8)

    # result = tk.Label( 
    #     input_button_frame,
    #     text = "",
    #     font=result_font
    # )
    # #result.pack(anchor="s", ipadx=20, ipady=8) # Center, add internal padding
    # result.pack(side=tk.TOP)


    

    root.mainloop()