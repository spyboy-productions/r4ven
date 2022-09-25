"""
Author: R3tr0
Date: 25/09/2022
Purpose: will hold the util functions of the program
"""


def get_file_data(file_path):
    """
    gets the file data
    :param file_path: the path to the file you want to read
    :return: the file data as plain text
    """
    with open(file_path, 'r') as open_file:
        return open_file.read()
