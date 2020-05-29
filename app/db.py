import traceback
import sqlite3
import pickle


class Database:

    """
    Class that directly connects and interacts with the database.

    TODO:
    Create class for each relation?
    FINISH DOCUMENTATION
    """

    def __init__(self, dbname):

        # Name of the database to connect to
        self.dbname = dbname

        # Declare connections. Set to None while not in use. This is to avoid locking the database.
        self.conn = None
        self.cursor = None

        # Initialize the tables if they do not exist. Populate necessary tables
        self.initializeTables()

    def connect(self):

        """
        Function to connect to the database and set the connection and cursor.
        :return:
        """
        try:
            self.conn = sqlite3.connect(self.dbname)
            self.cursor = self.conn.cursor()
        except Exception:
            print("There was an error connecting to the database.")
            traceback.print_stack()
            return False
        return True

    def disconnect(self):
        """
        Function to gracefully disconnect from the database
        :return:
        """
        try:
            self.cursor.close()
            self.conn.close()
        except:
            print('Error disconnecting to database')
            traceback.print_stack()
            return False
        return True

    def initializeTables(self):

        """
        This function initializes the database with the tables required for the application.
        They are not all required at the moment, but a full fledged app would likely use tables like the ones created.
        """

        self.connect()
        sqlQuery = """
                    CREATE TABLE IF NOT EXISTS customer(
                    email varchar NOT NULL,
                    pword varchar NOT NULL,
                    fname varchar,
                    lname varchar,
                    country varchar,
                    region varchar,
                    address varchar,
                    postalcode varchar,
                    balance int DEFAULT 0,
                    preferredcard char(16),
                    rating BOOLEAN DEFAULT 'False',
                    status varchar DEFAULT 'inactive',
                    cycledate int,
                    typename varchar,
                    bday date,
                    FOREIGN KEY (typename) REFERENCES subscriptionType(typename),
                    PRIMARY KEY (email)
                    );
                    """
        try:
            self.cursor.execute(sqlQuery)
            self.conn.commit()
        except:
            print('Error initializing Customer table')
            traceback.print_stack()
            return False
        finally:
            self.disconnect()


        self.connect()
        sqlQuery = """
                    CREATE TABLE IF NOT EXISTS economic_region(
                    eruid char(4),
                    ername varchar,
                    PRIMARY KEY(eruid)
                    );
                    """
        try:
            self.cursor.execute(sqlQuery)
            self.conn.commit()
        except:
            print('Error initializing economic_region table')
            traceback.print_stack()
            return False
        finally:
            self.disconnect()

        # User Table
        self.connect()
        sqlQuery = """
                   CREATE TABLE IF NOT EXISTS User (
                    username VARCHAR PRIMARY KEY,
                    password VARCHAR NOT NULL,
                    status   BOOLEAN DEFAULT (1) 
                    );
                    """
        try:
            self.cursor.execute(sqlQuery)
            self.conn.commit()
        except:
            print('Error initializing User table')
            traceback.print_stack()
            return False
        finally:
            self.disconnect()

        # Insert the Admin user
        self.connect()
        sqlQuery = """
                    INSERT INTO User 
                    SELECT 'admin', 'password', '0'
                    WHERE NOT EXISTS (SELECT username FROM User
                                      WHERE username = 'admin'
                                      );
                    """
        try:
            self.cursor.execute(sqlQuery)
            self.conn.commit()
        except:
            print('Error adding admin to user table')
            traceback.print_stack()
            return False
        finally:
            self.disconnect()

        # Permission Table
        # NOTE: If ever add permissions columns, it is advised to add them to the getPermissions() method, and
        #       the dictionary within that method that it returns
        self.connect()
        sqlQuery = """
                    CREATE TABLE IF NOT EXISTS Permission (
                        user                    VARCHAR REFERENCES User (username) PRIMARY KEY,
                        login                   BOOLEAN DEFAULT (0),
                        edit_customer_btn       BOOLEAN DEFAULT (0),
                        delete_customer_btn     BOOLEAN DEFAULT (0),
                        delete_all_customer_btn BOOLEAN DEFAULT (0),
                        add_customer_btn        BOOLEAN DEFAULT (0),
                        analyze_customer_btn    BOOLEAN DEFAULT (0) 
                    );

                    """
        try:
            self.cursor.execute(sqlQuery)
            self.conn.commit()
        except:
            print('Error initializing Permission table')
            traceback.print_stack()
            return False
        finally:
            self.disconnect()

        # Grant Admin all permissions
        self.connect()
        sqlQuery = """
                    INSERT INTO Permission (user, login, edit_customer_btn, delete_customer_btn, delete_all_customer_btn,
                                            add_customer_btn, analyze_customer_btn)
                    SELECT 'admin', '1', '1', '1', '1', '1', '1'
                    WHERE NOT EXISTS (SELECT user FROM Permission WHERE user = 'admin');
                    """
        try:
            self.cursor.execute(sqlQuery)
            self.conn.commit()
        except:
            print('Error initializing admin permissions')
            traceback.print_stack()
            return False
        finally:
            self.disconnect()


        self.connect()
        sqlQuery = """
                    CREATE TABLE IF NOT EXISTS request (
                    email VARCHAR PRIMARY KEY
                    ); 
                   """
        try:
            self.cursor.execute(sqlQuery)
            self.conn.commit()
        except:
            print('Error initializing request table')
            traceback.print_stack()
            return False
        finally:
            self.disconnect()

        self.populateEconomicRegions()

        return True

    def validateUserLoginCredentials(self, user, passw):

        """
        Function to validate username and password match in the database

        :param user:
        :param passw:
        :return:
        """

        self.connect()
        sqlQuery = """
                     SELECT username FROM User
                     WHERE username = ? AND password = ?;
                     """
        sqlTuple = (user, passw)
        try:
            self.cursor.execute(sqlQuery, sqlTuple)
            data = self.cursor.fetchall()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return data

    def getPermissions(self, user):

        """
        Function to retrieve the permissions of a given user on the accessibility of certain buttons/functions
        of the application. It will return a dictionary of the given functionality and its permission as a boolean.
        1 for permitted, 0 for not permitted.

        :param user: The unique username of the user
        :return: Permissions: A dictionary of functionalities as string keys and permissions boolean values
        """

        self.connect()
        sqlQuery = """
                 SELECT login, edit_customer_btn, delete_customer_btn, delete_all_customer_btn, add_customer_btn,
                        analyze_customer_btn FROM Permission
                 WHERE user = ?;
                 """
        sqlTuple = (user,)
        try:
            self.cursor.execute(sqlQuery, sqlTuple)
            data = self.cursor.fetchall()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()

        permissions = {'login': data[0][0],
                       'edit_customer_btn': data[0][1],
                       'delete_customer_btn': data[0][2],
                       'delete_all_customer_btn': data[0][3],
                       'add_customer_btn': data[0][4],
                       'analyze_customer_btn': data[0][5]
                       }

        return permissions

    def populateEconomicRegions(self):

        """
        Function to populate and display the choropleth graph of the regions of canada. The shade represents the
        number of customers from that particular region.
        :return:
        """

        with open('lib/canadian_region_uids.pickle', 'rb') as handle:
            eruids = pickle.load(handle)

        with open('lib/canadian_region_names.pickle', 'rb') as handle:
            ernames = pickle.load(handle)

        for uid, ername in zip(eruids, ernames):

            self.connect()
            sqlQuery = """
                        INSERT INTO economic_region(eruid,ername) 
                        SELECT ?, ?
                        WHERE NOT EXISTS(SELECT eruid FROM economic_region WHERE eruid = ?);
                        """
            sqlTuple = (uid, ername, uid)
            try:
                self.cursor.execute(sqlQuery, sqlTuple)
                self.conn.commit()
            except:
                print('There was a problem populating economic region table')
                traceback.print_stack()
                return False
            finally:
                self.disconnect()

        return True

    def getCustomerInfo(self, email):

        """
        Retrieves record data from Customer relation with the passed in email.

        :param email: Primary key
        :return: The record data of customer, otherwise False
        """

        self.connect()
        sqlQuery = """
                    SELECT * FROM Customer
                    WHERE email = ?;
                    """
        sqlTuple = (email,)
        try:
            self.cursor.execute(sqlQuery, sqlTuple)
            data = self.cursor.fetchall()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return data

    def insertCustomer(self, email, pword, fname, lname, country, region, address, dob):

        """
        Insert's new Customer into Customer Relation using the passed in arguments.

        :param email: The primary key
        :param pword: Password
        :param fname: First name
        :param lname: Last name
        :param country: Country
        :param region: region
        :param address: Address
        :return: Successfulness of function
        """

        self.connect()
        sqlQuery = """
                    INSERT INTO Customer (email, pword, fname, lname, country, city, address, bday)
                    VALUES  (?, ?, ?, ?, ?, ?, ?, ?);
                    """
        sqlTuple = (email, pword, fname, lname, country, region, address, dob)

        try:
            self.cursor.execute(sqlQuery, sqlTuple)
            self.conn.commit()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()

        return True

    def insertFullCustomer(self, email, password, firstname, lastname, country, region, address, postalcode, balance, preferredCard, rating,
        status, cycledate, type, bday):

        """
        Function to insert a customer into the database with all the data initialized/available.

        :param email:
        :param password:
        :param firstname:
        :param lastname:
        :param country:
        :param region:
        :param address:
        :param postalcode:
        :param balance:
        :param preferredCard:
        :param rating:
        :param status:
        :param cycledate:
        :param type:
        :param bday:
        :return:
        """

        self.connect()
        sqlQuery = """
                    INSERT INTO customer
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); 
                    """

        recordTuple = (email, password, firstname, lastname, country, region, address, postalcode, balance, preferredCard, rating,
        status, cycledate, type, bday)

        try:
            self.cursor.execute(sqlQuery, recordTuple)
            self.conn.commit()
        except:
            print('Error inserting customer record to customer table.')
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return True

    def deleteCustomer(self, email):

        """
        Delete's customer from database by using the primary key, which is the email passed into the function.
        :param email: The primary key of the customer data
        :return: Successfulness of function
        """

        self.connect()
        sqlQuery = """
                    DELETE FROM Customer
                    WHERE email = ?;
                    """
        sqlTuple = (email,)

        try:
            self.cursor.execute(sqlQuery, sqlTuple)
            self.conn.commit()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return True

    def emailsBeginningWith(self, user_input):

        """
        Function to get all the customers with emails that begin with the user_input parameter.
        :param user_input: The user_input in the form of a string.
        :return:
        """

        user_input = user_input + '%'

        self.connect()
        sqlQuery = """
                   SELECT email FROM Customer
                   WHERE email LIKE ?
                   LIMIT 10;
                   """
        sqlTuple = (user_input,)
        try:
            self.cursor.execute(sqlQuery, sqlTuple)
            data = self.cursor.fetchall()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()

        return data

    # In progress
    def updateCustomer(self, attribute, user_input, email):

        """
        Function to update a customer record matching the email parameter by setting the attribute parameter to the
        user_input parameter.
        :param attribute String:  The attribute to be edited/updated.
        :param user_input String: The new value the attribute will be equal to.
        :param email String: The email of the customer to be edited.
        :return:
        """

        self.connect()
        sqlQuery = ("""
                    UPDATE Customer
                    SET (%s) = ?
                    WHERE email = ?;
                    """ %attribute)
        sqlTuple = (user_input, email)

        try:
            self.cursor.execute(sqlQuery, sqlTuple)
            self.conn.commit()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()

        return True

    def selectNumberOfCustomerRecords(self):

        """
        Function to find the number of records in the customer relation.
        :return:
        """

        self.connect()
        sqlQuery = """
                    SELECT COUNT(email) FROM customer; 
                    """

        try:
            self.cursor.execute(sqlQuery)
            data = self.cursor.fetchall()
        except:
            print("Error counting Customer records")
            traceback.print_stack()
        finally:
            self.disconnect()
        return data

    def deleteAllCustomers(self):

        """
        Delete's all records from Customer relation.
        :return: Successfulness of function
        """

        self.connect()
        sqlQuery = """
                    DELETE FROM Customer;
                    """
        try:
            self.cursor.execute(sqlQuery)
            self.conn.commit()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return True

    def getCustomerAgeGroups(self):

        """
        Function to get all customer date of births.
        This function is used to plot the age data visualization of customers.

        :return:
        """

        self.connect()
        sqlQuery = """
                   SELECT bday FROM customer;
                   """
        try:
            self.cursor.execute(sqlQuery)
            data = self.cursor.fetchall()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return data

    def getCustomerRegions(self):

        """
       Function to get the count of customers for each region, grouped by each region.
       Ex: (Laval, 7)

       :return data: The list of regions, and their customer counts, otherwise False.
       """

        self.connect()
        sqlQuery = """
                  SELECT eruid, (SELECT COUNT(*) FROM customer WHERE region = eruid)
                  FROM economic_region;
                  """
        try:
            self.cursor.execute(sqlQuery)
            data = self.cursor.fetchall()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return data

    def getRegions(self):

        """
        Function to retrieve the names of the economic regions.
        :return:
        """

        self.connect()
        sqlQuery = """
                 SELECT ername
                 FROM economic_region;
                 """
        try:
            self.cursor.execute(sqlQuery)
            data = self.cursor.fetchall()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return data

    def getEruidFromErname(self, region):

        """
        Function to get the corresponding economic region name from it's uid in economic_region table.
        :return: data, otherwise False
        """

        self.connect()
        sqlQuery = """
                 SELECT eruid FROM economic_region
                 WHERE ername = ?;
                 """
        sqlTuple = (region, )
        try:
            self.cursor.execute(sqlQuery, sqlTuple)
            data = self.cursor.fetchall()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return data

    def getErnameFromEruid(self, eruid):

        """
        Function to get the economic_region.eruid using the ername.
        :param eruid:
        :return:
        """

        self.connect()
        sqlQuery = """
                     SELECT ername FROM economic_region
                     WHERE eruid = ?;
                     """
        sqlTuple = (eruid,)
        try:
            self.cursor.execute(sqlQuery, sqlTuple)
            data = self.cursor.fetchall()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return data

    def getRequests(self):

        """
        Function to get all emails in the request relation.
        :return:
        """

        self.connect()
        sqlQuery = """
                 SELECT email FROM request;
                 """
        try:
            self.cursor.execute(sqlQuery)
            data = self.cursor.fetchall()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return data

    def addUser(self, email, password):

        """
        Function to add a user into the User relation.
        :param email String: The email of the new user.
        :param password String: The password of the new user.
        :return:
        """

        # Set their status to default value of 1
        defaultStatus = 1

        self.connect()
        sqlQuery = """
                     INSERT INTO User (username,password,status)
                     SELECT ?, ?, ?;
                   """
        try:
            sqlTuple = (email, password, defaultStatus)
            self.cursor.execute(sqlQuery, sqlTuple)
            self.conn.commit()
        except:
            traceback.print_stack()
        finally:
            self.disconnect()
        return True

    def setPermissions(self, email, login_var, edit_var, delete_var, delete_all_var, add_var, analyze_var):

        """
        Function to set the permissions of a user. The permissions represent the functionalities/buttons the user
        has access to within the application.

        :param email: The email of the user
        :param login_var: A tk IntVar value that represents the value of the login permission
        :param edit_var: A tk IntVar value that represents the value of the edit_customer permission
        :param delete_var: A tk IntVar value that represents the value of the delete_customer permission
        :param delete_all_var: A tk IntVar value that represents the value of the delete_all_customer permission
        :param add_var: A tk IntVar that value represents the value of the add_customer permission
        :param analyze_var: A tk IntVar value that represents the value of the analyze_customer permission
        :return:
        """
        self.connect()
        try:
            sqlQuery = """
                            INSERT INTO permission (user, login, edit_customer_btn, delete_customer_btn, delete_all_customer_btn, add_customer_btn, analyze_customer_btn)
                            SELECT ?, ?, ?, ?, ?, ?, ?;
                            """
            sqlTuple = (email, login_var, edit_var, delete_var, delete_all_var, add_var, analyze_var)
            self.cursor.execute(sqlQuery, sqlTuple)
            self.conn.commit()
        except:
            return False
        finally:
            self.disconnect()

        return True

    def changeUserPermissions(self, email, login_var, edit_var, delete_var, delete_all_var, add_var, analyze_var):

        """
        Function to change the permissions of a user.

        :param email: The email of the user
        :param login_var: A tk IntVar value that represents the value of the login permission
        :param edit_var: A tk IntVar value that represents the value of the edit_customer permission
        :param delete_var: A tk IntVar value that represents the value of the delete_customer permission
        :param delete_all_var: A tk IntVar value that represents the value of the delete_all_customer permission
        :param add_var: A tk IntVar that value represents the value of the add_customer permission
        :param analyze_var: A tk IntVar value that represents the value of the analyze_customer permission
        :return:
        """

        self.connect()
        try:
            sqlQuery = """
                       UPDATE permission
                       SET login = ?,
                           edit_customer_btn = ?,
                           delete_customer_btn = ?,
                           delete_all_customer_btn = ?,
                           add_customer_btn = ?,
                           analyze_customer_btn = ?
                       WHERE user = ?;
                       """
            sqlTuple = (login_var, edit_var, delete_var, delete_all_var, add_var, analyze_var, email)
            self.cursor.execute(sqlQuery, sqlTuple)
            self.conn.commit()
        except:
            return False
        finally:
            self.disconnect()

        return True

    def submitRequest(self, email):

        """
        Function to add request into the request relation.
        :param email: The email of the user requesting an account
        :return:
        """

        self.connect()
        sqlQuery = """
                     INSERT INTO request (email)
                     SELECT ?;
                   """

        sqlTuple = (email,)
        try:
            self.cursor.execute(sqlQuery, sqlTuple)
            self.conn.commit()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return True

    def checkReqeustExists(self, email):

        """
        Function to check if there exists a request in the request relation equal to the email parameter.
        :param email: The email to be checked for.
        :return:
        """

        self.connect()
        sqlQuery = """
                     SELECT email FROM request
                     WHERE email = ?;
                   """

        sqlTuple = (email,)
        try:
            self.cursor.execute(sqlQuery, sqlTuple)
            data = self.cursor.fetchall()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return data

    def removeRequest(self, email):

        """
        Function to remove a request from the request relation equal to the email parameter.
        :param email: The email to be removed
        :return:
        """

        self.connect()
        sqlQuery = """
                    DELETE FROM request
                    WHERE email = ?;
                   """

        sqlTuple = (email,)
        try:
            self.cursor.execute(sqlQuery, sqlTuple)
            self.conn.commit()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return True

    def checkUserExists(self, email):

        """
        Function to check if there exists a user in the User relation with a username that equals to the email param.
        :param email: The email to be checked for.
        :return:
        """

        self.connect()
        sqlQuery = """
                    SELECT username FROM User
                    WHERE username = ?;
                  """

        sqlTuple = (email,)
        try:
            self.cursor.execute(sqlQuery, sqlTuple)
            data = self.cursor.fetchall()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()
        return data

    def deleteUser(self, username):

        """
        Function to delete a user from the User relation equal to the username param.
        :param username: The username of the user to be deleted. Typically an email.
        :return:
        """

        self.connect()
        sqlQuery = """
                    DELETE FROM User
                    WHERE username = ?;
                   """
        try:
            sqlTuple = (username,)
            self.cursor.execute(sqlQuery, sqlTuple)
            self.conn.commit()
        except:
            traceback.print_stack()
        finally:
            self.disconnect()
        return True

    def usernameContaining(self, user_input):

        """
        Function to check if there exists a username beginning with the user_input param string.
        :param user_input: The input passed from the user.
        :return:
        """

        user_input = user_input + '%'

        self.connect()
        sqlQuery = """
                           SELECT username FROM User
                           WHERE username LIKE ?
                           LIMIT 10;
                           """
        sqlTuple = (user_input,)
        try:
            self.cursor.execute(sqlQuery, sqlTuple)
            data = self.cursor.fetchall()
        except:
            traceback.print_stack()
            return False
        finally:
            self.disconnect()

        return data

        return

    def deletePermissions(self, username):

        """
        Function to delete the permissions record of the user who's username is equal to the username param.
        :param username: The username of the user who's permissions record will be deleted from the permissions table.
        :return:
        """

        self.connect()
        sqlQuery = """
                   DELETE FROM Permission
                   WHERE user = ?;
                   """
        try:
            sqlTuple = (username,)
            self.cursor.execute(sqlQuery, sqlTuple)
            self.conn.commit()
        except:
            return False
        finally:
            self.disconnect()
        return True