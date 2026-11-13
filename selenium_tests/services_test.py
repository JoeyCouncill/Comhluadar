from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
from services.models import *
import pytest


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

    def test_browse_listings_loads_logged_in(self, logged_in_browser, live_server):
        """
        Attempting to access the 'browse listings' page directly while logged in loads the page.
        """
        logged_in_browser.get(live_server.url + '/all_listings_view/')
        assert '/user_login/' not in logged_in_browser.current_url
        assert logged_in_browser.find_element(By.TAG_NAME, "h1").text == "View All Listings"

    def test_empty_listings_page(self, logged_in_browser, live_server) -> None:
        """
        The 'browse listings' page displays a 'no listings found' message if no listings are available.
        """
        logged_in_browser.get(live_server.url + '/all_listings_view/')
        assert 'No matching listings found.' in logged_in_browser.page_source

    def test_listing_displayed(self, logged_in_browser, live_server, test_offer_listing) -> None:
        """
        Page displays posts if they exist in the database.
        """
        logged_in_browser.get(live_server.url + '/all_listings_view/')
        assert 'Selenium Test Offer Listing' in logged_in_browser.page_source
        assert 'Offering a service' in logged_in_browser.page_source
        assert 'seltestuser' in logged_in_browser.page_source

    @pytest.mark.parametrize("type_value, shown, hidden", [
        ("offer", ["Selenium Test Offer Listing"], ["Selenium Test Request Listing"]),
        ("request", ["Selenium Test Request Listing"], ["Selenium Test Offer Listing"]),
        ("", ["Selenium Test Offer Listing", "Selenium Test Request Listing"], [])
    ])
    def test_type_filter(self, logged_in_browser, live_server, test_offer_listing, test_request_listing, type_value, shown, hidden) -> None:
        """
        Page displays the correct post type (All/Offer/Request) when filtered by listing type.
        """
        logged_in_browser.get(live_server.url + f'/all_listings_view/?type={type_value}')
        for i in shown:
            assert i in logged_in_browser.page_source
        for j in hidden:
            assert j not in logged_in_browser.page_source

    @pytest.mark.parametrize("cat_value, shown, hidden", [
        ("Tutoring", ["Selenium Test Offer Listing"], ["Selenium Test Request Listing"]),
        ("General Labor", ["Selenium Test Request Listing"], ["Selenium Test Offer Listing"]),
        ("", ["Selenium Test Offer Listing", "Selenium Test Request Listing"], [])
    ])
    def test_category_filter(self, logged_in_browser, live_server, test_offer_listing, test_request_listing, cat_value, shown, hidden) -> None:
        """
        Page displays relevant posts when filtered by category.
        """
        logged_in_browser.get(live_server.url + f'/all_listings_view/?category={quote(cat_value)}')
        for i in shown:
            assert i in logged_in_browser.page_source
        for j in hidden:
            assert j not in logged_in_browser.page_source

    def test_search_no_match(self, logged_in_browser, live_server, test_offer_listing) -> None:
        """
        Page displays a 'no matching listings' message if no posts match a submitted search.
        """
        logged_in_browser.get(live_server.url + f'/all_listings_view/?search=aintthatjusttheway')
        assert "No matching listings found." in logged_in_browser.page_source

    @pytest.mark.parametrize("search_term, shown, hidden", [
        ("Selenium", ["Selenium Test Offer Listing", "Selenium Test Request Listing"], []),
        ("Offer Test Description", ["Selenium Test Offer Listing"], ["Selenium Test Request Listing"]),
        ("Tutoring", ["Selenium Test Offer Listing"], ["Selenium Test Request Listing"]),
        ("tutoring", ["Selenium Test Offer Listing"], ["Selenium Test Request Listing"]),
    ])
    def test_search(self, logged_in_browser, live_server, test_offer_listing, test_request_listing, search_term, shown, hidden) -> None:
        """
        Page displays matching listings when a keyword search is performed. Tests for matches in listing title, description,
        and category as well as upper/lower case sensitivity.
        """
        logged_in_browser.get(live_server.url + f'/all_listings_view/?search={quote(search_term)}')
        for i in shown:
            assert i in logged_in_browser.page_source
        for j in hidden:
            assert j not in logged_in_browser.page_source

    @pytest.mark.parametrize("sort_value, expected_order", [
        ("posted_new", ["Selenium Test Request Listing", "Selenium Test Offer Listing"]),
        ("posted_old", ["Selenium Test Offer Listing", "Selenium Test Request Listing"]),
        ("service_soon", ["Selenium Test Request Listing", "Selenium Test Offer Listing"]),
        ("service_late", ["Selenium Test Offer Listing", "Selenium Test Request Listing"]),
    ])
    def test_sort_listings(self, logged_in_browser, live_server, test_offer_listing, test_request_listing, sort_value, expected_order) -> None:
        """
        'browse listings' page orders listings correctly for each sort option.
        """
        logged_in_browser.get(live_server.url + f'/all_listings_view/?sort={sort_value}')
        listing_titles = []
        for title in logged_in_browser.find_elements(By.CLASS_NAME, "card-title"):
            listing_titles.append(title.text)
        assert listing_titles == expected_order

    def test_view_button_opens_detail(self, logged_in_browser, live_server, test_offer_listing) -> None:
        """
        Clicking 'View' on a listing opens that listing's detail page.
        """
        logged_in_browser.get(live_server.url + '/all_listings_view/')
        logged_in_browser.find_element(By.LINK_TEXT, "View").click()

        assert str(test_offer_listing.pk) in logged_in_browser.current_url
        assert 'Selenium Test Offer Listing' in logged_in_browser.page_source
        assert 'Offer Test Description' in logged_in_browser.page_source

    def test_pagination(self, logged_in_browser, live_server, test_user) -> None:
        """
        Page shows 12 listings per page, and the Next/Previous links move between pages.
        """
        Listing.objects.bulk_create([
            Listing(
                author=test_user,
                title=f"Pagination Listing {i}",
                service_type="offer",
                category="Tutoring",
                date=date.today() + timedelta(days=1),
            )
            for i in range(13)
        ])

        logged_in_browser.get(live_server.url + '/all_listings_view/')
        assert len(logged_in_browser.find_elements(By.CLASS_NAME, "card")) == 12
        assert "Page 1 of 2" in logged_in_browser.page_source
        assert logged_in_browser.find_elements(By.LINK_TEXT, "Previous") == []  # disabled on page 1, not a link

        logged_in_browser.find_element(By.LINK_TEXT, "Next").click()
        assert "page=2" in logged_in_browser.current_url
        assert len(logged_in_browser.find_elements(By.CLASS_NAME, "card")) == 1
        assert "Page 2 of 2" in logged_in_browser.page_source

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
        