import random
import pickle

"""
This is a class that contains all the scripts used by the application.
"""

class Scripts:

    def __init__(self, db):

        self.db = db
        return

    def generateCustomers(self, numberOfCustomers, limit):

        """
        Script that will generate 'numberOfCustomers' customer records with random data and insert them into the database.
        The limit is the 'limit' passed in argument as defined in the backend.

        If the database contains 'limit' number of records, the script will not execute. Likewise, if it is called,
        and the numberOfCustomers would makes the database exceed the limit, it will not execute.

        :param numberOfCustomers: The number of random customers to generate
        :return: tuple: response as string, number of current records in table
        """

        response = 'Success'

        data = self.db.selectNumberOfCustomerRecords()
        currrentNumberOfCustomers = data[0][0]

        # Check if the limit has been reached
        if currrentNumberOfCustomers + numberOfCustomers > limit:
            response = 'Limit reached'
            numOfRecordsThatFit = limit - currrentNumberOfCustomers
            return response, numOfRecordsThatFit

        # Names - Source: https://www.ssa.gov/oact/babynames/limits.html
        with open('lib/names.pickle', 'rb') as handle:
            names = pickle.load(handle)

        # Get canadian region uids, this is the region the customer is from.
        # Source https://library.carleton.ca/find/gis/geospatial-data/shapefiles-canada-united-states-and-world
        with open('lib/canadian_region_uids.pickle', 'rb') as handle:
            economic_region_uids = pickle.load(handle)

        # Loop to generate records
        for n in range(0, numberOfCustomers):

            print('Progress: ', n, end='\r')

            # Get unique email
            emailIsUnique = False
            while not emailIsUnique:

                # First name
                firstname = random.choice(names)
                names.remove(firstname)

                # Last name
                lastname = random.choice(names)
                names.remove(lastname)

                # email
                email = firstname + '.' + lastname + '@hotmail.com'
                result = self.db.getCustomerInfo(email)

                if len(result) < 1:
                    emailIsUnique = True

            # password
            characters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                          'S', 'T', 'U','V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
                          'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u','v', 'w', 'x', 'y', 'z', '1', '2', '3', '4',
                          '5', '6', '7', '8', '9', '0', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '<',
                          '>', '?', '/']
            password = ""
            for i in range(0, 10):
                password += random.choice(characters)

            # country
            country = 'Canada'

            city = random.choice(economic_region_uids)

            # Address
            streets = """Main,Maple,Park,Church,Pine,Birch,Railway,Cedar,River,Spruce,1 Avenue,2 Avenue,3 Avenue,4 Avenue"""
            streets = streets.split(',')
            street = random.choice(streets)

            number = str(random.randint(0, 9999))

            address = number + " " + street

            # Postal Code
            letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                       'S', 'T', 'U','V', 'W', 'X', 'Y', 'Z']
            numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

            isLetter = True
            isNumber = False
            postalcode = ""
            for i in range(0, 6):
                if isLetter:
                    postalcode += random.choice(letters)
                    isLetter = False
                    isNumber = True
                elif isNumber:
                    postalcode += random.choice(numbers)
                    isLetter = True
                    isNumber = False

            # Balance
            balance = random.randint(0, 14)

            # Rating
            ratings = [True, False]
            rating = random.choice(ratings)

            # Preferred Card
            visaPrefixes = ['4539', '4556', '4916', '4532', '4929']
            preferredCard = random.choice(visaPrefixes) + str(random.randint(12345679123, 999999999999))

            # Status
            statuses = ['active', 'inactive']
            status = random.choice(statuses)

            # Cycle Date
            cycledate = random.randint(1, 28)

            # Typename
            types = ['regular', 'student']
            type = random.choice(types)

            # B-day
            year = str(random.randint(1930, 2002))
            month = str(random.randint(1, 12))

            if month in ['1', '3', '5', '7', '8', '10', '12']:
                day = str(random.randint(1, 31))
            if month in ['4', '6', '9', '11']:
                day = str(random.randint(1, 30))
            if month in ['2']:
                day = str(random.randint(1, 28))

            bday = year + '-' + month + '-' + day

            # If error during insert, break
            if not self.db.insertFullCustomer(email, password, firstname, lastname, country, city, address, postalcode, balance, preferredCard, rating,
            status, cycledate, type, bday):
                response = 'Error'
                break

        # Get current number of records in Customer table
        data = self.db.selectNumberOfCustomerRecords()
        currrentNumberOfCustomers = int(data[0][0])

        return response, currrentNumberOfCustomers


