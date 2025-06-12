# tracker.py

import math
from collections import OrderedDict

class ObjectTracker:
    """
    Rastreia objetos detectados em frames de vídeo.
    
    Atribui um ID único a cada objeto e acompanha sua posição,
    mantendo o rastreamento mesmo que a detecção falhe por alguns frames.
    """
    def __init__(self, max_distance, max_missed, max_tracking_time):
        self.max_distance = max_distance
        self.max_missed = max_missed
        self.max_tracking_time = max_tracking_time
        self.next_id = 0
        self.tracked_objects = OrderedDict()

    def _get_centroid(self, box):
        x1, y1, x2, y2 = map(int, box)
        return (x1 + x2) // 2, (y1 + y2) // 2

    def update(self, processed_detections):
        """
        Atualiza o estado do rastreador com as novas detecções de um frame.
        Args:
            processed_detections (list): Uma lista de tuplas, onde cada tupla contém (box, class_name).
        """
        # Limpa objetos antigos antes de associar
        self._cleanup_old_tracks()
        
        current_ids = set()
        unmatched_detections = []

        # Tenta associar detecções a objetos existentes
        for box, cls_name in processed_detections:
            cx, cy = self._get_centroid(box)
            best_id, best_dist = None, self.max_distance

            # Prioriza associar a objetos não contados e recentemente vistos
            sorted_oids = sorted(
                self.tracked_objects.keys(),
                key=lambda oid: (self.tracked_objects[oid].get('counted', False), self.tracked_objects[oid]['missed'])
            )

            for oid in sorted_oids:
                if oid in current_ids:
                    continue
                
                data = self.tracked_objects[oid]
                dist = math.hypot(cx - data['centroid'][0], cy - data['centroid'][1])
                
                if dist < best_dist:
                    best_dist = dist
                    best_id = oid

            if best_id is not None:
                # Atualiza um objeto existente
                self.tracked_objects[best_id]['centroid'] = (cx, cy)
                self.tracked_objects[best_id]['box'] = box
                self.tracked_objects[best_id]['missed'] = 0
                self.tracked_objects[best_id]['frames_active'] += 1
                current_ids.add(best_id)
            else:
                unmatched_detections.append({'box': box, 'class': cls_name})
        
        # Incrementa 'missed' para objetos não associados
        for oid in self.tracked_objects.keys():
            if oid not in current_ids:
                self.tracked_objects[oid]['missed'] += 1
        
        # Cria novos objetos para detecções não associadas
        for det in unmatched_detections:
            self._register_new_object(det['box'], det['class'])

        return self.tracked_objects

    def _register_new_object(self, box, cls_name):
        """Cria um novo objeto rastreado."""
        self.tracked_objects[self.next_id] = {
            'class': cls_name,
            'initial_class': cls_name,
            'centroid': self._get_centroid(box),
            'box': box,
            'zones_passed': [],
            'zones_visited': set(),
            'counted': False,
            'missed': 0,
            'frames_active': 1,
            'current_zone_frames': 0,
            'id': self.next_id
        }
        self.next_id += 1

    def _cleanup_old_tracks(self):
        """Remove objetos que foram perdidos por muitos frames ou estão sendo rastreados há muito tempo."""
        ids_to_remove = []
        for oid, data in self.tracked_objects.items():
            lost = data['missed'] > self.max_missed
            too_long = data['counted'] and data['frames_active'] > self.max_tracking_time
            if lost or too_long:
                ids_to_remove.append(oid)
        
        for oid in ids_to_remove:
            if oid in self.tracked_objects:
                del self.tracked_objects[oid]