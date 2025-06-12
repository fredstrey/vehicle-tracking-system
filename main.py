# main.py

import config
from video_processor import VideoProcessor
import os

def main():
    """
    Ponto de entrada principal para o script de análise de vídeo.
    """
    # Verifica se o vídeo de entrada existe
    if not os.path.exists(config.INPUT_VIDEO):
        print(f"Erro: Arquivo de vídeo não encontrado em '{config.INPUT_VIDEO}'")
        print("Verifique o caminho no arquivo 'config.py'.")
        return

    # Instancia e executa o processador de vídeo
    processor = VideoProcessor(config)
    processor.run()

if __name__ == "__main__":
    main()