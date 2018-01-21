
from collections import defaultdict

from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class CompareDictionary(object):
    """
    This class compares between two dictionaried with openstack objects
    Run on each list of dictionaries and compare
    Create a list of "difference" between the dictionaries
    """

    IGNORE_CLIENTS = []

    def __init__(self, dict1, dict2):
        self.dict1 = dict1
        self.dict2 = dict2
        self.difference = defaultdict(list)

    def compare_dictionaries(self):
        for key in self.dict1.keys():
            d1_list, d2_list = self._get_info_from_key(key)
            self._difference_bettwen_lists(d1_list, d2_list, key)
        return self.difference

    def _get_info_from_key(self, key_name):
        # get the info from keys
        dict1 = self.dict1.get(key_name)
        dict2 = self.dict2.get(key_name)
        if dict1 and dict2:
            if len(dict1) - len(dict2) != 0:
                LOG.info("dictionary len is not equal in %s data is missing"
                         % key_name)
            return dict1, dict2
        raise RuntimeError("Key %s does not exist on both dictionaries"
                           % key_name)

    def _list_of_difference(self, l1, l2, key):
        for d1 in l1:
            if not self._search_dictionary_in_list(d1, l2):
                if key not in self.IGNORE_CLIENTS:
                    self._add_to_difference_list(d1, key)
        for d2 in l2:
            if not self._search_dictionary_in_list(d2, l1):
                if key not in self.IGNORE_CLIENTS:
                    self._add_to_difference_list(d2, key)

    def _difference_bettwen_lists(self, list_of_dict1, list_of_dict2, key):
        self._list_of_difference(list_of_dict1, list_of_dict2, key)

    def _search_dictionary_in_list(self, d1, list_dictionary):
        for d2 in list_dictionary:
            if d1 == d2:
                return True
        return False

    def _add_to_difference_list(self, dictionary, key):
        if dictionary not in [item for item in self.difference.items()]:
            self.difference[key].append(dictionary)
