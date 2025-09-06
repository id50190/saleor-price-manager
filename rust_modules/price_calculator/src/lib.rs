use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use rust_decimal::Decimal;
use rust_decimal::prelude::*;
use serde::{Deserialize, Serialize};

/// Рассчитывает цену с учетом наценки
#[pyfunction]
fn calculate_price(base_price: String, markup_percent: String) -> PyResult<String> {
    let base = Decimal::from_str(&base_price).unwrap_or(Decimal::ZERO);
    let markup = Decimal::from_str(&markup_percent).unwrap_or(Decimal::ZERO);
    
    // Формула расчета: base_price * (1 + markup_percent/100)
    let markup_factor = Decimal::ONE + (markup / Decimal::from(100));
    let final_price = base * markup_factor;
    
    // Округляем до 2 знаков после запятой
    let rounded = final_price.round_dp(2);
    
    Ok(rounded.to_string())
}

/// Массовый расчет цен
#[pyfunction]
fn batch_calculate<'p>(py: Python<'p>, items: &PyList) -> PyResult<&'p PyList> {
    let result = PyList::empty(py);
    
    for item_obj in items.iter() {
        let item = item_obj.downcast::<PyDict>()?;
        
        let product_id = item.get_item("product_id")?.extract::<String>()?;
        let base_price = item.get_item("base_price")?.extract::<String>()?;
        let markup_percent = item.get_item("markup_percent")?.extract::<String>()?;
        
        // Расчет цены
        let final_price = calculate_price(base_price, markup_percent)?;
        
        // Создаем словарь с результатом
        let result_dict = PyDict::new(py);
        result_dict.set_item("product_id", product_id)?;
        result_dict.set_item("final_price", final_price)?;
        
        // Добавляем в список результатов
        result.append(result_dict)?;
    }
    
    Ok(result)
}

/// Регистрация модуля Python
#[pymodule]
fn price_calculator(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(calculate_price, m)?)?;
    m.add_function(wrap_pyfunction!(batch_calculate, m)?)?;
    Ok(())
}
