import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from accounts.models import *
from services.models import *
from datetime import date, timedelta

@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    try:
        yield driver
    finally:
        driver.quit()

@pytest.fixture
def test_user(django_user_model):
    user = django_user_model.objects.create_user(
        username="seltestuser@example.com",
        password="T3stp@ssword4Sel",
        email="seltestuser@example.com",
        first_name="Sel",
        last_name="Tester",
    )
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.skills = "Technology"
    profile.interests = "Test interests for selenium"
    profile.bio = "Test bio for selenium."
    profile.save()
    return user

@pytest.fixture
def logged_in_browser(browser, live_server, test_user):
    browser.get(live_server.url + '/user_login/')
    browser.find_element(By.NAME, "email").send_keys("seltestuser@example.com")
    browser.find_element(By.NAME, "password").send_keys("T3stp@ssword4Sel")
    browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    WebDriverWait(browser, 5).until(EC.none_of(EC.url_contains('/user_login/')))

    return browser

@pytest.fixture
def test_offer_listing(test_user):
    return Listing.objects.create(
        author = test_user,
        title = "Selenium Test Offer Listing",
        description = "Offer Test Description",
        service_type = "offer",
        category = "Tutoring",
        date = date.today() + timedelta(days=5),
    )

@pytest.fixture
def test_request_listing(test_user):
    return Listing.objects.create(
        author=test_user,
        title="Selenium Test Request Listing",
        description="Request Test Description",
        service_type="request",
        category="General Labor",
        date=date.today() + timedelta(days=3),
    )