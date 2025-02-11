from settings_manager import SettingsManager
from audio_manager import AudioManager
from image_detection import ImageDetection
from fishing_bot import FishingBot
from gui_manager import GUIManager
from bot_config_manager import BotConfigManager



import dearpygui.dearpygui as dpg

def main():
    # Inicialización de clases
    settings_manager = SettingsManager()
    max_volume = int(settings_manager.get_setting('Settings', 'Volume_Threshold'))
    screen_area = eval(settings_manager.get_setting('Settings', 'tracking_zone'))
    print(f"max_volume:{max_volume}]")
    print(f" tracking_zone:{screen_area}]")
    audio_manager = AudioManager(max_volume)
    image_detection = ImageDetection(screen_area)
    bot_config_manager = BotConfigManager()
    fishing_bot = FishingBot(bot_config_manager,audio_manager,image_detection, None)
    # Pasamos bot_config_manager, image_detection y el callback del log a FishingBot
    #fishing_bot = FishingBot(bot_config_manager,audio_manager, image_detection)
    gui_manager = GUIManager(fishing_bot , settings_manager, bot_config_manager,image_detection)
    

    # Configuración de la GUI
    gui_manager.setup_gui()

    # Iniciar hilos
    
    #threading.Thread(target=fishing_bot.cast_hook).start()

    # Iniciar la GUI

    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()