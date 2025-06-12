# Vehicle Tracking System 🚗📹

Este projeto é um sistema simples de **rastreamento de veículos em vídeo**, desenvolvido em Python, que utiliza técnicas de **visão computacional** para detectar, contar e acompanhar veículos ao longo de um trecho de vídeo.

## 🎯 Objetivo

Desenvolver um sistema que:

- Detecta veículos em um vídeo;
- Acompanha o movimento dos veículos ao longo dos quadros;
- Conta a quantidade de veículos que cruzam uma linha virtual;
- Exibe visualmente as caixas delimitadoras e o ID de rastreamento de cada veículo.

## 📹 Demonstração

Assista ao vídeo demonstrando o funcionamento do sistema:

➡️ [Clique aqui para assistir no YouTube](https://www.youtube.com/watch?v=EperFa-XS4w)

## 🧠 Tecnologias Utilizadas

- Python 3
- OpenCV
- NumPy
- Algoritmos de rastreamento baseado em centroides (como o `CentroidTracker`)

## 📁 Estrutura do Projeto

vehicle-tracking-system/
│
├── main.py # Código principal para processamento do vídeo
├── tracker.py # Classe do algoritmo de rastreamento
├── input/ # Pasta com os vídeos de entrada
└── output/ # Pasta para salvar vídeos processados


## ▶️ Como Executar

1. Clone o repositório:

```bash
git clone https://github.com/fredstrey/vehicle-tracking-system.git
cd vehicle-tracking-system

Instale as dependências:

python main.py

Coloque o vídeo que deseja processar na pasta input/.

Execute o script:

python main.py

O vídeo processado será exibido na tela com os veículos rastreados e contados.
