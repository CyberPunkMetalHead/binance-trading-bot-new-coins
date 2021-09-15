FROM python:alpine3.14	

RUN apk add --no-cache git build-base && \
    git clone https://github.com/CyberPunkMetalHead/binance-trading-bot-new-coins /app && \
    pip3 install python-binance pyaml
	
WORKDIR app	
	
CMD ["python3", "main.py"]
