import os.path
import yaml


THIS_SCRIPT_FOLDER = os.path.dirname(__file__)


class Settings:
    """Settings for SilenceNotifier.

    All settings set in settings.yaml can be accessed as properties of an
    instance of this class.
    """
    def __init__(self, *config_files):
        self._settings = dict()
        self.load_settings(config_files)

    def load_settings(self, config_files=None):
        """Populate this instance with the settings from the setting files.

        Args:
            config_files: List of configuration files to read in from. The
                default configuration file is always read first, so you need not
                specify it. If not specified, the default settings.yaml file
                is used (after settings_default.yaml, of course). Settings from
                later configuration files overwrite values in earlier ones.

        Note that this method is executed as a part of __init__.
        """
        if not config_files:
            actual_config_files = self.get_default_config_files()
        else:
            actual_config_files = [self.get_default_default_config_file()] + \
                                  config_files

        self._settings = self.load_from_file(actual_config_files)

    def get_default_config_files(self):
        """Return the default list of configuration files."""
        config_file_usr = self.get_default_user_config_file()
        config_file_std = self.get_default_default_config_file()

        return [config_file_std, config_file_usr]

    def get_default_user_config_file(self):
        """Return the default path for the custom settings file."""
        return self.process_config_path("settings.yaml")

    def get_default_default_config_file(self):
        """Return the default path for the default settings file."""
        return self.process_config_path("settings_default.yaml")

    @staticmethod
    def process_config_path(filename):
        """Process filename so it becomes absolute path, assuming it to be a
        file in the parent folder."""
        rel_path = os.path.join('..', filename)
        absolute_path = os.path.join(THIS_SCRIPT_FOLDER, rel_path)
        return os.path.normpath(absolute_path)

    @staticmethod
    def load_from_file(config_files):
        """Create dictionary with settings from the list of files.

        Args:
            config_files: List of files to read settings from.

        Returns:
            Dictionary where items defined in earlier files are overwritten by
            same items found in later files.
        """
        settings = dict()

        for single_config_file in config_files:
            with open(single_config_file) as fp:
                document = yaml.load(fp)

            settings.update(document)
        return settings

    def __getattr__(self, item):
        """Make settings loaded from files available as properties."""
        try:
            return self._settings[item]
        except KeyError:
            raise AttributeError(item)
