class TestBrowsePosts:
    """
    Tests for Browse Posts page.
    """
    def test_browse_posts_access_attempt_not_logged_in(self, browser, live_server) -> None:
        """
        Attempting to access the 'browse posts' page directly while not logged in redirects to log in page.
        """
        browser.get(live_server.url + '/all_posts_view/')

        assert '/user_login/' in browser.current_url
        

class TestNewPost:
    """
    Tests for New Post page
    """

    def test_new_post_access_attempt_not_logged_in(self, browser, live_server) -> None:
        """
        Attempting to access the 'new post' page directly while not logged in redirects to log in page.
        """
        browser.get(live_server.url + '/services/new_post')

        assert '/user_login/' in browser.current_url
        