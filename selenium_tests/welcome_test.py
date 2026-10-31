from selenium.webdriver.common.by import By


class TestWelcome:
    """
    Tests for the Comhluadar welcome page. Validates Welcome page loads and link navigation to login/create account pages
    """

    def test_welcome_page_loads(self, browser, live_server) -> None:
        """
        Welcome page and elements load correctly.
        """
        browser.get(live_server.url)

        assert 'Comhluadar | Welcome!' in browser.title
        assert browser.find_element(By.TAG_NAME, 'h1').text == 'Welcome to Comhluadar!'
        assert browser.find_element(By.LINK_TEXT, 'Log in').is_displayed()
        assert browser.find_element(By.LINK_TEXT, 'Create Account').is_displayed()

    def test_welcome_page_log_in_button(self, browser, live_server) -> None:
        """
        Welcome page 'Log In' button navigates to user log in page.
        """
        browser.get(live_server.url)
        browser.find_element(By.LINK_TEXT, 'Log in').click()

        assert browser.current_url.endswith('/user_login/')
        assert 'Comhluadar | Log In' in browser.title

    def test_welcome_page_create_account_button(self, browser, live_server) -> None:
        """
        Welcome page 'Create Account' button navigates to create account page.
        """
        browser.get(live_server.url)
        browser.find_element(By.LINK_TEXT, 'Create Account').click()

        assert browser.current_url.endswith('/create_account/')
        assert 'Comhluadar | Create Account' in browser.title