import pytest
from selenium import webdriver


@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    try:
        yield driver
    finally:
        driver.quit()