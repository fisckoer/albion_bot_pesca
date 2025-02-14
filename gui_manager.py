import dearpygui.dearpygui as dpg
import threading

class GUIManager:
    """
    Clase para manejar la interfaz gráfica de usuario (GUI) utilizando DearPyGui.
    """
    def __init__(self, fishing_bot, settings_manager, bot_config_manager,image_detection,audio_manager,miniGameSolver):
        self.fishing_bot = fishing_bot
        self.settings_manager = settings_manager
        self.bot_config_manager = bot_config_manager
        self.image_detection = image_detection
        self.audio_manager = audio_manager
        self.miniGameSolver =miniGameSolver

    def setup_gui(self):
        dpg.create_context()

        # Configuración de colores pastel en azules y grises
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 57, 104), category=dpg.mvThemeCat_Core)  # Azul oscuro BBVA
                dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 173, 239), category=dpg.mvThemeCat_Core)      # Azul claro BBVA
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 123, 193), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 97, 159), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (240, 240, 240), category=dpg.mvThemeCat_Core)   # Gris claro
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255), category=dpg.mvThemeCat_Core)       # Blanco
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0), category=dpg.mvThemeCat_Core) 
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 5, category=dpg.mvThemeCat_Core)
              
        # Cargar y aplicar una fuente en negritas
        with dpg.font_registry():
            bold_font = dpg.add_font("./robo/ROBO.ttf", 12)  # Reemplaza con la ruta a tu fuente
        dpg.bind_font(bold_font)

        with dpg.window(label="Fisherman Control Panel", width=780, height=580, pos=(10, 10)):
            with dpg.group(horizontal=True):
                dpg.add_input_int(label="Amount Of Spots", max_value=10, min_value=0, tag="Amount_Of_Spots" , width=100)
  
                dpg.add_input_int(label="Volume Threshold", max_value=100000, callback=self.save_volume, 
                                  min_value=0, default_value=int(self.settings_manager.get_setting('Settings', 'Volume_Threshold')), tag="Set_Volume_Threshold" , width=200)

            with dpg.group(horizontal=True):
                dpg.add_button(label="Set Fishing Spots", width=150, callback=self.generate_coords)
                dpg.add_button(label="Set Tracking Zone", width=150, callback=self.grab_screen)

            with dpg.group(horizontal=True):
                dpg.add_button(label="Start Bot", width=150, callback=self.start_bot)
                dpg.add_button(label="Start Assistant", width=150, callback=self.start_asistent)
                dpg.add_button(label="Stop Bot", width=150, callback=self.stop_bot)
                dpg.add_button(label="Save Settings", width=150, callback=self.save_settings)

            dpg.add_separator()
            dpg.add_text("Log:")
            dpg.add_child_window(width=750, height=300, border=True, autosize_x=True, autosize_y=True)
            dpg.add_input_text(multiline=True, tag="Log_Info", width=-1, height=-1, readonly=True, tracked=True)
            

            
        # Configurar el viewport
        dpg.bind_theme(global_theme)
        dpg.create_viewport(title='Fisherman Bot', width=800, height=600)
        dpg.setup_dearpygui()
        dpg.show_viewport()
     

    def generate_coords(self, sender, data):
        """
        Llama a la función para generar coordenadas de pesca.
        """
        self.log_info("Click on generate coords")
        amount_of_spots = dpg.get_value("Amount_Of_Spots")  # Obtener el valor del campo "Amount Of Spots"
        self.bot_config_manager.generate_coords(amount_of_spots, log_callback=self.log_info)
        self.log_info(f"Generated {amount_of_spots} fishing spots.")

    def grab_screen(self, sender, data):
        """
        Llama a la función para definir la zona de seguimiento.
        """
        self.bot_config_manager.grab_screen(log_callback=self.log_info)
        self.image_detection.screen_area = self.bot_config_manager.screen_area
        self.log_info(f"Tracking zone updated: {self.image_detection.screen_area}")

    def start_bot(self, sender, data):
        """
        Inicia el bot cuando se presiona el botón 'Start Bot'.
        """
        self.fishing_bot.log_callback=self.log_info
        self.fishing_bot.coords= self.bot_config_manager.coords
        self.fishing_bot.state = "STARTED"
        threading.Thread(target=self.fishing_bot.cast_hook).start()
        self.log_info("Bot started.")

    def stop_bot(self, sender, data):
        """
        Detiene el bot cuando se presiona el botón 'Stop Bot'.
        """
        self.fishing_bot.state = "STOPPED"
        self.fishing_bot.audio_manager.stop_listening
        self.miniGameSolver.status="STOP"
        self.log_info("Bot stopped.")

    def save_volume(self, sender, data):
        """
        Guarda el umbral de volumen en la configuración.
        """
        max_volume = dpg.get_value("Set_Volume_Threshold")  # Obtener el valor del campo "Set Volume Threshold"
        self.settings_manager.set_setting('Settings', 'Volume_Threshold', max_volume)
        self.audio_manager.max_volume=max_volume
        self.log_info(f'Max Volume Updated to: {max_volume}')

    def save_settings(self, sender, data):
        """
        Guarda la configuración actual en el archivo 'settings.ini'.
        """
        self.settings_manager.set_setting('Settings', 'tracking_zone', str(self.bot_config_manager.screen_area))
        self.log_info('Saved New Settings to settings.ini')

    def log_info(self, message):
        """
        Muestra un mensaje en el logger de la GUI.
        """
        dpg.set_value("Log_Info", dpg.get_value("Log_Info") + message + "\n")

    def start_asistent(self):
        self.miniGameSolver.status="START"
        threading.Thread(target=self.miniGameSolver.solve).start()
