FROM python:3.9

WORKDIR /app

RUN apt update && apt install -y ffmpeg

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
