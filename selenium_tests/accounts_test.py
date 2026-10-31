import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestLogin:
    """
    Tests for Comhluadar 'Log In' page. Validates page loads and various log in/navigation scenarios.
    """
    def test_login_page_loads(self, browser, live_server) -> None:
        """
        Log In page loads correctly
        """
        browser.get(live_server.url + '/user_login/')

        assert 'Log In' in browser.title
        assert browser.find_element(By.TAG_NAME, 'h1').is_displayed()
        assert browser.find_element(By.TAG_NAME, 'h1').text == 'Log in to Comhluadar Account'
        

    def test_login_fields_exist(self, browser, live_server) -> None:
        """
        Username/Email and password fields and Log In button exist.
        """
        browser.get(live_server.url + '/user_login/')
        username = browser.find_element(By.NAME, 'email')
        password = browser.find_element(By.NAME, 'password')
        login_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        assert username.is_displayed()
        assert password.is_displayed()
        assert login_button.is_displayed()
        

    def test_login_to_create_account_link(self, browser, live_server) -> None:
        """
        'Create Account' link from Log In page correctly navigates to 'create account' page.
        """
        browser.get(live_server.url + '/user_login/')
        browser.find_element(By.LINK_TEXT, 'Create Account').click()

        assert browser.current_url.endswith('/create_account/')
        assert 'Comhluadar | Create Account' in browser.title
        assert browser.find_element(By.NAME, 'email').is_displayed()
        

    def test_login_forgot_password_link(self, browser, live_server):
        pytest.skip('Test not written yet. Awaiting forgot password functionality.')

    def test_login_invalid_username(self, browser, live_server) -> None:
        """
        Submitting an invalid username displays an error message and remains on the login page
        """
        browser.get(live_server.url + '/user_login/')
        assert not browser.find_elements(By.CSS_SELECTOR, '.alert')

        browser.find_element(By.NAME, 'email').send_keys('testuser@unomaha.edu')
        browser.find_element(By.NAME, 'password').send_keys('t3stp4ssw0rd')
        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        assert browser.current_url.endswith('/user_login/')
        alert = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert"))
            )
        assert "Invalid email, username, or password." in alert.text
        

    def test_login_incorrect_password(self, browser, live_server):
        pytest.skip('Test not written yet. Awaiting user model.')

    def test_login_empty_form(self, browser, live_server) -> None:
        """
        A submitted empty form is rejected and remains on the login page
        """
        browser.get(live_server.url + '/user_login/')
        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        assert browser.current_url.endswith('/user_login/')
        

    def test_login_valid(self, browser, live_server):
        pytest.skip('Test not written yet. Awaiting user model.')


class TestCreateAccount:
    """
    Tests for Comhluadar 'Create Account' page. Validates page loads and various account creations scenarios.
    """
    def test_create_account_page_loads(self, browser, live_server) -> None:
        """
        Create account page loads correctly
        """
        browser.get(live_server.url + '/create_account/')

        assert 'Create Account' in browser.title
        assert 'Create User Account' in browser.page_source
        

    def test_create_account_fields_exist(self, browser, live_server) -> None:
        """
        Create account fields exist upon page loading
        """
        browser.get(live_server.url + '/create_account/')
        firstName = browser.find_element(By.NAME, 'firstName')
        lastName = browser.find_element(By.NAME, 'lastName')
        email = browser.find_element(By.NAME, 'email')
        password1 = browser.find_element(By.NAME, 'password1')
        password2 = browser.find_element(By.NAME, 'password2')
        create_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        assert firstName.is_displayed()
        assert lastName.is_displayed()
        assert email.is_displayed()
        assert password1.is_displayed()
        assert password2.is_displayed()
        assert create_button.is_displayed()
        

    def test_create_account_to_login_link(self, browser, live_server) -> None:
        """
        Clicking Log In link navigates to the user login page
        """
        browser.get(live_server.url + '/create_account/')
        browser.find_element(By.LINK_TEXT, 'Log In').click()

        assert browser.current_url.endswith('/user_login/')
        

    def test_create_account_valid(self, browser, live_server) -> None:
        """
        Submitting valid new account details navigates directly to the 'account summary' page
        """
        browser.get(live_server.url + '/create_account/')
        
        browser.find_element(By.NAME, 'firstName').send_keys('FirstNameTest1')
        browser.find_element(By.NAME, 'lastName').send_keys('LastNameTest1')
        browser.find_element(By.NAME, 'email').send_keys('test1@unomaha.edu')
        browser.find_element(By.NAME, 'password1').send_keys('Comhluadart3st1')
        browser.find_element(By.NAME, 'password2').send_keys('Comhluadart3st1')
        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        assert browser.current_url.endswith('/account_summary/')
        

    def test_create_account_passwords_mismatch(self, browser, live_server) -> None:
        """
        Attempting to create an account with mismatched passwords stays on create account page
        """
        browser.get(live_server.url + '/create_account/')
        assert not browser.find_element(By.ID, 'password-error').is_displayed()

        browser.find_element(By.NAME, 'firstName').send_keys('FirstNameTest2')
        browser.find_element(By.NAME, 'lastName').send_keys('LastNameTest2')
        browser.find_element(By.NAME, 'email').send_keys('test2@unomaha.edu')
        browser.find_element(By.NAME, 'password1').send_keys('ComhluadarTest1')
        browser.find_element(By.NAME, 'password2').send_keys('ComhluadarTest2')
        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        assert browser.current_url.endswith('/create_account/')
        assert browser.find_element(By.ID, 'password-error').is_displayed()
        

    def test_create_account_email_already_in_use(self, live_server):
        pytest.skip('Test not written yet. Awaiting user model.')

    def test_create_account_invalid_email_domain(self, live_server):
        pytest.skip('Test not written yet. Awaiting email domain validation.')

class TestAccountSummary:
    """
    Tests for Account Summary page. Validates that Summary loads and displays correctly.
    """

    def test_account_summary_access_attempt_not_logged_in(self, browser, live_server) -> None:
        """
        Attempting to access the account summary page directly while not logged in redirects to log in page.
        """
        browser.get(live_server.url + '/account_summary/')

        assert '/user_login/' in browser.current_url
        