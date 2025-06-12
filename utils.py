# utils.py

import cv2
import numpy as np

def point_in_zone(point, zone_polygon):
    """
    Verifica se um ponto (x, y) está dentro de um polígono.

    Args:
        point (tuple): A coordenada (x, y) do ponto.
        zone_polygon (list): Uma lista de pontos que formam o polígono da zona.

    Returns:
        bool: True se o ponto está dentro do polígono, False caso contrário.
    """
    return cv2.pointPolygonTest(np.array(zone_polygon, np.int32), point, False) >= 0