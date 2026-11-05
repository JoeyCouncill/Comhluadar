class TestBrowselistings:
    """
    Tests for Browse listings page.
    """
    def test_browse_listings_access_attempt_not_logged_in(self, browser, live_server) -> None:
        """
        Attempting to access the 'browse listings' page directly while not logged in redirects to log in page.
        """
        browser.get(live_server.url + '/all_listings_view/')

        assert '/user_login/' in browser.current_url
        

class TestNewlisting:
    """
    Tests for New listing page
    """

    def test_new_listing_access_attempt_not_logged_in(self, browser, live_server) -> None:
        """
        Attempting to access the 'new listing' page directly while not logged in redirects to log in page.
        """
        browser.get(live_server.url + '/services/new_listing')

        assert '/user_login/' in browser.current_url
        