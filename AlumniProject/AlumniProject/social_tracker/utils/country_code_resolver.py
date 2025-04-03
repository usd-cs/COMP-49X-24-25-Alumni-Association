import os

def load_country_dict():
    """
    Loads the country codes and names from a text file.
    Returns a dictionary where keys are codes and values are country names.
    """
    country_dict = {}
    file_path = os.path.join(os.path.dirname(__file__), "country_codes_list.txt")
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            code, name = line.strip().split('&')
            country_dict[code] = name
    return country_dict



def get_country_name(country_dict, code):
    """
    Retrieves the country name from the dictionary using the code.
    """
    return country_dict.get(code, 'Country code not found')