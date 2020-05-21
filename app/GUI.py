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
        self.window_width = 750
        self.window_height = 650

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
        The main menu window. Users can log in with their credentials through this page. New users can also
        request an account by entering their emailing and await approval from the admin. Once approved, new users
        will receive their credentials through their email.
        :return:
        """

        self.clearFrame()

        self.window.title('Main Menu')

        if self.backend.user is not '':
            self.backend.user = ''
            ty_msg = tk.Label(self.window, text='You are logged Out.\n\nThank you for using the Customer Management System!', anchor='center',
                                  font=('bold', 16), pady=10)
            ty_msg.place(relx=0.5, rely=0.9, anchor='center')

        # Create the main frame that will act as the container
        main_frame = tk.Frame(self.window, width=750, height=650, name='main_menu_main_frame')
        main_frame.place(relx=0, rely=0)

        menu_title = tk.Label(main_frame, text='Welcome to the Customer Management System', anchor='center', font=('bold', 16), pady=13)
        menu_title.place(relx=0.5, rely=0.1, anchor='center')

        # Admin user Username
        admin_username = tk.StringVar(main_frame)
        admin_username_label = tk.Label(main_frame, text='Username:', font=('bold', 14))
        admin_username_label.place(relx=0.5, rely=0.2, anchor='center')
        admin_username_entry = tk.Entry(main_frame, textvariable=admin_username)
        admin_username_entry.place(relx=0.5, rely=0.23, anchor='center')

        # Admin user Password
        admin_pass = tk.StringVar(main_frame)
        admin_pass_label = tk.Label(main_frame, text='Password:', font=('bold', 14))
        admin_pass_label.place(relx=0.5, rely=0.3, anchor='center')
        admin_pass_entry = tk.Entry(main_frame, textvariable=admin_pass)
        admin_pass_entry.place(relx=0.5, rely=0.33, anchor='center')

        # Login Button
        login_btn = tk.Button(main_frame, text='Log in', width=10,
                              command=lambda: self.backend.login(admin_username.get(), admin_pass.get(), response_msg))
        login_btn.place(relx=0.5, rely=0.4, anchor='center')

        # Response
        response_msg = tk.StringVar(main_frame)
        response_label = tk.Label(main_frame, text='', textvariable=response_msg, font=(14))
        response_label.place(relx=0.5, rely=0.45, anchor='center')

        # Request
        response_label = tk.Label(main_frame, text='Request Account', font=('bold', 16))
        response_label.place(relx=0.5, rely=0.54, anchor='center')

        # Email request
        email = tk.StringVar(main_frame)
        email_label = tk.Label(main_frame, text='Email:', font=('bold', 14))
        email_label.place(relx=0.5, rely=0.60, anchor='center')
        email_entry = tk.Entry(main_frame, textvariable=email)
        email_entry.place(relx=0.5, rely=0.63, anchor='center')

        # Request Button
        request_btn = tk.Button(main_frame, text='Request', width=10,
                              command= lambda: self.backend.submitRequest(email.get(), request_rsp))
        request_btn.place(relx=0.5, rely=0.69, anchor='center')

        # Response
        request_rsp = tk.StringVar(main_frame)
        request_rsp_label = tk.Label(main_frame, text='', textvariable=request_rsp, font=(14))
        request_rsp_label.place(relx=0.5, rely=0.74, anchor='center')

        # Exit button
        exit_btn = tk.Button(main_frame, text='Exit', width=8, command=self.exitProgram)
        exit_btn.place(relx=0, rely=0)

        return

    def adminMenu(self):

        """
        The administrator menu exclusively accessible to the admin of the application.
        Allows unique access to user management and to regular customer management

        :return:
        """

        self.clearFrame()

        self.window.title('Admin Menu')

        self.showUserCredentials()

        # Button to go to customer menu
        customer_menu_btn = tk.Button(self.window, text='Manage Customers', width=15, command=self.customerMenu)
        customer_menu_btn.place(relx=0.80, rely=0.0)

            # REQUESTS

        # Request Notification
        request_notification = tk.StringVar(self.window)
        request_notify_label = tk.Label(self.window, textvariable=request_notification, font=14)
        request_notify_label.place(relx=0.4, rely=0.05)

        # Requests Label
        requests_label = tk.Label(self.window, text='Requests:', font=('bold', 14))
        requests_label.place(relx=0.05, rely=0.10)

        # Customer Info List
        request_list = tk.Listbox(self.window, height=12, width=50, name='requests')
        request_list.place(relx=0.05, rely=0.15)
        request_list.bind('<Button-1>', lambda x: self.backend.enableApproveAndDeclineBtn(request_feedback))
        request_list.bind('<FocusIn>', lambda x: self.backend.enableApproveAndDeclineBtn(request_feedback))
        request_list.bind('<FocusOut>', lambda x: self.backend.disableApproveAndDeclineBtn(request_feedback))
        self.backend.getRequests(request_list, request_notification)

        # Approve btn
        approve_btn = tk.Button(self.window, text='Approve', name='approve_btn', width=10, command=lambda: self.backend.approveUser(request_notification, request_feedback, login_var, edit_var, delete_var, delete_all_var, add_var, analyze_var))
        approve_btn.place(relx=0.7, rely=0.16)
        approve_btn['state'] = 'disabled'

        # Decline btn
        decline_btn = tk.Button(self.window, text='Decline', name='decline_btn', width=10,
                                command=lambda: self.backend.declineUser(request_notification, request_feedback, login_var, edit_var, delete_var, delete_all_var, add_var, analyze_var))
        decline_btn.place(relx=0.7, rely=0.22)
        decline_btn['state'] = 'disabled'

        # Feedback to approval or decline
        request_feedback = tk.StringVar(self.window)
        request_feedback_label = tk.Label(self.window, textvariable=request_feedback, font=14)
        request_feedback_label.place(relx=0.05, rely=0.47)

            # PERMISSIONS

        # Permissions Label
        requests_label = tk.Label(self.window, text='Permissions:', font=('bold', 14))
        requests_label.place(relx=0.05, rely=0.55)

        # Permissions
        login_var = tk.IntVar(self.window)
        login_checkbox = tk.Checkbutton(self.window, name='login_permission', text="Login", variable=login_var)
        login_checkbox.place(relx=0.05, rely=0.6)
        login_checkbox['state'] = 'disabled'

        edit_var = tk.IntVar(self.window)
        edit_checkbox = tk.Checkbutton(self.window, name='edit_permission', text="Edit Customers", variable=edit_var)
        edit_checkbox.place(relx=0.05, rely=0.65)
        edit_checkbox['state'] = 'disabled'

        delete_var = tk.IntVar(self.window)
        delete_checkbox = tk.Checkbutton(self.window, name='delete_permission', text="Delete Customers", variable=delete_var)
        delete_checkbox.place(relx=0.05, rely=0.7)
        delete_checkbox['state'] = 'disabled'

        delete_all_var = tk.IntVar(self.window)
        delete_all_checkbox = tk.Checkbutton(self.window, name='delete_all_permission', text="Delete All Customers", variable=delete_all_var)
        delete_all_checkbox.place(relx=0.05, rely=0.75)
        delete_all_checkbox['state'] = 'disabled'

        add_var = tk.IntVar(self.window)
        add_checkbox = tk.Checkbutton(self.window, name='add_permission', text="Add Customers", variable=add_var)
        add_checkbox.place(relx=0.05, rely=0.8)
        add_checkbox['state'] = 'disabled'

        analyze_var = tk.IntVar(self.window)
        analyze_checkbox = tk.Checkbutton(self.window, name='analyze_permission', text="Analyze Customers", variable=analyze_var)
        analyze_checkbox.place(relx=0.05, rely=0.85)
        analyze_checkbox['state'] = 'disabled'

            # USER SEARCH

        # User Search
        user = tk.StringVar(self.window)
        user.trace('w', lambda x, y, z: self.backend.autoCompleteUser(auto_complete_list, user.get(), user_fdbk, login_var, edit_var, delete_var, delete_all_var, add_var, analyze_var))

        user_label = tk.Label(self.window, text='Search user:', width=10, font=('bold', 14))
        user_label.place(relx=0.65, rely=0.55, )
        user_entry = tk.Entry(self.window, textvariable=user)
        user_entry.place(relx=0.66, rely=0.60)

        # Search button
        search_btn = tk.Button(self.window, text='Search', width=10, name='search_user_btn',
                               command=lambda: self.backend.searchUser(user.get(), login_var, edit_var, delete_var, delete_all_var, add_var, analyze_var, user_fdbk))
        search_btn.place(relx=0.79, rely=0.55)

        # Search feedback
        user_fdbk = tk.StringVar(self.window)
        search_fdbk_label = tk.Label(self.window, textvariable=user_fdbk, font=14)
        search_fdbk_label.place(relx=0.66, rely=0.76)

        # Change permission button
        change_btn = tk.Button(self.window, text='Apply changes', width=13, name='change_permissions_btn',
                               command=lambda: self.backend.changeUserPermissions(user.get(), login_var, edit_var, delete_var, delete_all_var, add_var, analyze_var, user_fdbk))
        change_btn.place(relx=0.66, rely=0.85)
        change_btn['state'] = 'disabled'

        # Delete user button
        delete_user_btn = tk.Button(self.window, text='Delete user', width=13, name='delete_user_btn',
                               command=lambda: self.backend.deleteUser(user.get(), user_fdbk))
        delete_user_btn.place(relx=0.82, rely=0.85)
        delete_user_btn['state'] = 'disabled'

        # Customer Info
        auto_complete_list = tk.Listbox(self.window, height=4, width=20, name='autocomplete')
        auto_complete_list.bind('<FocusIn>',
                                lambda x: self.backend.selectFromAutoCompleteUser(auto_complete_list, user))


        # log out
        logout_btn = tk.Button(self.window, text='Log out', width=10, command=self.mainMenu)
        logout_btn.place(relx=0, rely=0)

        return

    def customerMenu(self):

        """
        The Customer window where customer data can be manipulated.
        :return:
        """

        self.clearFrame()

        self.window.title('Customer Menu')

        self.showUserCredentials()

        if self.backend.user == 'admin':
            # admin menu
            admin_menu_btn = tk.Button(self.window, text='Admin menu', width=10, command=self.adminMenu)
            admin_menu_btn.place(relx=0.15, rely=0)

        # This is so that buttons always appear one after another. They change y position dynamically according
        # to the user's permission setting that determines what buttons will be available
        ycoordinate = 0.1
        ycoordinateIncr = 0.05
        xcoordinate = 0.8

        # Customer Search
        cust_email = tk.StringVar(self.window)
        cust_email.trace('w', lambda x, y, z: self.backend.autoCompleteEmail(auto_complete_list, cust_email.get()))

        cust_email_label = tk.Label(self.window, text='Search Customer Email:', font=('bold', 14))
        cust_email_label.place(relx=0.05, rely=0.1,)
        cust_email_entry = tk.Entry(self.window, textvariable=cust_email)
        cust_email_entry.place(relx=0.30, rely=0.1)
        cust_email_entry.focus()

        # Search button
        search_btn = tk.Button(self.window, text='Search', width=10,
                               command=lambda: self.backend.getCustomerInfo(cust_email.get(), cust_list, delete_btn))
        search_btn.place(relx=0.6, rely=0.105)

        # Customer Info Label
        view_label = tk.Label(self.window, text='Customer Info:', font=('bold', 14))
        view_label.place(relx=0.05, rely=0.2)

        # Edit button
        edit_btn = tk.Button(self.window, text='Edit', name='edit_btn', state='disabled', width=8,
                             command=lambda: self.editCustomerWindow())
        if self.backend.permissions['edit_customer_btn'] == 1:
            edit_btn.place(relx=0.05, rely=0.62)

        # Customer Info List
        cust_list = tk.Listbox(self.window, height=12, width=50, name='datalist')
        cust_list.place(relx=0.05, rely=0.26)
        cust_list.bind('<Button-1>', lambda x: self.backend.enableEditBtn())
        cust_list.bind('<FocusIn>', lambda x: self.backend.enableEditBtn())
        cust_list.bind('<FocusOut>', lambda x: self.backend.disableEditBtn())

        # Create scrollbar
        scrollbar = tk.Scrollbar(self.window)
        scrollbar.place(relx=0.75, rely=0.26)
        # Set scroll to list
        cust_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=cust_list.yview)

        add_btn = tk.Button(self.window, text='Add New Customer', width=15, command=self.addCustomerMenu)
        if self.backend.permissions['add_customer_btn'] == 1:
            add_btn.place(relx=xcoordinate, rely=ycoordinate)
            ycoordinate += ycoordinateIncr

        delete_btn = tk.Button(self.window, text='Delete Customer', name='delete_btn', width=15, state='disabled',
                                   command=lambda: self.confirmDeleteCustomerMenu(cust_list, delete_btn))
        if self.backend.permissions['delete_customer_btn'] == 1:
            delete_btn.place(relx=0.53, rely=0.62)

        delete_all_btn = tk.Button(self.window, text='Delete All Customers', width=15,
                                   command=lambda: self.confirmDeleteAllCustomersMenu(cust_list, delete_all_btn))
        if self.backend.permissions['delete_all_customer_btn'] == 1:
            delete_all_btn.place(relx=xcoordinate, rely=ycoordinate)
            ycoordinate += ycoordinateIncr

        analyze_btn = tk.Button(self.window, text='Analyze Customers', width=15, command=self.customerAnalysisMenu)
        if self.backend.permissions['analyze_customer_btn'] == 1:
            analyze_btn.place(relx=xcoordinate, rely=ycoordinate)
            ycoordinate += ycoordinateIncr

        # log out
        logout_btn = tk.Button(self.window, text='Log out', width=10, command=self.mainMenu)
        logout_btn.place(relx=0, rely=0)

        # Customer Info
        auto_complete_list = tk.Listbox(self.window, height=4, width=20, name='autocomplete')
        auto_complete_list.bind('<FocusIn>',
                                lambda x: self.backend.selectFromAutoComplete(auto_complete_list, cust_email))

        return

    def editCustomerWindow(self):

        """
        Function to edit data in the list box of the currently selected customer.

        :return:
        """

        listbox = self.window.nametowidget('datalist')
        edit_btn = self.window.nametowidget('edit_btn')
        delete_btn = self.window.nametowidget('delete_btn')

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

    # Change to place instead of grid. Add seperator in middle and add labels on top for "Manual" and "Random/Auto"
    def addCustomerMenu(self):

        '''
        Window where customers can be added.
        '''

        self.clearFrame()

        self.window.title('Add Customer Menu')

        self.showUserCredentials()

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

        # # Separator
        # separator = ttk.Separator(self.window)
        # separator.grid(column=2, sticky='ew', rowspan=12)

        # Create entry for N records
        number_input = tk.StringVar(self.window)
        number_label = tk.Label(self.window, text='Number of records:', font=('bold', 14))
        number_label.grid(row=1, column=3, padx=60, sticky=tk.W)
        number_entry = tk.Entry(self.window, textvariable=number_input)
        number_entry.grid(row=2, column=3, pady=10, padx=60)

        # Feedback Label for random generation
        feedback_rand_msg = tk.StringVar(self.window)
        feedback_rand_label = tk.Label(self.window, textvariable=feedback_rand_msg, font=(14))
        feedback_rand_label.grid(row=8, column=3, columnspan=12, padx=60, sticky=tk.W)

        generate_btn = tk.Button(self.window, text='Generate random customers', width=22, command=lambda: self.backend.generateRandomCustomers(number_input, feedback_rand_msg, limit_current_msg))
        generate_btn.grid(row=3, column=3, rowspan=2, padx=60)

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
        x_position = self.window.winfo_rootx() + (self.window_width/2) - (window_width/2)
        y_position = self.window.winfo_rooty() + (self.window_height/2) - (window_height/2) - 20
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
        x_position = self.window.winfo_rootx() + (self.window_width / 2) - (window_width / 2)
        y_position = self.window.winfo_rooty() + (self.window_height / 2) - (window_height / 2) - 20
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
        self.showUserCredentials()

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

    def animateLogin(self):

        main_menu_main_frame = self.window.nametowidget('main_menu_main_frame')

        main_menu_main_frame.place(rely=-0.01, relx=0)
        self.window.update()

        main_menu_main_frame.place(rely=-0.02, relx=0)
        self.window.update()

        main_menu_main_frame.place(rely=-0.04, relx=0)
        self.window.update()

        main_menu_main_frame.place(rely=-0.08, relx=0)
        self.window.update()

        main_menu_main_frame.place(rely=-0.16, relx=0)
        self.window.update()

        main_menu_main_frame.place(rely=-0.32, relx=0)
        self.window.update()

        main_menu_main_frame.place(rely=-0.64, relx=0)
        self.window.update()

        main_menu_main_frame.place(rely=-0.90, relx=0)
        self.window.update()

        main_menu_main_frame.place(rely=-0.95, relx=0)
        self.window.update()

        main_menu_main_frame.place(rely=-0.975, relx=0)
        self.window.update()

        main_menu_main_frame.place(rely=-0.99, relx=0)
        self.window.update()

        main_menu_main_frame.place_forget()
        self.window.update()

        return

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
