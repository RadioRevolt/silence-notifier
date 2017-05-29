import os.path
import yaml


THIS_SCRIPT_FOLDER = os.path.dirname(__file__)


class Settings:
    def __init__(self, *config_files):
        self._settings = dict()
        self.load_settings(config_files)

    def load_settings(self, config_files=None):
        if not config_files:
            actual_config_files = self.get_default_config_files()
        else:
            actual_config_files = [self.get_default_default_config_file()] + \
                                  config_files

        self._settings = self.load_from_file(actual_config_files)

    def get_default_config_files(self):
        config_file_usr = self.get_default_user_config_file()
        config_file_std = self.get_default_default_config_file()

        return [config_file_std, config_file_usr]

    def get_default_user_config_file(self):
        return self.process_config_path("settings.yaml")

    def get_default_default_config_file(self):
        return self.process_config_path("settings_default.yaml")

    @staticmethod
    def process_config_path(filename):
        rel_path = os.path.join('..', filename)
        absolute_path = os.path.join(THIS_SCRIPT_FOLDER, rel_path)
        return os.path.normpath(absolute_path)

    @staticmethod
    def load_from_file(config_files):
        settings = dict()

        for single_config_file in config_files:
            with open(single_config_file) as fp:
                document = yaml.load(fp)

            settings.update(document)
        return settings

    def __getattr__(self, item):
        try:
            return self._settings[item]
        except KeyError:
            raise AttributeError(item)
