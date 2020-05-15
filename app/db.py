import traceback
import sqlite3
import pickle


class Database:

    """
    Class that directly connects and interacts with the database.

    TODO:
    Create subclass for each relation?
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

        return True

    def login(self, user, passw):

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

    def populateEconomicRegions(self):

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

    def emailsContaining(self, user_input):

        """

        :param user_input:
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
                  SELECT eruid, (SELECT COUNT(*) FROM customer WHERE city = eruid)
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