FROM python:3.9-slim

WORKDIR /app

# Instala dependências
RUN pip install --no-cache-dir paho-mqtt

# O código será montado como volume
# O ponto de entrada será definido pelo comando no docker-compose.yml

CMD ["python", "iits.py"]