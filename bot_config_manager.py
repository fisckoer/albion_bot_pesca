import pyautogui
import win32api
import time

class BotConfigManager:
    """
    Clase para manejar la configuración del bot, como la generación de coordenadas y la zona de seguimiento.
    """
    def __init__(self):
        self.coords = []  # Lista de coordenadas de pesca
        self.screen_area = None  # Zona de seguimiento en la pantalla

    def generate_coords(self, amount_of_spots, log_callback):
        """
        Genera las coordenadas de pesca basadas en la entrada del usuario.
        El usuario debe presionar la barra espaciadora sobre los puntos deseados.

        :param amount_of_spots: Número de puntos de pesca a generar.
        :param log_callback: Función de callback para registrar mensajes en la GUI.
        """
        self.coords = []  # Reiniciar la lista de coordenadas
        state_left = win32api.GetKeyState(0x01)  # Estado del botón izquierdo del mouse

        for n in range(amount_of_spots):
            if log_callback:
                log_callback(f'[spot:{n + 1}]|Press Spacebar over the spot you want')
            time.sleep(1)

            while True:
                a = win32api.GetKeyState(0x20)  # Estado de la barra espaciadora
                if a != state_left:
                    state_left = a
                    if a < 0:  # Barra espaciadora presionada
                        break
                time.sleep(0.001)

            x, y = pyautogui.position()
            self.coords.append((x, y))
            if log_callback:
                log_callback(f'Position:{n + 1} Saved. | {x, y}')

        if log_callback:
            log_callback(f'Successfully saved {amount_of_spots} fishing spots.')

    def grab_screen(self, log_callback=None):
        """
        Permite al usuario definir la zona de seguimiento en la pantalla.
        El usuario debe arrastrar el mouse mientras mantiene presionada la barra espaciadora.

        :param log_callback: Función de callback para registrar mensajes en la GUI.
        """
        state_left = win32api.GetKeyState(0x20)  # Estado de la barra espaciadora
        image_coords = []

        if log_callback:
            log_callback('Please hold and drag space over tracking zone (top left to bottom right)')

        while True:
            a = win32api.GetKeyState(0x20)
            if a != state_left:  # Estado de la barra espaciadora cambiado
                state_left = a
                if a < 0:  # Barra espaciadora presionada
                    x, y = pyautogui.position()
                    image_coords.append((x, y))
                else:  # Barra espaciadora liberada
                    x, y = pyautogui.position()
                    image_coords.append((x, y))
                    break
            time.sleep(0.001)

        start_point = image_coords[0]
        end_point = image_coords[1]
        self.screen_area = (start_point[0], start_point[1], end_point[0], end_point[1])

        if log_callback:
            log_callback(f'Updated tracking area to {self.screen_area}')