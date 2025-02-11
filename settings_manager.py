import configparser

class SettingsManager:
    """
    Clase para manejar la configuración del bot.
    Lee y escribe en el archivo 'settings.ini'.
    """
    def __init__(self):
        self.parser = configparser.ConfigParser()
        self.parser.read('settings.ini')

    def get_setting(self, section, key):
        """
        Obtiene un valor de configuración del archivo 'settings.ini'.
        """
        return self.parser.get(section, key)

    def set_setting(self, section, key, value):
        """
        Actualiza un valor de configuración en el archivo 'settings.ini'.
        """
        self.parser.set(section, key, str(value))
        with open('settings.ini', 'w') as configfile:
            self.parser.write(configfile)