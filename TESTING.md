# Testing Guide for Saleor Price Manager

🧪 **Comprehensive testing framework with API mocks and browser automation**

## 🎨 Testing Architecture

### **API Testing (pytest)**
- **Unit Tests**: Individual components with mocked dependencies
- **Integration Tests**: Complete workflows and service interactions
- **Performance Tests**: Response times and concurrent handling
- **Mock Strategy**: External services (Saleor API, Redis) fully mocked

### **Frontend Testing (Playwright)**
- **E2E Browser Tests**: Real browser automation across Chrome/Firefox/Safari
- **Mobile Testing**: Responsive design validation
- **Accessibility Testing**: WCAG compliance and keyboard navigation
- **Visual Testing**: UI consistency and error state handling

---

## 🚀 Quick Start

```bash
# Run all tests
./TEST

# Quick deployment verification (30s)
./TEST quick

# API tests only (2 minutes)
./TEST api

# Frontend E2E tests only (5 minutes)
./TEST frontend

# Docker-based testing
./TEST_DOCKER all
```

---

## 🧪 API Testing Details

### **Test Structure**
```
tests/
├── conftest.py              # Shared fixtures and mocks
├── api/
│   ├── test_health.py       # Health endpoint tests
│   ├── test_channels.py     # Channel management tests
│   ├── test_prices.py       # Price calculation tests
│   ├── test_webhooks.py     # Webhook handling tests
│   ├── test_services.py     # Business logic tests
│   └── test_integration.py  # End-to-end workflow tests
└── fixtures/
    └── sample_data.py       # Test data and mock responses
```

### **Key Testing Features**
- **🎦 Automatic Mocking**: All external dependencies mocked via `conftest.py`
- **📊 Coverage Reports**: HTML and terminal coverage reports
- **⚡ Fast Execution**: Tests run in ~2 minutes with full coverage
- **🔄 Parametrized Tests**: Multiple scenarios tested efficiently

### **Sample API Test**
```python
def test_calculate_price_with_markup(client, mock_rust_module):
    """Test price calculation with 15% markup"""
    request_data = {
        "product_id": "UHJvZHVjdDox",
        "channel_id": "Q2hhbm5lbDoy",
        "base_price": 100.00
    }
    
    response = client.post("/api/prices/calculate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["final_price"] == "115.00"
    assert data["markup_percent"] == "15"
```

### **Run API Tests**
```bash
# All API tests with coverage
./TEST api

# Specific test file
pytest tests/api/test_prices.py -v

# Run with coverage report
pytest tests/api/ --cov=app --cov-report=html

# Run only integration tests
pytest tests/api/test_integration.py -m integration
```

---

## 🌐 Frontend Testing Details

### **Test Structure**
```
frontend/tests/
├── homepage.spec.js           # Homepage functionality
├── channel-management.spec.js  # Channel management workflows
└── accessibility.spec.js       # Accessibility compliance
```

### **Browser Coverage**
- 🖥️ **Desktop**: Chrome, Firefox, Safari
- 📱 **Mobile**: iPhone 12, Pixel 5
- ♿ **Accessibility**: Keyboard navigation, screen readers

### **Sample Frontend Test**
```javascript
test('can update markup for a channel', async ({ page }) => {
  await page.goto('/');
  
  // Find channel and update markup
  const firstChannel = page.locator('.channel-card').first();
  const markupInput = firstChannel.locator('.markup-input').first();
  
  await markupInput.fill('25');
  await firstChannel.locator('.update-btn').first().click();
  
  // Verify success message
  await expect(page.locator('text=Markup updated successfully')).toBeVisible();
});
```

### **Run Frontend Tests**
```bash
# All frontend tests
./TEST frontend

# Run in headed mode (see browser)
cd frontend && npx playwright test --headed

# Run specific test file
cd frontend && npx playwright test homepage.spec.js

# Run on specific browser
cd frontend && npx playwright test --project=chromium

# Debug mode with UI
cd frontend && npx playwright test --ui
```

---

## 🐳 Docker Testing

### **Containerized Test Environment**
```bash
# Full Docker test suite
./TEST_DOCKER all

# API tests in Docker
./TEST_DOCKER api

# Frontend tests in Docker
./TEST_DOCKER frontend

# Integration tests in Docker
./TEST_DOCKER integration
```

### **Docker Test Services**
```yaml
services:
  redis-test:     # Test Redis instance
  api-test:       # FastAPI with test config
  frontend-test:  # React app in test mode
  test-runner:    # Pytest execution
  playwright-runner: # Browser test execution
```

---

## 📊 Test Reports

### **Coverage Reports**
- **HTML Report**: `htmlcov/index.html` - Interactive coverage report
- **Terminal Report**: Real-time coverage during test execution
- **CI Integration**: Automated coverage uploads to Codecov

### **Playwright Reports**
- **HTML Report**: `frontend/playwright-report/index.html`
- **Trace Viewer**: Step-by-step test execution replay
- **Screenshots**: Automatic screenshots on test failures

### **View Reports**
```bash
# Open API coverage report
open htmlcov/index.html

# Open Playwright report
open frontend/playwright-report/index.html

# View test traces
cd frontend && npx playwright show-trace trace.zip
```

---

## ⚙️ CI/CD Integration

### **GitHub Actions**
- **🎨 Multi-job Pipeline**: API tests, Frontend tests, Integration tests
- **📊 Coverage Upload**: Automatic Codecov integration
- **🗺️ Matrix Testing**: Multiple Python/Node.js versions
- **📁 Artifact Upload**: Test reports and failure screenshots

### **Workflow Triggers**
- Push to `main`, `develop`, `sketch-wip` branches
- Pull requests to `main` and `develop`
- Manual workflow dispatch

---

## 📈 Test Metrics

### **Performance Benchmarks**
- **Quick Tests**: < 30 seconds (deployment checks)
- **API Tests**: < 2 minutes (80% coverage, 50+ tests)
- **Frontend Tests**: < 5 minutes (3 browsers, 20+ scenarios)
- **Full Suite**: < 7 minutes (complete test coverage)

### **Coverage Targets**
- **API Coverage**: 80% minimum (current: ~85%)
- **Critical Path Coverage**: 100% (auth, pricing, webhooks)
- **Error Handling**: 100% (all error scenarios tested)

---

## 🚪 Debugging Tests

### **API Test Debugging**
```bash
# Run with verbose output
pytest tests/api/test_prices.py -v -s

# Debug specific test
pytest tests/api/test_prices.py::test_calculate_price_success -v -s --pdb

# Run with coverage debug
pytest --cov=app --cov-report=term-missing --cov-debug
```

### **Frontend Test Debugging**
```bash
# Run in headed mode
cd frontend && npx playwright test --headed

# Debug with UI
cd frontend && npx playwright test --ui

# Run with video recording
cd frontend && npx playwright test --video=on

# Debug specific test
cd frontend && npx playwright test homepage.spec.js --debug
```

### **Test Environment Issues**
```bash
# Check test dependencies
pip list | grep -E "pytest|playwright"

# Verify browser installation
npx playwright install --with-deps

# Check Redis connection
redis-cli ping

# Validate test data
python -c "from tests.fixtures.sample_data import SAMPLE_CHANNELS; print(len(SAMPLE_CHANNELS))"
```

---

## 📄 Best Practices

### **API Testing**
- ✅ **Mock All External Services** - No real Saleor/Redis calls in tests
- ✅ **Test Both Success and Error Cases** - Comprehensive scenario coverage
- ✅ **Use Fixtures for Test Data** - Consistent and reusable test scenarios
- ✅ **Parametrize Tests** - Test multiple scenarios efficiently
- ✅ **Async Test Support** - Proper handling of async functions

### **Frontend Testing**
- ✅ **Test User Workflows** - Complete user journeys, not just UI elements
- ✅ **Mock API Responses** - Control test environment completely
- ✅ **Test Accessibility** - Ensure app works with assistive technologies
- ✅ **Mobile Testing** - Validate responsive design behavior
- ✅ **Error State Testing** - Test graceful degradation

### **General Testing**
- ✅ **Fast Feedback** - Tests should run quickly and provide clear output
- ✅ **Reliable Tests** - No flaky tests, deterministic results
- ✅ **Clear Test Names** - Test names should explain what is being tested
- ✅ **Isolated Tests** - Tests should not depend on each other
- ✅ **Maintainable Tests** - Tests should be easy to update when code changes

---

**🎆 Happy Testing!** Your comprehensive test suite ensures reliable, high-quality code!