import tkinter as tk
from tkinter import messagebox, SOLID, SUNKEN
from tkinter import *
from tkinter import font as tkFont


def pass_strength():

    ip = entry.get()

    minimum_length = 12
    uppercase = False
    lowercase = False
    numeric = False
    weak_password = False


    for ch in ip: 
        if ch.isupper():
            uppercase = True
        
        elif ch.islower():
            lowercase= True
            
        elif ch.isnumeric():
            numeric = True
            
    #print(uppercase, lowercase, numeric)
    if len(ip) < minimum_length and ip !="":
        print("Minimum password should be atleast 12 characters long")
        messagebox.showwarning("Error", "Password should be atleast 12 characters long")
        weak_password = True

    elif ( ip == "" or (uppercase is False and lowercase is False and numeric is False)):
        print("invalid password")
        messagebox.showerror("Error", "Invalid Password")
        weak_password = True

    elif uppercase is not True:
        print("Password should contain atleast 1 uppercase character")
        messagebox.showerror( "Error", "Should have atleast 1 uppercase character")
        weak_password = True

    elif lowercase is not True:
        print("Password should contain atleast 1 lowercase character")
        messagebox.showerror( "Error", "Should have atleast 1 lowercase character")

        weak_password = True

    elif numeric is not True:
        print("Password should contain atleast 1 numeric character")
        messagebox.showerror( "Error", "Should have atleast 1 numeric character")

        weak_password = True

    else: 
        print("Password accepted")
        top = Toplevel()
        top.title("Password Accepted")
        green_window = Message(top, text="Password Accepted")
        green_window.config(bg= "lightgreen")
        green_window.pack()
       
        weak_password = False

    print("Is it a weak password:", weak_password) 




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
        show="*" # Hide characters for password input
    )
    entry.pack(pady=(0, 20), anchor="center") # Add more padding below, center it

    # Submit Button
    submit_button = tk.Button(
        input_button_frame,
        text="Check Strength",
        command=pass_strength,
        font=button_font,
        bg="#4CAF50", # Material design green for primary action
        fg="white", # White text for contrast
        activebackground="#45A049", # Darker green when pressed
        activeforeground="white",
        relief=tk.RAISED, # Raised button effect
        bd=3 # Border for button
    )
    submit_button.pack(anchor="center", ipadx=15, ipady=8) # Center, add internal padding

    
    # label_frame = tk.Frame(root, relief= SOLID, borderwidth=2).pack(pady=20, fill="x")

    # heading = tk.Label(label_frame, text="Password Strength box", font="Calibri 18",justify="center")
    # heading.pack(pady=10, expand=True, fill="both")

    # input_button_frame= tk.Frame(root)
    # input_button_frame.pack(pady=20)

    # lable = tk.Label(input_button_frame, text = "Enter Password")
    # entry = tk.Entry(input_button_frame, bd=4, width=30)
    # button = tk.Button(input_button_frame, text="Submit", command=pass_strength)
    # lable.pack(pady=(0, 5), anchor="center")
    # entry.pack(pady=(0,10), anchor="center")
    # button.pack(anchor="center")

    

    root.mainloop()