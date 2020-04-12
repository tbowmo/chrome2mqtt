'''
Simple alias handling, for rooms
'''

class AliasException(Exception):
    """
    Exception class for alias errors
    """

class Alias:
    #pylint: disable=too-few-public-methods
    '''
    Handles aliases for room / devices in the mqtt tree.
    aliases is setup with an comma delimited string with alias pairs:
    device1=alias/path1,device2=alias/path2,....
    '''
    __aliases = {}
    def __init__(self, alias_string=None):
        print('alias init')
        try:
            if alias_string is not None:
                alias_pairs = alias_string.split(',')
                for alias_pair in alias_pairs:
                    alias = alias_pair.split('=')
                    self.__aliases.update({alias[0]: alias[1]})
        except IndexError:
            raise AliasException('You have an error in your alias definition')
        print(self.__aliases)

    def get(self, device_name):
        '''
        return an aliased deviceName, if an alias is found,
        otherwise it returns the deviceName as is.
        '''
        if device_name not in self.__aliases:
            return device_name
        return self.__aliases[device_name]
