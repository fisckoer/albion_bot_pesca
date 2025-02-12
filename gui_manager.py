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
        """
        Configura la interfaz gráfica de usuario.
        """
        dpg.create_context()  # Crear el contexto de DearPyGui
        dpg.create_viewport(title='Fisherman', width=700, height=500)  # Crear la ventana principal

        # Crear una ventana dentro del viewport
        with dpg.window(label="Fisherman Window", width=684, height=460):
            # Campo para la cantidad de puntos de pesca
            dpg.add_input_int(label="Amount Of Spots", max_value=10, min_value=0, tag="Amount_Of_Spots")
            
            # Campo para el umbral de volumen
            dpg.add_input_int(label="Set Volume Threshold", max_value=100000,callback = self.save_volume,
                               min_value=0, default_value=int(self.settings_manager.get_setting('Settings', 'Volume_Threshold')), tag="Set_Volume_Threshold")
            
            # Botón para generar coordenadas de pesca
            with dpg.group(horizontal=True):
                dpg.add_button(label="Set Fishing Spots", width=130, callback=self.generate_coords)
                dpg.add_tooltip(dpg.last_item(), label ="Starts function that lets you select fishing spots")
            
            # Botón para definir la zona de seguimiento
            with dpg.group(horizontal=True):
                dpg.add_button(label="Set Tracking Zone", callback=self.grab_screen)
                dpg.add_tooltip(dpg.last_item(),label = "Sets zone bot tracks for solving fishing minigame")
            
            dpg.add_spacer(height=3)
            
            # Botón para iniciar el bot
            with dpg.group(horizontal=True):
                dpg.add_button(label="Start Bot", callback=self.start_bot)
                dpg.add_tooltip(dpg.last_item(), label= "Starts the bot")

            # Botón para iniciar asistente de pesca
            with dpg.group(horizontal=True):
                dpg.add_button(label="Start Asistent", callback=self.start_asistent)
                dpg.add_tooltip(dpg.last_item(), label= "Inicia el asitente para pesca")    
            
            # Botón para detener el bot
          
            with dpg.group(horizontal=True):
                dpg.add_button(label="Stop Bot", callback=self.stop_bot)
                dpg.add_tooltip(dpg.last_item(), label= "Stops the bot")
            
            # Botón para guardar la configuración
          
            with dpg.group(horizontal=True):
                dpg.add_button(label="Save Settings", callback=self.save_settings)
                dpg.add_tooltip(dpg.last_item(), label= "Saves bot settings to settings.ini")
            
            dpg.add_spacer(height=5)
            #dpg.set_y_scroll("Log_Info", float('inf'))
            # Logger para mostrar mensajes de información
            with dpg.group(horizontal=True):
                dpg.add_text("Log:")
                dpg.add_input_text(multiline=True, tag="Log_Info", width=600, height=200, readonly=True)
            # Desplazar al final del log automáticamente
            
        # Configurar el viewport
        dpg.create_viewport(title='Fisherman', width=700, height=500)
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
        self.image_detection.screen_area = self.bot_confirg_manage.screen_area
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
            