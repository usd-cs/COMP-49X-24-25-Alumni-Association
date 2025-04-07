import os


def load_country_dict():
    """
    Load country codes and names from a the text file country_codes_list.txt in this same directory

    Returns:
        dict: A dictionary where keys are country codes (str) and values are country names (str)
    """
    country_dict = {}
    file_path = os.path.join(os.path.dirname(__file__), "country_codes_list.txt")
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            code, name = line.strip().split("&")
            country_dict[code] = name
    return country_dict


def get_country_name(country_dict, code):
    """
    Retrieve the country name from the dictionary using a given code

    Args:
        country_dict (dict): The dictionary returned by load_country_dict
        code (str): The country code to look up

    Returns:
        str: The name of the country if found, otherwise "Country code not found".
    """
    return country_dict.get(code, "Country code not found")
