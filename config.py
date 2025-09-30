# config.py

import torch

# --- Configurações Gerais ---
INPUT_VIDEO = "stream_saida.mp4"
OUTPUT_VIDEO = "video_processado.mp4"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --- Parâmetros do Rastreador ---
MAX_DISTANCE = 80  # Distância máxima (em pixels) para associar uma detecção a um objeto existente.
MAX_MISSED = 5     # Número de frames consecutivos que um objeto pode ficar sem ser detectado antes de ser removido.
MAX_TRACKING_TIME = 300 # Tempo máximo (em frames) que um objeto já contado permanece sendo rastreado.

# --- Parâmetros da Lógica de Negócio ---
MIN_FRAMES_TO_ENTER_ZONE = 3  # Número mínimo de frames que um objeto deve estar em uma zona para registrar a entrada.
CLASSES_TO_COUNT = {"car", "motorcycle", "bus", "truck"} # Classes de objetos a serem contadas.

# --- Definição das Zonas de Contagem ---
# As zonas são polígonos definidos por uma lista de pontos (x, y).
ZONES = {
    "Rua 1": [(335, 435), (540, 355), (790, 445), (455, 550)],
    "Rua 2": [(400, 978), (278, 678), (420, 612), (663, 900)],
    "Rua 3": [(1300, 960), (1815, 620), (1890, 685), (1430, 1040)],
    "Rua 4": [(1295, 470), (1437, 431), (1783, 505), (1705, 595)]
}

# --- Configurações de Visualização ---
FONT = "FONT_HERSHEY_SIMPLEX"
FONT_SCALE_INFO = 0.7
FONT_SCALE_COUNTER = 0.6
COLOR_ZONE = (255, 255, 0)      # Ciano
COLOR_TEXT_INFO = (0, 0, 255)   # Vermelho
COLOR_TEXT_OD = (0, 255, 0)     # Verde
COLOR_TEXT_CLASS = (0, 255, 255) # Amarelo
COLOR_BOX_UNCOUNTED = (0, 255, 0) # Verde

COLOR_BOX_COUNTED = (0, 0, 255)   # Vermelho
