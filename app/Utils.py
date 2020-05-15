import datetime

class Utils:

    """
    Class that contains helper functions to backend.
    """

    def __init__(self):

        return

    def padStrings(self, listOfStrings):

        """
        Function to pad strings evenly according to the string with the max length.

        :param listOfStrings: A list of string objects
        :return: The list of strings now padded
        """

        max_len = max(len(el) for el in listOfStrings)

        paddedList = []
        for string in listOfStrings:
            diff = max_len - len(string)
            padding = ' ' * diff
            paddedList.append(string + padding)
        return paddedList

    def checkForEmptyStrings(self, listOfStrings):

        """
        Function to check if there is an empty string in the list of strings.
        This is used to check for empty input fields where they should not be.
        :param listOfStrings: The list of string objects
        :return: True if list contains an empty string, false otherwise
        """
        for string in listOfStrings:
            if len(string) == 0:
                return True
        return False

    def convertToStrings(self, listOfValues):

        """
        Convert a list of objects, typically values from a database, to strings.
        This function is necessary because it is ideal for widgets to typically
        take in string values only and the database columns have many data types.

        :param listOfValues: The list of data values objects
        :return:
        """

        stringValues = []
        for value in listOfValues:
            stringValues.append(str(value))

        return stringValues

    def isValidDate(self, date):

        """
        Check if passed in date is valid.
        Expecting format yyyy-mm-dd.

        :param date: Date (yyyy-mm-dd)
        :return: True if valid, False otherwise
        """

        dateIsValid = False
        try:
            if datetime.datetime.strptime(date, '%Y-%m-%d'):
                dateIsValid = True
        except ValueError:
            print('Date entered is not a valid date.')

        return dateIsValid