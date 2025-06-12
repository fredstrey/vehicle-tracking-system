# Vehicle Tracking System 🚗📹

Este projeto é um sistema simples de **rastreamento de veículos em vídeo**, desenvolvido em Python, que utiliza técnicas de **visão computacional** para detectar, contar e acompanhar veículos ao longo de um trecho de vídeo.

Por se tratar de um algoritmo muito simples, possui algumas limitações e medições imprecisas. 

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
- rfdetr 



## ▶️ Como Executar

1. Clone o repositório:
   
git clone https://github.com/fredstrey/vehicle-tracking-system.git
cd vehicle-tracking-system

3. Instale as dependências:

pip install -r requirements.txt

3. Adicione o caminho do vídeo no config.py

4. Execute o script:

python main.py

O vídeo processado será exibido na tela com os veículos rastreados e contados.
