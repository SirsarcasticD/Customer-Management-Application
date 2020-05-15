import tkinter as tk
from Backend import *

class Application(tk.Frame):

    """
    Create subclass for functions? Function for every menu?

    Expand app to have verifications for each type of data
    """

    def __init__(self, master):

        # Would like to know exactly what this is doing
        super().__init__(master)

        # Instantiate main window
        self.window = master

        # Set Window dimensions
        self.window.geometry("700x500")

        # Connect to backend.
        # Pass in our root window to allow manipulation of it's contents within the backend namespace
        self.backend = Backend(self.window)

        """
        There is an exception, some objects of TK are not tied to the root window object. Those are passed in
        as arguments so that they can be manipulated in the backend and the effects are applied to the gui.
        """

        # Display Main Menu
        self.mainMenu()

    def mainMenu(self):

        """
        This function ...

        :return:
        """

        self.clearFrame()

        self.window.title('Generic Music Provider System Manager')

        # Buttons
        add_btn = tk.Button(self.window, text='Customer Menu', width=12, command=self.customerMenu)
        add_btn.grid(row=2, column=0, pady=20)

        remove_btn = tk.Button(self.window, text='Music Menu', width=12, command=None)
        remove_btn.grid(row=2, column=1)

        update_btn = tk.Button(self.window, text='Artist Menu', width=12, command=None)
        update_btn.grid(row=2, column=2)

        exit_btn = tk.Button(self.window, text='Exit', width=12, command=self.exitProgram)
        exit_btn.grid(row=2, column=3)

    def customerMenu(self):

        """
        This function ...

        Change variable names
        :return:
        """

        self.clearFrame()

        self.window.title('Customer Menu')

        # Customer Search
        cust_email = tk.StringVar(self.window)
        cust_label = tk.Label(self.window, text='Search Customer Email', font=('bold', 14), pady=20)
        cust_label.grid(row=1, column=0, sticky=tk.W)
        cust_entry = tk.Entry(self.window, textvariable=cust_email)
        cust_entry.grid(row=1, column=1)

        # Customer View
        view_text = tk.StringVar(self.window)
        view_label = tk.Label(self.window, text='View Customer Info', font=('bold', 14), pady=20)
        view_label.grid(row=5, column=0, sticky=tk.W)

        # Customer Info (Listbox)
        cust_list = tk.Listbox(self.window, height=8, width=50)
        cust_list.grid(row=6, column=0, columnspan=3, rowspan=6, pady=20, padx=20)
        # cust_list.configure(justify='left')

        # Create scrollbar
        scrollbar = tk.Scrollbar(self.window)
        scrollbar.grid(row=6, column=3)
        # Set scroll to list
        cust_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=cust_list.yview)

        # Buttons
        add_btn = tk.Button(self.window, text='Search', width=12, command=lambda: self.backend.getCustomerInfo(cust_email.get(), cust_list))
        add_btn.grid(row=1, column=2)

        add_btn = tk.Button(self.window, text='Add Customer', width=12, command=self.addCustomerMenu)
        add_btn.grid(row=2, column=3)

        remove_btn = tk.Button(self.window, text='Delete Customer', width=12, command=lambda: self.backend.deleteCustomer(cust_list))
        remove_btn.grid(row=3, column=3)

        update_btn = tk.Button(self.window, text='Edit Customer', width=12, command=self.backend.editCustomer)
        update_btn.grid(row=4, column=3)

        # Return
        add_btn = tk.Button(self.window, text='<- Main Menu', width=15, command=self.mainMenu)
        add_btn.grid(row=0, column=0)

    def addCustomerMenu(self):

        '''
        Function to..

        :return:
        '''

        self.clearFrame()

        self.window.title('Add Customer Menu')

        # Customer email
        cust_email = tk.StringVar(self.window)
        cust_label = tk.Label(self.window, text='Email', font=('bold', 14), pady=10)
        cust_label.grid(row=2, column=0, sticky=tk.W)
        cust_entry = tk.Entry(self.window, textvariable=cust_email)
        cust_entry.grid(row=2, column=1)

        # Check Label
        check_msg = tk.StringVar(self.window)
        check_label = tk.Label(self.window, textvariable=check_msg, font=('bold', 14))
        check_label.grid(row=3, column=0, columnspan=3, sticky=tk.W)

        # Customer Password
        cust_pass = tk.StringVar(self.window)
        cust_label = tk.Label(self.window, text='Password', font=('bold', 14), pady=10)
        cust_label.grid(row=4, column=0, sticky=tk.W)
        cust_entry = tk.Entry(self.window, textvariable=cust_pass)
        cust_entry.grid(row=4, column=1)

        # Customer First name
        cust_fname = tk.StringVar(self.window)
        cust_label = tk.Label(self.window, text='First name', font=('bold', 14), pady=10)
        cust_label.grid(row=6, column=0, sticky=tk.W)
        cust_entry = tk.Entry(self.window, textvariable=cust_fname)
        cust_entry.grid(row=6, column=1)

        # Customer Last name
        cust_lname = tk.StringVar(self.window)
        cust_label = tk.Label(self.window, text='Last name', font=('bold', 14), pady=10)
        cust_label.grid(row=8, column=0, sticky=tk.W)
        cust_entry = tk.Entry(self.window, textvariable=cust_lname)
        cust_entry.grid(row=8, column=1)

        # Customer Country
        cust_country = tk.StringVar(self.window)
        cust_label = tk.Label(self.window, text='Country', font=('bold', 14), pady=10)
        cust_label.grid(row=10, column=0, sticky=tk.W)
        cust_entry = tk.Entry(self.window, textvariable=cust_country)
        cust_entry.grid(row=10, column=1)

        # Customer City
        cust_city = tk.StringVar(self.window)
        cust_label = tk.Label(self.window, text='City', font=('bold', 14), pady=10)
        cust_label.grid(row=12, column=0, sticky=tk.W)
        cust_entry = tk.Entry(self.window, textvariable=cust_city)
        cust_entry.grid(row=12, column=1)

        # Customer Address
        cust_address = tk.StringVar(self.window)
        cust_label = tk.Label(self.window, text='Address', font=('bold', 14), pady=10)
        cust_label.grid(row=14, column=0, sticky=tk.W)
        cust_entry = tk.Entry(self.window, textvariable=cust_address)
        cust_entry.grid(row=14, column=1)

        # Feedback Label
        feedback_msg = tk.StringVar(self.window)
        feedback_label = tk.Label(self.window, textvariable=feedback_msg, font=('bold', 14))
        feedback_label.grid(row=16, column=0, columnspan=3, sticky=tk.W)

        # Buttons
        add_btn = tk.Button(self.window, text='Check', width=12, command=lambda: self.backend.checkCustomerExists(cust_email.get(), check_msg))
        add_btn.grid(row=2, column=2)

        add_btn = tk.Button(self.window, text='Add Customer', width=12, command=lambda: self.backend.addCustomer(cust_email.get(), cust_pass.get(), cust_fname.get(), cust_lname.get(), cust_country.get(), cust_city.get(), cust_address.get(), feedback_msg))
        add_btn.grid(row=15, column=0)

        # Return
        add_btn = tk.Button(self.window, text='<- Customer Menu', width=14, command=self.customerMenu)
        add_btn.grid(row=0, column=0)

        return

    def clearFrame(self):

        """
        Function to clear the Frame/Window of any widgets. This is typically called when changing menus.
        :return:
        """

        for widget in self.window.winfo_children():
            widget.destroy()

    def exitProgram(self):

        self.window.destroy()
        # sys.exit()

if __name__ == '__main__':

    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
