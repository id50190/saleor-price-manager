FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка Rust для компиляции модуля
RUN apt-get update && apt-get install -y curl build-essential && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Копируем код
COPY . .

# Компилируем Rust-модуль
WORKDIR /app/rust_modules/price_calculator
RUN cargo build --release
RUN cp target/release/libprice_calculator.so /app/app/services/

# Запускаем приложение
WORKDIR /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
