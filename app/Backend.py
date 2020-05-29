# Local dependencies
from db import Database
from Utils import *
import Scripts
import random
#

# External dependencies
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pickle
#

# Dependency for email
import smtplib

# External dependencies for regional map visualization
import pandas
import matplotlib
matplotlib.use('tkAgg')
from matplotlib import pyplot
#

class Backend:

    """
    Class that contains all the logistics of manipulating widgets and data.

    TODO:
    FINISH DOCUMENTATION
    """

    def __init__(self, app, window):

        # Application (front end) instance
        self.app = app

        # Root window instance from the main app
        self.window = window

        # Instantiate database object
        self.db = Database('Database1.db')

        # Connect to utilities
        self.utils = Utils()

        # Get access to scripts
        self.scripts = Scripts.Scripts(self.db)

        # The limit to number of records in the Customer table
        # Warning: If you increase limit, need to add more names in names.txt
        self.recordLimit = 1000

        # Current user username
        self.user = ''

        # Current user's permissions in the application
        self.permissions = {}

        # Email setting
        self.email = False

    def login(self, user_username, user_password, response_msg):

        """
        Function to validate user credentials and allow access if they exist and match in the user
        Table in the database.

        :param user_username: Entered username as string
        :param user_password: Entered password as string
        :param response_msg: The label instance to provide feedback to user
        :return: Successfulness of function
        """

        # No input
        if user_username == '' and user_password == '':
            return

        # Check username and password
        response = self.db.validateUserLoginCredentials(user_username, user_password)

        # Username and password did not match
        if len(response) == 0:
            response_msg.set('That username and password did not match.')
            return False

        # Get permissions of user
        self.permissions = self.db.getPermissions(user_username)

        # User has a record in user table but permissions have not been set
        if len(self.permissions) < 1:
            response_msg.set('Please contact the administrator')
            return False

        # If its admin, go to admin menu
        if user_username == 'admin':
            self.user = user_username
            self.app.adminMenu()
            return True
        else:
            # Allow login if user has permission
            if self.permissions['login'] == 1:
                self.user = user_username
                self.app.customerMenu()
            else:
                response_msg.set('Cannot log you in.')
                return False

        return True

    def checkEmailExists(self, email, check_msg):

        """
        This function takes in the StringVar() object from the email label and checks if there exists such an
        email in the database. It then returns the response by manipulating the check_msg StringVar() object.

        :param email:
        :param check_msg:
        :return:
        """

        if email.get() == '':
            check_msg.set('Enter an email.')
            return False

        data = self.db.getCustomerInfo(email.get())

        if len(data) < 1:
            output = "Email OK"
            check_msg.set(output)
            return False
        else:
            output = "That email already exists."
            check_msg.set(output)
            return True

    def getCustomerInfo(self, email, cust_list, delete_btn):

        """
        Function to get customer data from the Customer Relation using the primary key, email.

        :param email: The customer's unique email -> str
        :param cust_list
        :param delete_btn
        :return: Successfulness of function -> boolean
        """

        if email is '':
            return False

        delete_btn['state'] = 'disabled'

        data = self.db.getCustomerInfo(email)

        # Clear widget of any text
        cust_list.delete(0, 'end')

        if data is False:
            output = "Something went wrong."
            cust_list.insert(1, output)
            return False

        # Check if email exists in db
        if len(data) < 1:
            output = "That email does not exist."
            cust_list.insert(1, output)
            return False

        # Convert all data to strings
        stringData = self.utils.convertToStrings(list(data[0]))

        customerTableAttributes = ['Email: ', 'Password: ', 'First name: ', 'Last name: ', 'Country: ', 'Region: ', 'Address: ',
                                   'Postal Code: ', 'Balance: ', 'Preferred card: ', 'Rating: ', 'Status: ', 'Cycle date: ',
                                   'Subscription Type: ', 'Birthday: ']

        for i, value in enumerate(stringData):
            if value is None:
                continue
            if customerTableAttributes[i] is 'Region: ':
                value = self.db.getErnameFromEruid(value)[0][0]
            output = customerTableAttributes[i] + value
            cust_list.insert(i, output)

        delete_btn['state'] = 'normal'

        return True

    def addCustomer(self, email, pword, fname, lname, country, region, address, feedback_msg, dob, check_msg, limit_current_msg):

        """
        This function takes in the StringVar() objects, and Combobox() object, from the root window and uses
        them to get the values stored inside.
        If entries are valid, customer record is added and entry fields are then made empty to clean up the window.
        if entries are invalid, feedback_msg is updated with corresponding issues.

        True = Success
        False = Issue

        :param email:
        :param pword:
        :param fname:
        :param lname:
        :param country:
        :param region:
        :param address:
        :param feedback_msg:
        :param dob:
        :param check_msg:
        :param limit_current_msg:
        :return: Successivefulness of function
        """

        supportedCountries = ['Canada']

        inputList = [email, pword, fname, lname, country, region, address, dob]

        inputIntoListOfStrings = [email.get(), pword.get(), fname.get(), lname.get(), country.get(), region.get(), address.get(), dob.get()]

        data = self.db.getEruidFromErname(region.get())

        if data is False:
            feedback_msg.set('Something wrong with region name')
            return False

        nbCurrentCustomers = self.db.selectNumberOfCustomerRecords()[0][0]

        outputIssue= 'Issues:\n\n'
        outputIssue1 = ''
        outputIssue2 = ''
        outputIssue3 = ''
        outputIssue4 = ''
        outputIssue5 = ''
        outputIssue6 = ''
        issues = 0

        if nbCurrentCustomers >= self.recordLimit:
            issues += 1
            outputIssue1 = '    ' + str(issues) + '. ' + str(self.recordLimit) + ' Record limit reached.\n'

        if self.checkEmailExists(email, feedback_msg):
            issues += 1
            outputIssue2 = '    ' + str(issues) + '. That email already exists.\n'

        if self.utils.checkForEmptyStrings(inputIntoListOfStrings):
            issues += 1
            outputIssue3 = '    ' + str(issues) + '. There cannot be an empty field.\n'

        if country.get() not in supportedCountries:
            issues += 1
            outputIssue4 = '    ' + str(issues) + '. Country not selected.\n'

        if len(data) == 0:
            issues += 1
            outputIssue5 = '    ' + str(issues) + '. Region not selected.\n'
        else:
            eruid = data[0][0]

        if not self.utils.isValidDate(dob.get()):
            issues += 1
            outputIssue6 = '    ' + str(issues) + '. Not a valid date (yyyy-mm-dd).\n'

        # If no issues, insert into db, provide success message, and clear text fields.
        if issues == 0:
            if self.db.insertCustomer(email.get(), pword.get(), fname.get(), lname.get(), country.get(), eruid, address.get(), dob.get()):
                for strvar in inputList:
                    strvar.set('')
                check_msg.set('')
                feedback_msg.set('Customer successively added.')
                nbCurrentCustomers = self.db.selectNumberOfCustomerRecords()[0][0]
                limit_current_msg.set('Limit: ' + str(self.recordLimit) + '  ' + 'Current: ' + str(nbCurrentCustomers))
                return True
        else:
            feedback_msg.set(outputIssue + outputIssue1 + outputIssue2 + outputIssue3 + outputIssue4 + outputIssue5 + outputIssue6)
            return False

    def deleteCustomer(self, cust_list, confirmWindow):

        """
        Function to delete the selected customer in cust_list listbox.

        :param cust_list: The listbox() object with the customer data
        :return: Successfulness of function
        """

        valueInCustList = cust_list.get(0)
        cust_list.delete(0, 'end')

        if 'Email' not in valueInCustList:
            cust_list.insert(0, 'Search an existing customer first in order to delete')
            return False

        valueSplit = valueInCustList.split(': ')
        email = valueSplit[1]

        if self.db.deleteCustomer(email):
            cust_list.insert(0,'Customer successively deleted')
            confirmWindow.destroy()
            return True
        else:
            cust_list.insert(0,'Something went wrong. Customer could not be deleted.')
        return False

    def deleteAllCustomers(self, cust_list, confirmWindow):

        """
        Function to delete all customers in cust_list listbox.

        :param cust_list: The Listbox() object with customer data.
        :return: Successfulness of function
        """
        cust_list.delete(0, 'end')

        if self.db.deleteAllCustomers():
            cust_list.insert(0,'All customers successively deleted')
            confirmWindow.destroy()
            return True
        else:
            cust_list.insert(0,'Something went wrong. Customers could not be deleted.')
        return False

    def autoCompleteEmail(self, autoCompleteList, user_input):

        """
        Function to populate dropdown list with emails that begin with the string in user_input.

        :param autoCompleteList: A tkinter listbox
        :param user_input: The string given by the user
        :return:
        """

        # Hide and clear widget of any text
        autoCompleteList.delete(0, 'end')
        autoCompleteList.place_forget()

        # Do nothing if input is empty
        if user_input is '':
            return

        # Get emails that begin with user_input string
        data = self.db.emailsBeginningWith(user_input)

        # If there are no emails. Do nothing
        if len(data) < 1:
            return

        # Populate list
        for i, email in enumerate(data):
            autoCompleteList.insert(i, email)

        # Display list
        autoCompleteList.place(x=230, y=90)

        return True

    def selectFromAutoComplete(self, autoCompleteList, user_input_field):

        """
        Function to populate the user_input_field, which is an entry, with the email selected by the user.
        The email is selected from the autoCompleteList listbox object.

        :param autoCompleteList: A listbox containing emails
        :param user_input_field: The entry field for searching customers
        :return:
        """

        # Ensure 1 and only 1 email is selected from list
        clicked_items = autoCompleteList.curselection()
        if len(clicked_items) > 1 or len(clicked_items) < 1:
            return False

        # Get email from list
        clicked_item_index = clicked_items[0]
        selected_email = autoCompleteList.get(clicked_item_index)[0]

        # Set entry value to email
        user_input_field.set(selected_email)

        # Hide listbox
        autoCompleteList.place_forget()

        return True

    def updateCustomer(self, attribute, user_input, email, editWindow, cust_list, delete_btn):

        """
        Function to update customer record data that user has input through edit window.

        :param attribute:
        :param user_input:
        :param email:
        :param editWindow:
        :param cust_list:
        :param delete_btn:
        :return:
        """

        if user_input == '':
            return

        # Dictionary mapping of the column names to their front end equivalent name
        attributes = {'Email': 'email',
                      'Password': 'pword',
                      'First name': 'fname',
                      'Last name': 'lname',
                      'Country': 'country',
                      'Region': 'region',
                      'Address': 'address',
                      'Postal Code': 'postalcode',
                      'Balance': 'balance',
                      'Preferred card': 'preferredcard',
                      'Rating': 'rating',
                      'Status': 'status',
                      'Cycle date': 'cycledate',
                      'Subscription Type': 'typename',
                      'Birthday': 'bday',
                      }

        # Get column name from front end equivalent name
        attribute = attributes[attribute]

        # Update customer data
        data = self.db.updateCustomer(attribute, user_input, email)

        if data is False:
            print('Could not update customer info.')
            return False

        self.getCustomerInfo(email, cust_list, delete_btn)
        self.app.confirmEditWindow(editWindow)

        return True

    def enableEditBtn(self):

        """
        Function to enable edit button if user selects one and only one item in the list box.

        :return:
        """

        edit_btn = self.window.nametowidget('edit_btn')
        list_box = self.window.nametowidget('datalist')

        # Check if selected more than 1 item or no items
        clicked_items = list_box.curselection()
        if len(clicked_items) > 1 or len(clicked_items) < 1:
            return False
        clicked_item_index = clicked_items[0]

        selected_info = list_box.get(clicked_item_index)

        if 'Email' in selected_info:
            return

        if ':' in selected_info:
            edit_btn['state'] = 'normal'
            self.window.update()

        return True

    def disableEditBtn(self):

        """
        Function to disable edit button in customer menu
        :return:
        """

        edit_btn = self.window.nametowidget('edit_btn')
        edit_btn['state'] = 'disabled'
        self.window.update()
        return

    def generateRandomCustomers(self, number_input, feedback_msg, limit_current_msg):

        """
        Generates random customer records equal to the number_input argument.
        This uses the generateCustomers() script.

        :param number_input: The number of records to generate
        :param feedback_msg: The StringVar() object from the gui
        :param limit_current_msg:
        :return: Successfulness of function
        """

        # Computation in progress feedback message
        feedback_msg.set('Generating...')
        self.window.update()

        number_input_String = number_input.get()
        number_input_String = number_input_String.lstrip('0')

        if number_input_String.isdigit():
            number_input_Int = int(number_input.get())
        else:
            feedback_msg.set('Please enter a number.')
            return False

        if number_input_Int < 1:
            feedback_msg.set('Please enter a value greater than 0.')
            return False

        response, currentRecords = self.scripts.generateCustomers(number_input_Int, self.recordLimit)

        if response == 'Success':
            feedback_msg.set(number_input_String + ' records successively generated.')
            number_input.set('')
            limit_current_msg.set('Limit: ' + str(self.recordLimit) + '  ' + 'Current: ' + str(currentRecords))
            return True

        if response == 'Limit reached':
            feedback_msg.set("Customer Table limited to " + str(self.recordLimit) + " records.\n"
                             "Can fit " + str(currentRecords) + " more records.")
            number_input.set('')
            return False

        if response == 'Error':
            feedback_msg.set('Error while generating customer records.\n' +
                              number_input_String + ' customer records currently in the database.')
            number_input.set('')
            return False

    def plotCustomerAge(self, loading_msg):

        """
        This function plots a bar graph on the frame with the age of customers in groups and their
        respective number of customers.

        :param loading_msg: The text label with the status of the page.
        :return: Success of function
        """

        # Clear canvas before plotting anything else onto it
        for widget in self.window.winfo_children():
            if 'canvas' in widget._name:
                widget.destroy()

        # Check if there are any records in the customer table first
        data = self.db.selectNumberOfCustomerRecords()
        if data[0][0] == 0:
            loading_msg.set('No data to visualize')
            return False

        loading_msg.set('Generating...')

        # Retrieve partitioned customer ages
        data = self.db.getCustomerAgeGroups()
        if data is False:
            loading_msg.set('Problem retrieving customer data')
            return False

        ageGroups = ['18 - 25', '26 - 40', '40 - 65', '65+']
        numberOfCustomer = [0, 0, 0, 0]

        # Create different age intervals and populate them with the data
        for row in data:
            dob = row[0]
            year = dob.split('-')[0]
            age = datetime.now().year - int(year)
            if 18 <= age <= 25:
                numberOfCustomer[0] += 1
            if 26 <= age <= 40:
                numberOfCustomer[1] += 1
            if 41 <= age <= 65:
                numberOfCustomer[2] += 1
            if 66 <= age:
                numberOfCustomer[3] += 1

        try:
            # Figure
            fig = pyplot.Figure(figsize=(5, 5), dpi=100)
            ax1 = fig.add_subplot(111).bar(ageGroups, numberOfCustomer)
            fig.suptitle("Number of Customers by Age Group")
            # ax1.set_xlabel('Age')
            # ax1.set_ylabel('Number of customers')

            # Canvas
            canvas = FigureCanvasTkAgg(fig, master=self.window)  # A tk.DrawingArea.
            canvas.get_tk_widget().grid(row=5, column=1)

            loading_msg.set('Graph Generated')
        except:
            print('Problem creating graph. Check matplotlib version.')
            loading_msg.set('Problem generating graph')
            return False

        return True

    def plotCustomerRegion(self, loading_msg):

        """
        Function to plot a choropleth map.(https://en.wikipedia.org/wiki/Choropleth_map)
        Each region is shaded darker according to how many customers are from that region.
        A darker region indicates more customers, and vice versa.

        TO DO:
        Make toolbar available.

        :param loading_msg: A label from the GUI that typically represents the status.
        :return: Successfulness of function
        """

        # Clear canvas before plotting anything else onto it
        for widget in self.window.winfo_children():
            if 'canvas' in widget._name:
                widget.destroy()

        # Check if there are any records in the Customer Table first
        data = self.db.selectNumberOfCustomerRecords()
        if data[0][0] == 0:
            loading_msg.set('No data to visualize')
            return False

        # Feedback to inform user of progress
        loading_msg.set('Generating map...this may take a moment.')
        self.window.update()

        # Get .shp file data stored as pickle for faster retrieval
        # Source https://library.carleton.ca/find/gis/geospatial-data/shapefiles-canada-united-states-and-world
        try:
            with open('lib/map_data.pickle', 'rb') as handle:
                map_dataframe = pickle.load(handle)
        except:
            print('Problem retrieving data from pickle file')
            loading_msg.set('Problem generating map')
            return False

        data = self.db.getCustomerRegions()

        if data is False:
            loading_msg.set('Problem generating map')
            return False

        # Formatting region uids and their respective number of customers to place into a pandas DataFrame.
        eruids = []
        nbCustomers = []
        maxValue = 1
        for val in data:
            eruids.append(val[0])
            nbCustomers.append(val[1])
            if val[1] > maxValue:
                maxValue = val[1]

        # Join region DataFrame with customer DataFrame
        try:
            tempDataFrame = pandas.DataFrame({'ERUID': eruids, 'nbCustomers': nbCustomers})
            newDataFrame = map_dataframe.set_index('ERUID').join(tempDataFrame.set_index('ERUID'))
        except:
            print('Problem with pandas dataframe. Check version, or pickle files for corruption')
            return False

        # Figure
        fig, ax = pyplot.subplots(1, figsize=(5, 5))
        ax.axis('off')
        ax.set_title('Number of Customers per Region')

        # Map
        sm = pyplot.cm.ScalarMappable(cmap='Blues', norm=pyplot.Normalize(vmin=0, vmax=maxValue))
        sm._A = []
        cbar = fig.colorbar(sm)
        newDataFrame.plot(column='nbCustomers', cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8')

        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=self.window)  # A tk.DrawingArea.
        canvas.get_tk_widget().grid(row=5, column=1)

        # toolbar = NavigationToolbar2Tk(canvas, self.window)
        # toolbar.grid(row=5, column=1)

        loading_msg.set('Map generated')
        return True

    def getRegions(self):

        """
        Function to get all the region names to provide in the Combobox() object in GUI.
        :return: Successfulness of function
        """

        data = self.db.getRegions()

        if data is False:
            print('Problem retrieving regions')
            return
        regions = []
        for val in data:
            regions.append(val[0])
        return regions

    def getRequests(self, request_list, request_notification):

        """
        Function to populate the request listbox with the emails of those who are requesting an account.
        Also update the request_notification label with the current number of requests.
        :param request_list: The request listbox
        :param request_notification: A tk label object that will display the number of current requests in the form of a string.
        :return:
        """

        data = self.db.getRequests()

        numOfRequests = len(data)

        request_notification.set("There's " + str(numOfRequests) + " new request(s).")

        request_list.delete(0, 'end')
        for i, email in enumerate(data):

            request_list.insert(i, email)

        return True

    def enableApproveAndDeclineBtn(self, request_feedback):


        """
        Function to enable approve button if user selects one and only one item (email) in the
        requests list box

        :return:
        """

        # Clear feedback
        request_feedback.set('')

        # Get buttons
        approve_btn = self.window.nametowidget('approve_btn')
        decline_btn = self.window.nametowidget('decline_btn')

        # Get checkboxes
        login_checkbox = self.window.nametowidget('login_permission')
        edit_checkbox = self.window.nametowidget('edit_permission')
        delete_checkbox = self.window.nametowidget('delete_permission')
        delete_all_checkbox = self.window.nametowidget('delete_all_permission')
        add_checkbox = self.window.nametowidget('add_permission')
        analyze_checkbox = self.window.nametowidget('analyze_permission')

        # get requests listbox
        list_box = self.window.nametowidget('requests')

        # Check if selected 1 and only 1 item
        clicked_items = list_box.curselection()
        if len(clicked_items) > 1 or len(clicked_items) < 1:
            return False

        request_feedback.set('Choose permissions')

        # Enable buttons and checkboxes
        approve_btn['state'] = 'normal'
        decline_btn['state'] = 'normal'
        login_checkbox['state'] = 'normal'
        edit_checkbox['state'] = 'normal'
        delete_checkbox['state'] = 'normal'
        delete_all_checkbox['state'] = 'normal'
        add_checkbox['state'] = 'normal'
        analyze_checkbox['state'] = 'normal'

        return True

    def disableApproveAndDeclineBtn(self, request_feedback):

        """
        Function to disable the buttons that can approve and decline the requests of new users.
        :return:
        """

        # Clear feedback
        request_feedback.set('')

        # Get buttons
        approve_btn = self.window.nametowidget('approve_btn')
        decline_btn = self.window.nametowidget('decline_btn')

        # Get checkboxes
        login_checkbox = self.window.nametowidget('login_permission')
        edit_checkbox = self.window.nametowidget('edit_permission')
        delete_checkbox = self.window.nametowidget('delete_permission')
        delete_all_checkbox = self.window.nametowidget('delete_all_permission')
        add_checkbox = self.window.nametowidget('add_permission')
        analyze_checkbox = self.window.nametowidget('analyze_permission')

        # Enable buttons and checkboxes
        approve_btn['state'] = 'disable'
        decline_btn['state'] = 'disable'
        login_checkbox['state'] = 'disable'
        edit_checkbox['state'] = 'disable'
        delete_checkbox['state'] = 'disable'
        delete_all_checkbox['state'] = 'disable'
        add_checkbox['state'] = 'disable'
        analyze_checkbox['state'] = 'disable'

        return

    def approveUser(self, request_notification, request_feedback, login_var, edit_var, delete_var, delete_all_var, add_var, analyze_var):

        """
        Function to add user to database. It is invoked by the approve button. It add a user using the email selected
        in the reqeuests listbox. Permissions are set according to their values selected by the admin.

        :return:
        """

        # Get requests listbox
        requests_listbox = self.window.nametowidget('requests')

        # Get email selected
        clicked_items = requests_listbox.curselection()
        if len(clicked_items) > 1 or len(clicked_items) < 1:
            return False
        clicked_item_index = clicked_items[0]
        email = requests_listbox.get(clicked_item_index)[0]

        # Random password
        password = random.randint(1111111, 9999999)

        # Add email to users
        add_user_response = self.db.addUser(email, password)

        # Remove requests
        feedback = ''
        if add_user_response is True:
            dlt_respone = self.db.removeRequest(email)
            if dlt_respone is True:
                feedback += 'User approved. '
            else:
                feedback += ' Unable to remove request. Contact db admin. '

        # Set permissions
        permission_response = self.db.setPermissions(email, login_var.get(), edit_var.get(), delete_var.get(), delete_all_var.get(), add_var.get(), analyze_var.get())

        if permission_response is True:
            feedback += 'Permissions successfully set. '
        else:
            feedback += 'Failed to set permissions. '

        # Refresh requests
        self.getRequests(requests_listbox, request_notification)

            # Reset and disable checkboxes and buttons
        # Get buttons
        approve_btn = self.window.nametowidget('approve_btn')
        decline_btn = self.window.nametowidget('decline_btn')

        # Get checkboxes
        login_checkbox = self.window.nametowidget('login_permission')
        edit_checkbox = self.window.nametowidget('edit_permission')
        delete_checkbox = self.window.nametowidget('delete_permission')
        delete_all_checkbox = self.window.nametowidget('delete_all_permission')
        add_checkbox = self.window.nametowidget('add_permission')
        analyze_checkbox = self.window.nametowidget('analyze_permission')

        # Disable
        approve_btn['state'] = 'disable'
        decline_btn['state'] = 'disable'
        login_checkbox['state'] = 'disable'
        edit_checkbox['state'] = 'disable'
        delete_checkbox['state'] = 'disable'
        delete_all_checkbox['state'] = 'disable'
        add_checkbox['state'] = 'disable'
        analyze_checkbox['state'] = 'disable'

        # Reset checkboxes
        login_var.set(0)
        edit_var.set(0)
        delete_var.set(0)
        delete_all_var.set(0)
        add_var.set(0)
        analyze_var.set(0)

        # Email new user with credentials
        if self.email is True:
            email_response = self.emailNewUserCredentials(email, password)

            if email_response is True:
                feedback += 'Email successfully sent. '
            else:
                feedback += 'Failed to send email to user. '
        else:
            feedback += 'Email setting turned off, email not sent.'

        # Respond to app user
        request_feedback.set(feedback)

        return True

    def declineUser(self, request_notification, request_feedback, login_var, edit_var, delete_var, delete_all_var, add_var, analyze_var):

        """
        Function to decline an account request. The email selected by the admin within the requests listbox will
        be removed from the requests table.

        :param request_notification:
        :param request_feedback:
        :return:
        """

        requests_listbox = self.window.nametowidget('requests')

        # Get selected request email
        clicked_items = requests_listbox.curselection()
        if len(clicked_items) > 1 or len(clicked_items) < 1:
            return False
        clicked_item_index = clicked_items[0]
        email = requests_listbox.get(clicked_item_index)[0]

        # Remove request
        response = self.db.removeRequest(email)

        # Respond to user
        if response is True:
            request_feedback.set('Request successfully declined.')
        else:
            request_feedback.set('Failed to remove request. Contact db admin.')
            return False

        # Refresh requests listbox
        self.getRequests(requests_listbox, request_notification)

            # Reset and disable checkboxes and buttons
        # Get buttons
        approve_btn = self.window.nametowidget('approve_btn')
        decline_btn = self.window.nametowidget('decline_btn')

        # Get checkboxes
        login_checkbox = self.window.nametowidget('login_permission')
        edit_checkbox = self.window.nametowidget('edit_permission')
        delete_checkbox = self.window.nametowidget('delete_permission')
        delete_all_checkbox = self.window.nametowidget('delete_all_permission')
        add_checkbox = self.window.nametowidget('add_permission')
        analyze_checkbox = self.window.nametowidget('analyze_permission')

        # Disable
        approve_btn['state'] = 'disable'
        decline_btn['state'] = 'disable'
        login_checkbox['state'] = 'disable'
        edit_checkbox['state'] = 'disable'
        delete_checkbox['state'] = 'disable'
        delete_all_checkbox['state'] = 'disable'
        add_checkbox['state'] = 'disable'
        analyze_checkbox['state'] = 'disable'

        # Reset checkboxes
        login_var.set(0)
        edit_var.set(0)
        delete_var.set(0)
        delete_all_var.set(0)
        add_var.set(0)
        analyze_var.set(0)

        return True

    def submitRequest(self, email, email_rsp):

        """
        Function to submit request for an account. These requests will appear in the admin menu.

        :param email: The email of the user requesting an account
        :return:
        """

        if email == '':
            return

        # Check if email already exists within requests
        data = self.db.checkReqeustExists(email)

        # Email already exists
        if len(data) > 0:
            email_rsp.set('Request already submitted with that email.')
            return False

        # Check if email is already used for a user
        data = self.db.checkUserExists(email)

        # Email already in use
        if len(data) > 0:
            email_rsp.set('Cannot use that email.')
            return False

        # Submit request
        response = self.db.submitRequest(email)

        # Resond to user
        if response is True:
            email_rsp.set('Account request submitted.\nIf approved you will receive an email with your login credentials.')
        else:
            email_rsp.set('There was a problem submitting the request.')

        return True

    def searchUser(self, username, login_var, edit_var, delete_var, delete_all_var, add_var, analyze_var, search_fdbk):

        """
        Function to search for a particulart user in the database from the admin menu and update the checkboxes that
        represent their permissions. These permissions represent the user's access to particular functionalities/buttons
        within the application.

        :param username: The username of the user being searched for.
         :param login_var: A tk IntVar that represents the value of the login permission
        :param edit_var: A tk IntVar that represents the value of the edit_customer permission
        :param delete_var: A tk IntVar that represents the value of the delete_customer permission
        :param delete_all_var: A tk IntVar that represents the value of the delete_all_customer permission
        :param add_var: A tk IntVar that represents the value of the add_customer permission
        :param analyze_var: A tk IntVar that represents the value of the analyze_customer permission
        :param user_fdbk: The tk label object that will contain the system feedback for the user in the form of a string.
        :return:
        """

        if username == '':
            return

        response = self.db.checkUserExists(username)

        if len(response) < 1:
            search_fdbk.set('No user with that username')
            return False

        # If user exists
        permissions = self.db.getPermissions(username)

        # Set checkbox values to user current permissions
        login_var.set(permissions['login'])
        edit_var.set(permissions['edit_customer_btn'])
        delete_var.set(permissions['delete_customer_btn'])
        delete_all_var.set(permissions['delete_all_customer_btn'])
        add_var.set(permissions['add_customer_btn'])
        analyze_var.set(permissions['analyze_customer_btn'])

        # Get checkboxes
        login_checkbox = self.window.nametowidget('login_permission')
        edit_checkbox = self.window.nametowidget('edit_permission')
        delete_checkbox = self.window.nametowidget('delete_permission')
        delete_all_checkbox = self.window.nametowidget('delete_all_permission')
        add_checkbox = self.window.nametowidget('add_permission')
        analyze_checkbox = self.window.nametowidget('analyze_permission')

        # Get buttons
        change_perm_btn = self.window.nametowidget('change_permissions_btn')
        delete_user_btn = self.window.nametowidget('delete_user_btn')

        # Set checkbox states to normal
        login_checkbox['state'] = 'normal'
        edit_checkbox['state'] = 'normal'
        delete_checkbox['state'] = 'normal'
        delete_all_checkbox['state'] = 'normal'
        add_checkbox['state'] = 'normal'
        analyze_checkbox['state'] = 'normal'

        # Set button states to normal
        change_perm_btn['state'] = 'normal'
        delete_user_btn['state'] = 'normal'

        return True

    def emailNewUserCredentials(self, user_email, user_password):

        """
        Function to send an email to the new approved user containing their login credentials.

        :return:
        """

        sender_email = 'thisisarandomemail000@gmail.com'
        sender_password = 'wordofpassage'

        message = "Your Customer Management System account has been approved. Here are your credentials.\n\n"\
                  "Username: " + str(user_email) + '\n'\
                  "Password: " + str(user_password)

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
        except:
            print('Could not connect to server')
            return False
        try:
            server.starttls()
        except:
            print('Problem on server end')
            return False
        try:
            server.login(sender_email, sender_password)
        except:
            print('Failed to log in to app account')
            return False
        try:
            server.sendmail(sender_email, user_email, message)
        except:
            print('Failed to send email to new user')
            return False

        return True

    def changeUserPermissions(self, username, login_var, edit_var, delete_var, delete_all_var, add_var, analyze_var, user_fdbk):

        """
        Function to change the permissions of a user. The permissions typically represent access to buttons/functionalities
        of the application that can manipulate customers/data.

        :param username: The username of the user
        :param login_var: A tk IntVar that represents the value of the login permission
        :param edit_var: A tk IntVar that represents the value of the edit_customer permission
        :param delete_var: A tk IntVar that represents the value of the delete_customer permission
        :param delete_all_var: A tk IntVar that represents the value of the delete_all_customer permission
        :param add_var: A tk IntVar that represents the value of the add_customer permission
        :param analyze_var: A tk IntVar that represents the value of the analyze_customer permission
        :param user_fdbk: The tk label object that will contain the system feedback for the user in the form of a string.
        :return:
        """

        response = self.db.changeUserPermissions(username, login_var.get(), edit_var.get(), delete_var.get(), delete_all_var.get(), add_var.get(), analyze_var.get())

        if response is True:
            user_fdbk.set('Successfully set permissions.')
        else:
            user_fdbk.set('Failed to set permissions. Contact db admin.')

        return True

    def deleteUser(self, username, user_fdbk):

        """
        Function to delete the user from the database. This function is only accessed from the admin menu.
        :param username: The username of the user to be deleted
        :param user_fdbk: The tk label object that will contain the system feedback for the user in the form of a string.
        :return:
        """

        # The feedback string
        feedback = ''

        response = self.db.deleteUser(username)

        if response is True:
            feedback += 'User successively deleted.\n'
        else:
            feedback += 'User could not be deleted. Contact db admin.\n'

        response = self.db.deletePermissions(username)

        if response is True:
            feedback += 'Permissions successively deleted.\n'
        else:
            feedback += 'Permissions could not be deleted. Contact db admin.\n'

        # Set the feedback
        user_fdbk.set(feedback)

            # Disable buttons and checkboxes

        # Get checkboxes
        login_checkbox = self.window.nametowidget('login_permission')
        edit_checkbox = self.window.nametowidget('edit_permission')
        delete_checkbox = self.window.nametowidget('delete_permission')
        delete_all_checkbox = self.window.nametowidget('delete_all_permission')
        add_checkbox = self.window.nametowidget('add_permission')
        analyze_checkbox = self.window.nametowidget('analyze_permission')

        # Get buttons
        delete_user_btn = self.window.nametowidget('delete_user_btn')
        change_perm_btn = self.window.nametowidget('change_permissions_btn')

        # Set checkbox states to normal
        login_checkbox['state'] = 'disabled'
        edit_checkbox['state'] = 'disabled'
        delete_checkbox['state'] = 'disabled'
        delete_all_checkbox['state'] = 'disabled'
        add_checkbox['state'] = 'disabled'
        analyze_checkbox['state'] = 'disabled'

        # Set button states to normal
        delete_user_btn['state'] = 'disabled'
        change_perm_btn['state'] = 'disabled'

        return True

    def autoCompleteUser(self, autoCompleteList, user_input, user_fdbk, login_var, edit_var, delete_var, delete_all_var, add_var, analyze_var):

        """
        Function to populate a dropdown listbox that contains all usernames in teh datatbase that start
        with the user_input string. This listbox is initialized in the GUI and hidden. It will only be revealed
        when there are 1 or more greater usernames that begin with the user_input string.

        :param auto_complete_list: The listbox that will hold and display the usernames.
        :param user_input: The string that represents the username the user is looking for.
        :return:
        """

        # Clear feedback
        user_fdbk.set('')

        # Clear widget of any text and hide
        autoCompleteList.delete(0, 'end')
        autoCompleteList.place_forget()

        # Get checkboxes
        login_checkbox = self.window.nametowidget('login_permission')
        edit_checkbox = self.window.nametowidget('edit_permission')
        delete_checkbox = self.window.nametowidget('delete_permission')
        delete_all_checkbox = self.window.nametowidget('delete_all_permission')
        add_checkbox = self.window.nametowidget('add_permission')
        analyze_checkbox = self.window.nametowidget('analyze_permission')

        # Get buttons
        delete_user_btn = self.window.nametowidget('delete_user_btn')
        change_perm_btn = self.window.nametowidget('change_permissions_btn')

        # Set checkbox states to normal
        login_checkbox['state'] = 'disabled'
        edit_checkbox['state'] = 'disabled'
        delete_checkbox['state'] = 'disabled'
        delete_all_checkbox['state'] = 'disabled'
        add_checkbox['state'] = 'disabled'
        analyze_checkbox['state'] = 'disabled'

        # Reset checkbox values
        login_var.set(0)
        edit_var.set(0)
        delete_var.set(0)
        delete_all_var.set(0)
        add_var.set(0)
        analyze_var.set(0)

        # Set button states to normal
        delete_user_btn['state'] = 'disabled'
        change_perm_btn['state'] = 'disabled'

        if user_input is '':
            return False

        data = self.db.usernameContaining(user_input)

        if len(data) < 1:
            return False

        for i, username in enumerate(data):
            autoCompleteList.insert(i, username)

        autoCompleteList.place(x=500, y=416)

        return True

    def selectFromAutoCompleteUser(self, autoCompleteList, user_input_field):

        """
        This function will take the selected item from the autocomplete listbox and set the entry value equal
        to the selected item. The listbox will then be cleared and hidden.

        :return:
        """

        clicked_items = autoCompleteList.curselection()
        if len(clicked_items) > 1 or len(clicked_items) < 1:
            return False
        clicked_item_index = clicked_items[0]

        selected_email = autoCompleteList.get(clicked_item_index)[0]

        user_input_field.set(selected_email)

        autoCompleteList.place_forget()

        return True