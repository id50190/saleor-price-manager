# Это файл-обертка Python, который будет вызывать Rust-библиотеку
from decimal import Decimal
import asyncio
from app.services.markup_service import markup_service

# Импортируем Rust-модуль
try:
    import price_calculator
except ImportError:
    try:
        # Try importing from rust_modules directory
        from rust_modules import price_calculator  
    except ImportError:
        # Fallback to pure Python implementation if Rust module is not available
        price_calculator = None
        print("Warning: Rust price_calculator module not available, using Python fallback")

def _python_calculate_price(base_price: str, markup_percent: str) -> str:
    """
    Pure Python fallback for price calculation when Rust module is unavailable
    """
    base = Decimal(base_price)
    markup = Decimal(markup_percent)
    
    # Formula: base_price * (1 + markup_percent/100)
    markup_factor = Decimal('1') + (markup / Decimal('100'))
    final_price = base * markup_factor
    
    # Round to 2 decimal places
    return str(final_price.quantize(Decimal('0.01')))

async def calculate_price_with_markup(product_id: str, channel_id: str, base_price: Decimal) -> Decimal:
    """
    Рассчитывает итоговую цену продукта с учетом наценки канала
    Использует Rust для высокой производительности или Python fallback
    """
    # Получаем наценку для канала
    markup_percent = await markup_service.get_channel_markup(channel_id)
    
    # Используем Rust модуль если доступен, иначе Python
    if price_calculator:
        final_price = price_calculator.calculate_price(
            str(base_price), 
            str(markup_percent)
        )
    else:
        final_price = _python_calculate_price(
            str(base_price),
            str(markup_percent)
        )
    
    return Decimal(final_price)

def _python_batch_calculate(batch_data):
    """
    Pure Python fallback for batch price calculation
    """
    results = []
    for item in batch_data:
        final_price = _python_calculate_price(
            item["base_price"], 
            item["markup_percent"]
        )
        results.append({
            "product_id": item["product_id"],
            "final_price": final_price
        })
    return results

async def batch_calculate_prices(items):
    """
    Массовый расчет цен для нескольких продуктов
    Использует Rust для высокой производительности или Python fallback
    """
    # Подготавливаем данные с наценками
    batch_data = []
    for item in items:
        markup = await markup_service.get_channel_markup(item["channel_id"])
        batch_data.append({
            "product_id": item["product_id"],
            "base_price": str(item["base_price"]),
            "markup_percent": str(markup)
        })
    
    # Используем Rust модуль если доступен, иначе Python
    if price_calculator:
        results = price_calculator.batch_calculate(batch_data)
    else:
        results = _python_batch_calculate(batch_data)
    
    # Преобразуем результаты обратно в Decimal
    for i, result in enumerate(results):
        results[i]["final_price"] = Decimal(result["final_price"])
    
    return results
