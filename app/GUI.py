import tkinter as tk
from tkinter import ttk

from Backend import *
import sys

"""
A simple customer management system for a hypothetical business. 
"""

class Application(tk.Frame):

    """
    Application Front end

    TODO:
    Make new windows appear in middle of parents. (Use winfo_rootx(), winfo_rooty())

    Auto complete? When typing, make system, wait 1 second and cancel any calls until last one?
    """

    def __init__(self, master):

        super().__init__(master)

        # Instantiate main window
        self.window = master
        self.window.resizable(False, False)

        # Get Screen dimensions
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        # Set window dimensions
        self.window_width = 650
        self.window_height = 600

        # Set position of window placement (Top left coordinates)
        self.x_position = (self.screen_width/2) - (self.window_width/2)
        self.y_position = (self.screen_height/2) - (self.window_height/2)

        # Configure Window dimensions
        self.window.geometry("%dx%d+%d+%d" % (self.window_width, self.window_height, self.x_position, self.y_position))

        # Connect to backend. Pass in app and root/master window
        self.backend = Backend(self, self.window)

        # Display Main Menu
        self.mainMenu()

    def mainMenu(self):

        """
        The main menu window.
        :return:
        """

        self.clearFrame()

        self.window.title('Main Menu')

        if self.backend.user is not None:
            self.backend.user = None
            ty_msg = tk.Label(self.window, text='You are logged Out.\n\nThank you for using the Customer Management System!', anchor='center',
                                  font=('bold', 16), pady=10)
            ty_msg.place(relx=0.5, rely=0.9, anchor='center')



        menu_title = tk.Label(self.window, text='Welcome to the Customer Management System', anchor='center', font=('bold', 16), pady=10)
        menu_title.place(relx=0.5, rely=0.2, anchor='center')

        # Admin user Username
        admin_username = tk.StringVar(self.window)
        admin_username_label = tk.Label(self.window, text='Username:', font=('bold', 14), pady=10)
        admin_username_label.place(relx=0.5, rely=0.3, anchor='center')
        admin_username_entry = tk.Entry(self.window, textvariable=admin_username)
        admin_username_entry.place(relx=0.5, rely=0.35, anchor='center')

        # Admin user Password
        admin_pass = tk.StringVar(self.window)
        admin_pass_label = tk.Label(self.window, text='Password:', font=('bold', 14), pady=10)
        admin_pass_label.place(relx=0.5, rely=0.45, anchor='center')
        admin_pass_entry = tk.Entry(self.window, textvariable=admin_pass)
        admin_pass_entry.place(relx=0.5, rely=0.50, anchor='center')

        # Login Button
        login_btn = tk.Button(self.window, text='Log in', width=10,
                              command=lambda: self.backend.login(admin_username.get(), admin_pass.get(), response_msg))
        login_btn.place(relx=0.5, rely=0.60, anchor='center')

        # Response
        response_msg = tk.StringVar(self.window)
        response_label = tk.Label(self.window, text='', textvariable=response_msg, font=(14), pady=10)
        response_label.place(relx=0.5, rely=0.70, anchor='center')

        # Exit button
        exit_btn = tk.Button(self.window, text='Exit', width=8, command=self.exitProgram)
        exit_btn.grid(row=0, column=0)

        return

    # Redo this page with place instead of grid?
    def customerMenu(self):

        """
        The Customer window where customer data can be manipulated.
        :return:
        """

        self.clearFrame()

        self.window.title('Customer Menu')

        self.showUserCredentials()

        # Customer Search
        cust_email = tk.StringVar(self.window)
        cust_email.trace('w', lambda x, y, z: self.backend.autoCompleteEmail(auto_complete_list, cust_email.get()))

        cust_email_label = tk.Label(self.window, text='Search Customer Email', font=('bold', 14), pady=20)
        cust_email_label.grid(row=1, column=0, sticky=tk.W)
        cust_email_entry = tk.Entry(self.window, textvariable=cust_email)
        cust_email_entry.grid(row=1, column=1)
        cust_email_entry.focus()

        # Search button
        search_btn = tk.Button(self.window, text='Search', width=10, command=lambda: self.backend.getCustomerInfo(cust_email.get(), cust_list, delete_btn))
        search_btn.grid(row=1, column=2)

        # Customer Info Label
        view_label = tk.Label(self.window, text='Customer Info', font=('bold', 14), pady=10)
        view_label.place(x=30, y=120)

        # Edit button
        edit_btn = tk.Button(self.window, text='Edit', name='edit_btn', state='disabled', width=8,
                             command=lambda: self.editCustomerWindow())
        edit_btn.grid(row=15, column=0)

        # Edit feedback Message
        edit_fdbk_msg = tk.StringVar(name='edit_fdbk')
        edit_fdbk_label = tk.Label(self.window, textvariable=edit_fdbk_msg, font=('bold', 14), pady=10)
        edit_fdbk_label.grid(row=16, column=0, sticky=tk.W)

        # Customer Info List
        cust_list = tk.Listbox(self.window, height=12, width=50, name='datalist')
        cust_list.grid(row=7, column=0, columnspan=3, rowspan=6, pady=20, padx=20)
        cust_list.bind('<Button-1>', lambda x: self.backend.enableEditBtn())
        cust_list.bind('<FocusIn>', lambda x: self.backend.enableEditBtn())
        cust_list.bind('<FocusOut>', lambda x: self.backend.disableEditBtn())

        # Create scrollbar
        scrollbar = tk.Scrollbar(self.window)
        scrollbar.grid(row=8, column=3)
        # Set scroll to list
        cust_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=cust_list.yview)

        # Buttons
        add_btn = tk.Button(self.window, text='Add Customer', width=15, command=self.addCustomerMenu)
        add_btn.grid(row=2, column=3)

        delete_btn = tk.Button(self.window, text='Delete Customer', name='delete_btn', width=15, state='disabled', command=lambda: self.confirmDeleteCustomerMenu(cust_list, delete_btn))
        delete_btn.grid(row=15, column=1, padx=50, columnspan=3)

        delete_all_btn = tk.Button(self.window, text='Delete All Customers', width=15,
                               command=lambda: self.confirmDeleteAllCustomersMenu(cust_list, delete_all_btn))
        delete_all_btn.grid(row=3, column=3)

        analyze_btn = tk.Button(self.window, text='Analyze Customers', width=15, command=self.customerAnalysisMenu)
        analyze_btn.grid(row=4, column=3)

        # Return
        back_btn = tk.Button(self.window, text='Log out', width=10, command=self.mainMenu)
        back_btn.grid(row=0, column=0)

        # Customer Info
        auto_complete_list = tk.Listbox(self.window, height=4, width=20, name='autocomplete')
        auto_complete_list.bind('<FocusIn>', lambda x: self.backend.selectFromAutoComplete(auto_complete_list, cust_email))
        # cust_list.place(x=188, y=68)

    # In progress. Need to do checks for each data entry before placing into db
    def editCustomerWindow(self):

        """
        Function to edit data in the list box of the currently selected customer.

        :return:
        """

        listbox = self.window.nametowidget('datalist')
        edit_btn = self.window.nametowidget('edit_btn')
        delete_btn = self.window.nametowidget('delete_btn')

        if listbox is None:
            return False

        clicked_items = listbox.curselection()
        if len(clicked_items) > 1 or len(clicked_items) < 1:
            return False
        clicked_item_index = clicked_items[0]

        attribute_to_edit = listbox.get(clicked_item_index)

        attribute = attribute_to_edit.split(':')[0]
        email_info = listbox.get(0)
        email = email_info.split(':')[1]
        email = email[1:]

        editwindow = tk.Toplevel()
        window_width = 350
        window_height = 100
        x_position = (self.screen_width / 2) - (window_width / 2)
        y_position = (self.screen_height / 2) - (window_height / 2)
        editwindow.geometry('%dx%d+%d+%d' % (window_width, window_height, x_position, y_position))
        editwindow.title('Edit Customer')

        # Message
        msg_label = tk.Label(editwindow, text=('Type in the new ' + attribute + '.'), font=('bold', 14))
        msg_label.grid(row=0, column=0, columnspan=3, sticky=tk.W)

        user_input = tk.StringVar()
        edit_entry = tk.Entry(editwindow, textvariable=user_input)
        edit_entry.grid(row=1, column=0)
        edit_entry.focus()

        update_btn = tk.Button(editwindow, text='Update', width=12, command=lambda: self.backend.updateCustomer(attribute, user_input.get(), email, editwindow, listbox, delete_btn))
        update_btn.grid(row=2, column=0)

        cancel_btn = tk.Button(editwindow, text='Cancel', width=12, command=lambda: editwindow.destroy())
        cancel_btn.grid(row=2, column=1)

        # Destroy edit window if there already is one
        edit_btn.bind('<Button-1>', lambda x: editwindow.destroy())

        return

    def addCustomerMenu(self):

        '''
        Window where customers can be added.
        '''

        self.clearFrame()

        self.window.title('Add Customer Menu')

        # Customer email
        cust_email = tk.StringVar(self.window)
        cust_email_label = tk.Label(self.window, text='Email:', font=('bold', 14), pady=10)
        cust_email_label.grid(row=1, column=0, sticky=tk.W)
        cust_email_entry = tk.Entry(self.window, textvariable=cust_email)
        cust_email_entry.grid(row=1, column=1)
        cust_email_entry.focus()

        # Check Button
        check_btn = tk.Button(self.window, text='Check', width=12, command=lambda: self.backend.checkEmailExists(cust_email, check_msg))
        check_btn.grid(row=2, column=0)

        # Check Label
        check_msg = tk.StringVar(self.window)
        check_label = tk.Label(self.window, textvariable=check_msg, font=(14))
        check_label.grid(row=2, column=1, columnspan=3, sticky=tk.W)

        # Customer Password
        cust_pass = tk.StringVar(self.window)
        cust_pass_label = tk.Label(self.window, text='Password:', font=('bold', 14), pady=10)
        cust_pass_label.grid(row=4, column=0, sticky=tk.W)
        cust_pass_entry = tk.Entry(self.window, textvariable=cust_pass)
        cust_pass_entry.grid(row=4, column=1)

        # Customer First name
        cust_fname = tk.StringVar(self.window)
        cust_fname_label = tk.Label(self.window, text='First name:', font=('bold', 14), pady=10)
        cust_fname_label.grid(row=6, column=0, sticky=tk.W)
        cust_fname_entry = tk.Entry(self.window, textvariable=cust_fname)
        cust_fname_entry.grid(row=6, column=1)

        # Customer Last name
        cust_lname = tk.StringVar(self.window)
        cust_lname_label = tk.Label(self.window, text='Last name:', font=('bold', 14), pady=10)
        cust_lname_label.grid(row=8, column=0, sticky=tk.W)
        cust_lname_entry = tk.Entry(self.window, textvariable=cust_lname)
        cust_lname_entry.grid(row=8, column=1)

        countries = ['Canada']
        # Customer Country
        cust_country_label = tk.Label(self.window, text='Country:', font=('bold', 14), pady=10)
        cust_country_label.grid(row=10, column=0, sticky=tk.W)
        cust_country_combo = ttk.Combobox(self.window, values=countries)
        cust_country_combo.set('Select')
        cust_country_combo.grid(row=10, column=1)

        # Customer Region
        cust_region_label = tk.Label(self.window, text='Region:', font=('bold', 14), pady=10)
        cust_region_label.grid(row=12, column=0, sticky=tk.W)
        regions = self.backend.getRegions()
        cust_region_combo = ttk.Combobox(self.window, values=regions)
        cust_region_combo.set('Select')
        cust_region_combo.grid(row=12, column=1)

        # Customer Address
        cust_address = tk.StringVar(self.window)
        cust_address_label = tk.Label(self.window, text='Address:', font=('bold', 14), pady=10)
        cust_address_label.grid(row=14, column=0, sticky=tk.W)
        cust_address_entry = tk.Entry(self.window, textvariable=cust_address)
        cust_address_entry.grid(row=14, column=1)

        # Customer DOB
        cust_DOB = tk.StringVar(self.window)
        cust_DOB_label = tk.Label(self.window, text='Date of birth:', font=('bold', 14), pady=10)
        cust_DOB_label.grid(row=16, column=0, sticky=tk.W)
        cust_DOB_entry = tk.Entry(self.window, textvariable=cust_DOB)
        cust_DOB_entry.grid(row=16, column=1)

        # Limit and current Label
        limit_current_msg = tk.StringVar(self.window)
        limit_current_msg.set('Limit: ' + str(self.backend.recordLimit) + '  ' + 'Current: ' + str(
            self.backend.db.selectNumberOfCustomerRecords()[0][0]))
        limit_current_label = tk.Label(self.window, textvariable=limit_current_msg, font=('bold', 14))
        limit_current_label.grid(row=6, column=2, columnspan=12, padx=60, sticky=tk.W)

        # Add Customer button
        add_btn = tk.Button(self.window, text='Add Customer', width=12, command=lambda: self.backend.addCustomer(cust_email, cust_pass, cust_fname, cust_lname, cust_country_combo, cust_region_combo, cust_address, feedback_msg, cust_DOB, check_msg, limit_current_msg))
        add_btn.grid(row=18, column=0)

        # Feedback Label for manual generation
        feedback_msg = tk.StringVar(self.window)
        feedback_label = tk.Label(self.window, textvariable=feedback_msg, justify='left', font=(14), pady=10)
        feedback_label.grid(row=22, column=0, columnspan=3, sticky=tk.W)

        # Create entry for N records
        number_input = tk.StringVar(self.window)
        number_label = tk.Label(self.window, text='Number of records:', font=('bold', 14))
        number_label.grid(row=1, column=2, padx=60, sticky=tk.W)
        number_entry = tk.Entry(self.window, textvariable=number_input)
        number_entry.grid(row=2, column=2, pady=10, padx=60)

        # Feedback Label for random generation
        feedback_rand_msg = tk.StringVar(self.window)
        feedback_rand_label = tk.Label(self.window, textvariable=feedback_rand_msg, font=(14))
        feedback_rand_label.grid(row=8, column=2, columnspan=12, padx=60, sticky=tk.W)

        generate_btn = tk.Button(self.window, text='Generate random customers', width=22, command=lambda: self.backend.generateRandomCustomers(number_input, feedback_rand_msg, limit_current_msg))
        generate_btn.grid(row=3, column=2, rowspan=2, padx=60)

        # Return
        add_btn = tk.Button(self.window, text='<- Customer Menu', width=14, command=self.customerMenu)
        add_btn.grid(row=0, column=0)

    def confirmDeleteCustomerMenu(self, cust_list, parent_delete_btn):

        """
        Window to confirm if user wants to delete customer.
        :param cust_list: The widget that contains the customer's information.
        :return: Successfulness of function.
        """
        value = cust_list.get(0)

        if 'Email' not in value:
            cust_list.delete(0, 'end')
            cust_list.insert(0, 'Search a customer first in order to delete')
            return False

        confirmWindow = tk.Toplevel()
        window_width = 350
        window_height = 100
        x_position = (self.screen_width / 2) - (window_width / 2)
        y_position = (self.screen_height / 2) - (window_height / 2)
        confirmWindow.geometry('%dx%d+%d+%d' % (window_width, window_height, x_position, y_position))
        confirmWindow.title('Delete Customer')

        email = value.split(':')[1]

        # Confirmation Message
        confirm_label = tk.Label(confirmWindow,
                                 text=('Are you sure you want to delete this customer?\n Email: ' + email),
                                 font=('bold', 14))
        confirm_label.grid(row=0, column=0, columnspan=3, sticky=tk.W)

        delete_btn = tk.Button(confirmWindow, text='Delete', width=12,
                               command=lambda: self.backend.deleteCustomer(cust_list, confirmWindow))
        delete_btn.grid(row=1, column=1)

        remove_btn = tk.Button(confirmWindow, text='Cancel', width=12, command=lambda: confirmWindow.destroy())
        remove_btn.grid(row=1, column=2)

        parent_delete_btn.bind('<Button-1>', lambda x: confirmWindow.destroy())

        return True

    def confirmDeleteAllCustomersMenu(self, cust_list, parent_delete_all_btn):

        """
        Window to confirm if user wants to delete customer.
        :param cust_list: The widget that contains the customer's information.
        :return: Successfulness of function.
        """

        confirmWindow = tk.Toplevel()
        window_width = 350
        window_height = 100
        x_position = (self.screen_width / 2) - (window_width / 2)
        y_position = (self.screen_height / 2) - (window_height / 2)
        confirmWindow.geometry('%dx%d+%d+%d' % (window_width, window_height, x_position, y_position))
        confirmWindow.title('Delete All Customers')

        data = self.backend.db.selectNumberOfCustomerRecords()

        if data[0][0] == 0:
            # There are no records message
            confirm_label = tk.Label(confirmWindow,
                                     text=('There are no customer records.'),
                                     font=('bold', 14))
            confirm_label.grid(row=0, column=0, columnspan=3, sticky=tk.W)

            remove_btn = tk.Button(confirmWindow, text='OK', width=12, command=lambda: confirmWindow.destroy())
            remove_btn.grid(row=1, column=2)
            return True
        else:
            # Confirmation Message
            confirm_label = tk.Label(confirmWindow,
                                     text=('Are you sure you want to delete all customers?'),
                                     font=('bold', 14))
            confirm_label.grid(row=0, column=0, columnspan=3, sticky=tk.W)

            delete_btn = tk.Button(confirmWindow, text='Delete', width=12, command=lambda: self.backend.deleteAllCustomers(cust_list, confirmWindow))
            delete_btn.grid(row=1, column=1)

            remove_btn = tk.Button(confirmWindow, text='Cancel', width=12, command=lambda: confirmWindow.destroy())
            remove_btn.grid(row=1, column=2)

        parent_delete_all_btn.bind('<Button-1>', lambda x: confirmWindow.destroy())
        return True

    def confirmEditWindow(self, editWindow):

        for widget in editWindow.winfo_children():
            widget.destroy()

        # Message
        msg_label = tk.Label(editWindow, text='Edit has been made.', font=('bold', 14))
        msg_label.grid(row=0, column=0, columnspan=3, sticky=tk.W)

        return

    def customerAnalysisMenu(self):

        """
        Window that provides features to analyze the current customer data.

        :return:
        """

        self.clearFrame()
        self.window.title("Customer Analysis Menu")

        # Label
        loading_msg = tk.StringVar(self.window)
        loading_msg.set('Select a visualization')
        cust_label = tk.Label(self.window, textvariable=loading_msg, font=('bold', 14), pady=10)
        cust_label.grid(row=0, column=1, sticky=tk.W)

        # Buttons
        age_btn = tk.Button(self.window, text='Age demographic', width=15, command=lambda: self.backend.plotCustomerAge(loading_msg))
        age_btn.grid(row=2, column=0, pady=10)

        age_btn = tk.Button(self.window, text='Region demographic', width=15, command=lambda: self.backend.plotCustomerRegion(loading_msg))
        age_btn.grid(row=4, column=0, pady=10)

        # Return
        add_btn = tk.Button(self.window, text='<- Customer Menu', width=14, command=self.customerMenu)
        add_btn.grid(row=0, column=0)

    def showUserCredentials(self):

        """
        Function to display the current users username on the bottom left of the screen
        :return:
        """

        # Credentials label
        current_admin_label = tk.Label(self.window, text='Logged in as ' + self.backend.user, font=('bold', 14))
        current_admin_label.place(relx=0.01, rely=0.95)

    def clearFrame(self):

        """
        Function to clear the Frame/Window of any widgets. This is typically called when changing menus.
        :return:
        """

        for widget in self.window.winfo_children():
            widget.destroy()

    def exitProgram(self):

        """
        Function to close the app mainloop() gracefully.
        """
        self.window.destroy()
        sys.exit()

if __name__ == '__main__':

    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
