FROM python:3.12-alpine
WORKDIR /app
COPY server.py index.html ./
EXPOSE 80
CMD ["python", "server.py"]
