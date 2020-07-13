FROM python:alpine
COPY . /home/user/DicePP
RUN apk add --no-cache tzdata python3-dev py3-multidict py3-yarl && \
	apk add --no-cache gcc g++ make automake freetype-dev && \
	pip3 install --upgrade pip && \
    pip3 install --no-cache-dir "nonebot[scheduler]" && \
    pip3 install --no-cache-dir -r /home/user/DicePP/requirements.txt

CMD ["python3", "/home/user/DicePP/dicepp.py"]