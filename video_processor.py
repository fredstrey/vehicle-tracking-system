# video_processor.py

import cv2
import numpy as np
from PIL import Image
import torch
import time
import os
import json
import shutil
from datetime import datetime
from rfdetr import RFDETRBase
from rfdetr.util.coco_classes import COCO_CLASSES

from tracker import ObjectTracker
from utils import point_in_zone

class VideoProcessor:
    """
    Orquestra o processo de detecção, rastreamento e contagem de veículos em um vídeo.
    """
    def __init__(self, config):
        self.config = config
        self.model = self._load_model()
        self.tracker = ObjectTracker(
            max_distance=config.MAX_DISTANCE,
            max_missed=config.MAX_MISSED,
            max_tracking_time=config.MAX_TRACKING_TIME
        )
        self.od_counter = {}
        self.class_counter = {cls: 0 for cls in config.CLASSES_TO_COUNT}

    def _load_model(self):
        print("Carregando modelo de detecção...")
        model = RFDETRBase()
        print(f"Modelo carregado. Usando dispositivo: {self.config.DEVICE}")
        return model

    def run(self):
        """
        Inicia e gerencia o loop de processamento do vídeo.
        """
        cap = cv2.VideoCapture(self.config.INPUT_VIDEO)
        if not cap.isOpened():
            print(f"Erro ao abrir o vídeo: {self.config.INPUT_VIDEO}")
            return

        # Propriedades do vídeo e configuração do writer
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(self.config.OUTPUT_VIDEO, fourcc, fps, (width, height))

        print(f"Processando {frame_count} frames de {self.config.INPUT_VIDEO}...")
        
        current_frame_num = 0
        start_time = time.time()
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                current_frame_num += 1
                processed_frame = self._process_frame(frame, current_frame_num)
                out.write(processed_frame)

                # Exibição de progresso
                if current_frame_num % 100 == 0:
                    self._print_progress(current_frame_num, frame_count, start_time)
                
                # Opcional: mostrar vídeo em tempo real
                cv2.imshow("Processamento", processed_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        finally:
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            self._save_results()
            print("Processamento finalizado.")

    def _process_frame(self, frame, frame_num):
        """Processa um único frame: detecção, rastreamento e contagem."""
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        detections = self.model.predict(img, threshold=0.5)
        
        # **INÍCIO DA CORREÇÃO**
        # Prepara os dados para o tracker, convertendo class_id para class_name
        processed_detections = []
        for box, class_id in zip(detections.xyxy, detections.class_id):
            class_name = COCO_CLASSES[class_id]
            if class_name in self.config.CLASSES_TO_COUNT:
                processed_detections.append((box, class_name))
        
        tracked_objects = self.tracker.update(processed_detections)
        # **FIM DA CORREÇÃO**
        
        for oid, data in tracked_objects.items():
            self._update_zone_logic(data)
            self._update_counting_logic(data, frame_num)
        
        self._draw_overlays(frame, tracked_objects)
        return frame

    def _update_zone_logic(self, data):
        """Atualiza o histórico de zonas de um objeto."""
        cx, cy = data['centroid']
        current_zone = None
        for zname, poly in self.config.ZONES.items():
            if point_in_zone((cx, cy), poly):
                current_zone = zname
                break
        
        if current_zone:
            data['current_zone_frames'] = data.get('current_zone_frames', 0) + 1
            if data['current_zone_frames'] >= self.config.MIN_FRAMES_TO_ENTER_ZONE:
                if current_zone not in data['zones_visited']:
                    if not data['zones_passed'] or data['zones_passed'][-1] != current_zone:
                        data['zones_passed'].append(current_zone)
                        data['zones_visited'].add(current_zone)
        else:
            data['current_zone_frames'] = 0

    def _update_counting_logic(self, data, frame_num):
        """Verifica se um objeto completou uma rota e o conta."""
        if not data['counted'] and len(data['zones_passed']) >= 2:
            origin = data['zones_passed'][0]
            destination = data['zones_passed'][-1]
            route = f"{origin}->{destination}"
            
            self.od_counter[route] = self.od_counter.get(route, 0) + 1
            self.class_counter[data['initial_class']] += 1
            data['counted'] = True
            data['count_frame'] = frame_num

    def _draw_overlays(self, frame, tracked_objects):
        """Desenha todas as informações visuais no frame."""
        # Desenha zonas
        for zname, poly in self.config.ZONES.items():
            cv2.polylines(frame, [np.array(poly, np.int32)], True, self.config.COLOR_ZONE, 2)
            cx_zone = int(np.mean([p[0] for p in poly]))
            cy_zone = int(np.mean([p[1] for p in poly]))
            cv2.putText(frame, zname, (cx_zone - 30, cy_zone), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.config.COLOR_ZONE, 2)

        # Desenha objetos rastreados
        for oid, data in tracked_objects.items():
            x1, y1, x2, y2 = map(int, data['box'])
            color = self.config.COLOR_BOX_COUNTED if data['counted'] else self.config.COLOR_BOX_UNCOUNTED
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"ID:{oid} {data['initial_class']}"
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Desenha contadores
        self._draw_counters(frame)
    
    def _draw_counters(self, frame):
        """Desenha os textos dos contadores OD e por classe."""
        # Contagem OD
        y0 = 30
        cv2.putText(frame, "Contagem OD:", (10, y0), cv2.FONT_HERSHEY_SIMPLEX, self.config.FONT_SCALE_INFO, self.config.COLOR_TEXT_OD, 2)
        sorted_od = sorted(self.od_counter.items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (route, cnt) in enumerate(sorted_od):
            cv2.putText(frame, f"{route}: {cnt}", (10, y0 + 30 * (i+1)), cv2.FONT_HERSHEY_SIMPLEX, self.config.FONT_SCALE_COUNTER, self.config.COLOR_TEXT_OD, 2)
        
        # Contagem por Classe
        y_cls = y0 + 30 * (len(sorted_od) + 2)
        cv2.putText(frame, "Contagem por Classe:", (10, y_cls), cv2.FONT_HERSHEY_SIMPLEX, self.config.FONT_SCALE_INFO, self.config.COLOR_TEXT_CLASS, 2)
        for i, (cls, cnt) in enumerate(self.class_counter.items()):
            cv2.putText(frame, f"{cls}: {cnt}", (10, y_cls + 30 * (i+1)), cv2.FONT_HERSHEY_SIMPLEX, self.config.FONT_SCALE_COUNTER, self.config.COLOR_TEXT_CLASS, 2)

    def _print_progress(self, current_frame, total_frames, start_time):
        """Imprime o progresso do processamento no console."""
        percent_complete = current_frame / total_frames * 100
        elapsed = time.time() - start_time
        eta = (elapsed / current_frame) * (total_frames - current_frame) if current_frame > 0 else 0
        print(f"Progresso: {percent_complete:.1f}% | Frame: {current_frame}/{total_frames} | ETA: {eta/60:.1f} min")

    def _save_results(self):
        """Salva os dados de contagem e rastreamento em arquivos JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = f"results_{timestamp}"
        os.makedirs(results_dir, exist_ok=True)
        
        try:
            # Salvar contadores
            with open(f"{results_dir}/od_counter.json", "w") as f:
                json.dump(self.od_counter, f, indent=4)
            with open(f"{results_dir}/class_counter.json", "w") as f:
                json.dump(self.class_counter, f, indent=4)
            
            # Copiar vídeo processado
            if os.path.exists(self.config.OUTPUT_VIDEO):
                shutil.copy(self.config.OUTPUT_VIDEO, results_dir)
            
            print("\n" + "="*50)
            print("Resultados salvos com sucesso!")
            print(f"Diretório: {results_dir}")
            print("="*50)
            
            # Resumo no console
            print("\nResumo Final:")
            print("Contagem OD:")
            if not self.od_counter:
                print("  Nenhuma rota contada.")
            else:
                for route, count in self.od_counter.items():
                    print(f"  {route}: {count}")
            
            print("\nContagem por Classe:")
            for cls, count in self.class_counter.items():
                print(f"  {cls}: {count}")

        except Exception as e:
            print(f"Erro ao salvar resultados: {e}")