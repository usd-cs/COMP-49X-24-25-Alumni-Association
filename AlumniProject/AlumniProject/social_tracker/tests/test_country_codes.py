from django.test import TestCase
from social_tracker.utils.country_code_resolver import load_country_dict, get_country_name


class CountryCodeTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.country_dict = load_country_dict()

    def test_valid_country_code(self):
        self.assertEqual(get_country_name(self.country_dict, 'US'), 'United States 🇺🇸')
        self.assertEqual(get_country_name(self.country_dict, 'CA'), 'Canada 🇨🇦')

    def test_invalid_country_code(self):
        self.assertEqual(get_country_name(self.country_dict, 'ZZ'), 'Country code not found')

    def test_partial_country_code(self):
        self.assertEqual(get_country_name(self.country_dict, 'U'), 'Country code not found')