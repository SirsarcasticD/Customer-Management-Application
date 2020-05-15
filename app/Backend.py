# Local dependencies
from db import Database
from Utils import *
import Scripts
#



# External dependencies
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pickle
#

# External dependencies for regional map visualization
import pandas
import matplotlib
matplotlib.use('tkAgg')
from matplotlib import pyplot
#

class Backend:

    """
    Class that contains all the logistics of manipulating widgets and data.
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
        self.user = None

    def login(self, user_username, user_password, response_msg):

        """
        Function to validate user credentials and allow access if they exist and match in the user
        Table in the database.

        :param user_username: Entered username as string
        :param user_password: Entered password as string
        :param response_msg: The label instance to provide feedback to user
        :return: Successfulness of function
        """

        response = self.db.login(user_username, user_password)

        if len(response) == 0:
            response_msg.set('That username and password did not match.')
            return False

        self.user = response[0][0]
        self.app.customerMenu()
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
            if customerTableAttributes[i] is 'Region:':
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

        :param user_input:
        :return:
        """

        # Clear widget of any text and hide
        autoCompleteList.delete(0, 'end')
        autoCompleteList.place_forget()

        if user_input is '':
            return

        data = self.db.emailsContaining(user_input)

        if len(data) < 1:
            return

        for i, email in enumerate(data):
            autoCompleteList.insert(i, email)

        autoCompleteList.place(x=188, y=68)

        return

    def selectFromAutoComplete(self, autoCompleteList, user_input_field):

        """

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

    def updateCustomer(self, attribute, user_input, email, editWindow, cust_list, delete_btn):

        """
        Function to update customer data that user has input through edit window

        :param attribute:
        :param user_input:
        :param email:
        :param editWindow:
        :param cust_list:
        :param delete_btn:
        :return:
        """

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

        attribute = attributes[attribute]

        data = self.db.updateCustomer(attribute, user_input, email)

        if data is True:
            self.getCustomerInfo(email, cust_list, delete_btn)
            self.app.confirmEditWindow(editWindow)

        return True

    def enableEditBtn(self):

        """
        Function to enable edit button if user selects one and only one item in the list box

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
        if ':' in selected_info:
            edit_btn['state'] = 'normal'

        return True

    def disableEditBtn(self):

        """
        Function to disable edit button in customer menu
        :return:
        """

        edit_btn = self.window.nametowidget('edit_btn')
        edit_btn['state'] = 'disabled'

    def generateRandomCustomers(self, number_input, feedback_msg, limit_current_msg):

        """
        Generates random customer records equal to the number_input argument.
        This uses the generateCustomers() script.

        :param number_input: The number of records to generate
        :param feedback_msg: The StringVar() object from the gui
        :return: Successfulness of function
        """

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

        loading_msg.set('Generating map...')

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