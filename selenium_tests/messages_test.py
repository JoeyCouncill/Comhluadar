from selenium.webdriver.common.by import By


class TestInbox:
    """
    Tests for User Inbox page.
    """
    def test_inbox_access_attempt_not_logged_in(self, browser, live_server) -> None:
        """
        Attempting to access the inbox page directly while not logged in redirects to log in page.
        """
        browser.get(live_server.url + '/inbox/')

        assert '/user_login/' in browser.current_url