import pytest
from pytest_django.live_server_helper import LiveServer
from selenium import webdriver
from selenium.webdriver.common.by import By

class TestWelcome:
    """
    Tests for the Comhluadar welcome page. Validates Welcome page loads and link navigation to login/create account pages
    """

    def test_welcome_page_loads(self, live_server: LiveServer) -> None:
        """
        Welcome page and elements load correctly.
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url)

            assert 'Comhluadar | Welcome!' in browser.title
            assert browser.find_element(By.TAG_NAME, 'h1').text == 'Welcome to Comhluadar!'
            assert browser.find_element(By.LINK_TEXT, 'Log in').is_displayed()
            assert browser.find_element(By.LINK_TEXT, 'Create Account').is_displayed()
        finally:
            browser.quit()

    def test_welcome_page_log_in_button(self, live_server: LiveServer) -> None:
        """
        Welcome page 'Log In' button navigates to user log in page.
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url)
            browser.find_element(By.LINK_TEXT, 'Log in').click()

            assert browser.current_url.endswith('/user_login/')
            assert 'Comhluadar | Log In' in browser.title
        finally:
            browser.quit()

    def test_welcome_page_create_account_button(self, live_server: LiveServer) -> None:
        """
        Welcome page 'Create Account' button navigates to create account page.
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url)
            browser.find_element(By.LINK_TEXT, 'Create Account').click()

            assert browser.current_url.endswith('/create_account/')
            assert 'Comhluadar | Create Account' in browser.title
        finally:
            browser.quit()

class TestLogin:
    """
    Tests for Comhluadar 'Log In' page. Validates page loads and various log in/navigation scenarios.
    """

    def test_login_page_loads(self, live_server: LiveServer) -> None:
        """
        Log In page loads correctly
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url + '/user_login/')

            assert 'Log In' in browser.title
            assert browser.find_element(By.TAG_NAME, 'h1').is_displayed()
            assert browser.find_element(By.TAG_NAME, 'h1').text == 'Log in to Comhluadar Account'
        finally:
            browser.quit()

    def test_login_fields_exist(self, live_server: LiveServer) -> None:
        """
        Username/Email and password fields and Log In button exist.
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url + '/user_login/')
            username = browser.find_element(By.NAME, 'username')
            password = browser.find_element(By.NAME, 'password')
            login_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

            assert username.is_displayed()
            assert password.is_displayed()
            assert login_button.is_displayed()
        finally:
            browser.quit()

    def test_login_to_create_account_link(self, live_server: LiveServer) -> None:
        """
        'Create Account' link from Log In page correctly navigates to 'create account' page.
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url + '/user_login/')
            browser.find_element(By.LINK_TEXT, 'Create Account').click()

            assert browser.current_url.endswith('/create_account/')
            assert 'Comhluadar | Create Account' in browser.title
            assert browser.find_element(By.NAME, 'email').is_displayed()
        finally:
            browser.quit()

    def test_login_forgot_password_link(self, live_server):
        pytest.skip('Test not written yet. Awaiting forgot password functionality.')

    def test_login_invalid_username(self, live_server: LiveServer) -> None:
        """
        Submitting an invalid username displays an error message and remains on the login page
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url + '/user_login/')
            assert not browser.find_elements(By.CSS_SELECTOR, '.alert')

            browser.find_element(By.NAME, 'username').send_keys('testuser@unomaha.edu')
            browser.find_element(By.NAME, 'password').send_keys('t3stp4ssw0rd')
            browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

            assert browser.current_url.endswith('/user_login/')
            assert browser.find_element(By.CSS_SELECTOR, '.alert').is_displayed()
        finally:
            browser.quit()

    def test_login_incorrect_password(self, live_server):
        pytest.skip('Test not written yet. Awaiting user model.')

    def test_login_empty_form(self, live_server: LiveServer) -> None:
        """
        A submitted empty form is rejected and remains on the login page
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url + '/user_login/')
            browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

            assert browser.current_url.endswith('/user_login/')
        finally:
            browser.quit()

    def test_login_valid(self, live_server):
        pytest.skip('Test not written yet. Awaiting user model.')

class TestCreateAccount:
    """
    Tests for Comhluadar 'Create Account' page. Validates page loads and various account creations scenarios.
    """

    def test_create_account_page_loads(self, live_server: LiveServer) -> None:
        """
        Create account page loads correctly
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url + '/create_account/')

            assert 'Create Account' in browser.title
            assert 'Create User Account' in browser.page_source
        finally:
            browser.quit()

    def test_create_account_fields_exist(self, live_server: LiveServer) -> None:
        """
        Create account fields exist upon page loading
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url + '/create_account/')
            name = browser.find_element(By.NAME, 'name')
            email = browser.find_element(By.NAME, 'email')
            password1 = browser.find_element(By.NAME, 'password1')
            password2 = browser.find_element(By.NAME, 'password2')
            create_button = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

            assert name.is_displayed()
            assert email.is_displayed()
            assert password1.is_displayed()
            assert password2.is_displayed()
            assert create_button.is_displayed()
        finally:
            browser.quit()

    def test_create_account_to_login_link(self, live_server: LiveServer) -> None:
        """
        Clicking Log In link navigates to the user login page
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url + '/create_account/')
            browser.find_element(By.LINK_TEXT, 'Log In').click()

            assert browser.current_url.endswith('/user_login/')
        finally:
            browser.quit()

    def test_create_account_valid(self, live_server: LiveServer) -> None:
        """
        Submitting valid new account details navigates directly to the 'account summary' page
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url + '/create_account/')
            browser.find_element(By.NAME, 'name').send_keys('TestUser1')
            browser.find_element(By.NAME, 'email').send_keys('test1@unomaha.edu')
            browser.find_element(By.NAME, 'password1').send_keys('Comhluadart3st1')
            browser.find_element(By.NAME, 'password2').send_keys('Comhluadart3st1')
            browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

            assert browser.current_url.endswith('/account_summary/')
        finally:
            browser.quit()

    def test_create_account_passwords_mismatch(self, live_server: LiveServer) -> None:
        """
        Attempting to create an account with mismatched passwords stays on create account page
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url + '/create_account/')
            assert not browser.find_element(By.ID, 'password-error').is_displayed()

            browser.find_element(By.NAME, 'name').send_keys('TestUser2')
            browser.find_element(By.NAME, 'email').send_keys('test2@unomaha.edu')
            browser.find_element(By.NAME, 'password1').send_keys('ComhluadarTest1')
            browser.find_element(By.NAME, 'password2').send_keys('ComhluadarTest2')
            browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

            assert browser.current_url.endswith('/create_account/')
            assert browser.find_element(By.ID, 'password-error').is_displayed()
        finally:
            browser.quit()

    def test_create_account_email_already_in_use(self, live_server):
        pytest.skip('Test not written yet. Awaiting user model.')

    def test_create_account_invalid_email_domain(self, live_server):
        pytest.skip('Test not written yet. Awaiting email domain validation.')

class TestAccountSummary:
    """
    Tests for Account Summary page. Validates that Summary loads and displays correctly.
    """

    def test_account_summary_access_attempt_not_logged_in(self, live_server: LiveServer) -> None:
        """
        Attempting to access the account summary page directly while not logged in redirects to log in page.
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url + '/account_summary/')

            assert '/user_login/' in browser.current_url
        finally:
            browser.quit()

class TestInbox:
    """
    Tests for User Inbox page.
    """

    def test_inbox_access_attempt_not_logged_in(self, live_server: LiveServer) -> None:
        """
        Attempting to access the inbox page directly while not logged in redirects to log in page.
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url + '/inbox/')

            assert '/user_login/' in browser.current_url
        finally:
            browser.quit()

class TestBrowsePosts:
    """
    Tests for Browse Posts page.
    """

    def test_browse_posts_access_attempt_not_logged_in(self, live_server: LiveServer) -> None:
        """
        Attempting to access the 'browse posts' page directly while not logged in redirects to log in page.
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url + '/all_posts_view/')

            assert '/user_login/' in browser.current_url
        finally:
            browser.quit()

class TestNewPost:
    """
    Tests for New Post page
    """

    def test_new_post_access_attempt_not_logged_in(self, live_server: LiveServer) -> None:
        """
        Attempting to access the 'new post' page directly while not logged in redirects to log in page.
        """
        browser = webdriver.Chrome()
        try:
            browser.get(live_server.url + '/service/new_post')

            assert '/user_login/' in browser.current_url
        finally:
            browser.quit()