import logging

from bastion_browser.kernel.Singleton import SingletonMeta

class KeyStore(metaclass=SingletonMeta):
    """This class implements a structure for storing in memory the ssh keys alongside with their passwords
    """

    def __init__(self):
        """Constructor.
        """

        self._keys = {}

    def addKey(self, keyfile, key):
        """Add a key to the store.

        Args:
            keyfile (str): the path to the key
            key (paramiko key): the key
        """

        if keyfile in self._keys:
            logging.warning('The key store already contains {} key'.format(keyfile))
            return

        self._keys[keyfile] = key

    def hasKey(self, keyfile):
        """Returns whether or not the store contains a key.

        Args:
            keyfile (str): the path to the key

        Returns:
            bool: True if the store contains that key. False otherwise.
        """

        return (keyfile in self._keys)

    def delKey(self, keyfile):
        """Remove a key from the store.

        Args:
            keyfile (str): the path to the key
        """

        try:
            del self._keys[keyfile]
        except KeyError:
            logging.warning('The key {} is not stored in the key store'.format(keyfile))
            return

    def getKey(self, keyfile):
        """Returns the key from the store.

        Args:
            keyfile (str): the path to the key

        Returns:
            paramiko key: the key
        """

        return self._keys[keyfile]

KEYSTORE = KeyStore()