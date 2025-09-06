# Это файл-обертка Python, который будет вызывать Rust-библиотеку
from decimal import Decimal
import asyncio
from app.services.markup_service import markup_service

# Импортируем Rust-модуль
from rust_modules import price_calculator

async def calculate_price_with_markup(product_id: str, channel_id: str, base_price: Decimal) -> Decimal:
    """
    Рассчитывает итоговую цену продукта с учетом наценки канала
    Этот метод делегирует вычисления в Rust-библиотеку
    """
    # Получаем наценку для канала
    markup_percent = await markup_service.get_channel_markup(channel_id)
    
    # Вызываем Rust-функцию для расчета цены
    # Передаем base_price как строку для точности
    final_price = price_calculator.calculate_price(
        str(base_price), 
        str(markup_percent)
    )
    
    return Decimal(final_price)

async def batch_calculate_prices(items):
    """
    Массовый расчет цен для нескольких продуктов
    Значительно эффективнее на Rust
    """
    # Подготавливаем данные для передачи в Rust
    batch_data = []
    for item in items:
        markup = await markup_service.get_channel_markup(item["channel_id"])
        batch_data.append({
            "product_id": item["product_id"],
            "base_price": str(item["base_price"]),
            "markup_percent": str(markup)
        })
    
    # Вызываем Rust-функцию для массового расчета
    results = price_calculator.batch_calculate(batch_data)
    
    # Преобразуем результаты обратно в Decimal
    for i, result in enumerate(results):
        results[i]["final_price"] = Decimal(result["final_price"])
    
    return results
