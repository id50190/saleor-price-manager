#!/usr/bin/env python3
"""
Test script for Rust price calculator module
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, 'app')

def test_python_fallback():
    """Test Python fallback calculation"""
    from services.price_calculator import _python_calculate_price
    
    result = _python_calculate_price("100.00", "15.00")
    expected = "115.00"
    
    print(f"Python fallback test: {result} == {expected}")
    assert result == expected, f"Expected {expected}, got {result}"
    print("✅ Python fallback works correctly")

def test_rust_module():
    """Test Rust module if available"""
    try:
        import price_calculator
        
        result = price_calculator.calculate_price("100.00", "15.00")
        expected = "115.00"
        
        print(f"Rust module test: {result} == {expected}")
        assert result == expected, f"Expected {expected}, got {result}"
        print("✅ Rust module works correctly")
        
        # Test batch calculation
        batch_data = [
            {"product_id": "1", "base_price": "100.00", "markup_percent": "10.00"},
            {"product_id": "2", "base_price": "200.00", "markup_percent": "15.00"}
        ]
        
        results = price_calculator.batch_calculate(batch_data)
        print(f"Batch calculation results: {len(results)} items")
        
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        assert results[0]['final_price'] == '110.00', f"Product 1: expected 110.00, got {results[0]['final_price']}"
        assert results[1]['final_price'] == '230.00', f"Product 2: expected 230.00, got {results[1]['final_price']}"
        
        print("✅ Rust batch calculation works correctly")
        return True
        
    except ImportError:
        print("⚠️  Rust module not available, using Python fallback")
        return False

if __name__ == "__main__":
    print("🧪 Testing price calculation modules...")
    print("="*50)
    
    # Test Python fallback (always available)
    test_python_fallback()
    
    # Test Rust module (if available)
    rust_available = test_rust_module()
    
    print("="*50)
    if rust_available:
        print("🎉 Both Python fallback and Rust module are working!")
    else:
        print("🐍 Python fallback is working (Rust module not built yet)")
        print("💡 Run ./BUILD to compile the Rust module for better performance")
