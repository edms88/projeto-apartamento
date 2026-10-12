FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py banco.py financeiro.py ./
RUN useradd --create-home appuser && mkdir -p /app/dados && chown -R appuser:appuser /app
USER appuser
ENV REQUIRE_APP_PASSWORD=true
EXPOSE 8501
CMD ["sh", "-c", "exec python -m streamlit run app.py --server.address 0.0.0.0 --server.port ${PORT:-8501} --server.headless true"]
