""" 
Test Case Context Singleton

"""
import os
import yaml


class TestContext(object):
    """Testing Context Singleton

    Allows definition of any attribute that immediately becomes
    available to all other objects.
    """

    # Define the interior class.
    class __TestContext(object):
        def __init__(self):
            '''Initialize the singleton object.'''

            # Determine the application root directory (up 2). If the
            # new "Framework" sub-directory is found, use that as the
            # root directory.
            self.root_dir = os.path.abspath(__file__)
            for i in range(3):
                self.root_dir = os.path.dirname(self.root_dir)
            if os.path.isdir(os.path.join(self.root_dir, 'Framework')):
                self.root_dir = os.path.join(self.root_dir, 'Framework')
            # Define the test log base directory.
            self.log_base = os.path.dirname(os.path.abspath(__file__))
            for i in range(1):
                self.log_base = os.path.dirname(self.log_base)
            self.log_base = os.path.join(self.log_base, 'log')
            try:
                os.makedirs(self.log_base)
            except os.error:
                pass

            # Define the media resource directory.
            self.media_dir = os.path.join(
                self.root_dir, 'test', 'audio')

            # Read and parse the application configuration.
            self.config_file = os.path.join(self.root_dir, 'config', 'testServerConfig.yaml')
            self._config_dir = os.path.join(self.root_dir, 'config')
            with open(self.config_file, 'r') as f:
                self.config = yaml.full_load(f)

    # Singleton instance storage
    instance = None

    def __init__(self):
        """ Construct the singleton - if not already done. """
        if not TestContext.instance:
            TestContext.instance = TestContext.__TestContext()

    @classmethod
    def flush(cls):
        """ Dispose of the current context. Get a new one. """
        cls.instance = TestContext.__TestContext()

'''
    @property
    def config_dir(self):
        return self._config_dir

    @property
    def soX_dir(self):
        return self._soX_dir

    def __getattr__(self, name):
        """ Get the attribute value of the singleton. """
        return getattr(self.instance, name)

    def __setattr__(self, name, value):
        """ Set the attribute value of the singleton. """
        return setattr(self.instance, name, value)
'''