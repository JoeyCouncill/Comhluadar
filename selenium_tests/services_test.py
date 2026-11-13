from selenium.webdriver.common.by import By
from django.urls import reverse
from django.utils import timezone
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, timedelta
from selenium.webdriver.common.action_chains import ActionChains

from urllib.parse import quote

from conftest import listing
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
        assert logged_in_browser.find_elements(By.LINK_TEXT, "Previous") == []

        next_link = logged_in_browser.find_element(By.LINK_TEXT, "Next")
        ActionChains(logged_in_browser).move_to_element(next_link).click().perform()
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

    @pytest.mark.parametrize("service_type, category", [("offer", "Tutoring"), ("request", "General Labor"),])
    def test_create_listing(self, logged_in_browser, live_server, test_user, service_type, category):
        """
        Submitting the form saves the listing with entered values and logged-in user as 'author'.
        """
        service_date = timezone.localdate() + timedelta(days=5)
        logged_in_browser.get(live_server.url + '/services/new_listing')

        Select(logged_in_browser.find_element(By.ID, 'service_type')).select_by_value(service_type)
        logged_in_browser.find_element(By.ID, 'title').send_keys('Selenium Created Listing')
        Select(logged_in_browser.find_element(By.ID, 'category')).select_by_value(category)
        logged_in_browser.find_element(By.ID, "date").send_keys(service_date.strftime("%m%d%Y"))
        logged_in_browser.find_element(By.CSS_SELECTOR, 'form button.btn-success').click()

        alert = WebDriverWait(logged_in_browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "alert")))

        assert 'Your listing has been saved!' in alert.text
        assert 'Your listing has been saved!' in logged_in_browser.find_element(By.CLASS_NAME, 'alert').text

        listing = Listing.objects.get(title='Selenium Created Listing')
        assert listing.author == test_user
        assert listing.service_type == service_type
        assert listing.category == category
        assert listing.date == service_date

    def test_created_listing_shows_on_browse_page(self, logged_in_browser, live_server) -> None:
        """
        A listing created through the form shows up on the 'browse listings' page.
        """
        logged_in_browser.get(live_server.url + '/services/new_listing')

        Select(logged_in_browser.find_element(By.ID, 'service_type')).select_by_value('offer')
        logged_in_browser.find_element(By.ID, 'title').send_keys('Selenium Created Listing')
        Select(logged_in_browser.find_element(By.ID, 'category')).select_by_value('Tutoring')
        logged_in_browser.find_element(By.ID, 'date').send_keys((timezone.localdate() + timedelta(days=5)).strftime("%m%d%Y"))
        logged_in_browser.find_element(By.CSS_SELECTOR, 'form button.btn-success').click()

        alert = WebDriverWait(logged_in_browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "alert")))

        assert "Your listing has been saved!" in logged_in_browser.find_element(By.CLASS_NAME, "alert").text

        logged_in_browser.get(live_server.url + '/all_listings_view/')
        assert "Selenium Created Listing" in logged_in_browser.page_source

    def test_create_listing_empty_form_blocked_by_browser(self, logged_in_browser, live_server) -> None:
        """
        Attempting to save an empty form is blocked and doesn't save anything.
        """
        logged_in_browser.get(live_server.url + '/services/new_listing')
        logged_in_browser.find_element(By.CSS_SELECTOR, "form button.btn-success").click()

        assert '/services/new_listing' in logged_in_browser.current_url
        assert "Your listing has been saved!" not in logged_in_browser.page_source
        assert Listing.objects.count() == 0

class TestListingdetail:
    """
    Tests for the listing detail page.
    """
    def test_listing_detail_access_attempt_not_logged_in(self, browser, live_server, test_offer_listing) -> None:
        """
        Accessing a listing detail page while not logged in redirects to the login page.
        """
        browser.get(live_server.url + reverse('listing_detail', args=[test_offer_listing.pk]))
        assert '/user_login/' in browser.current_url

    def test_listing_details_load(self, logged_in_browser, live_server, test_offer_listing) -> None:
        """
        Detail page displays the listing's title, type, category, description, service date, and author.
        """
        logged_in_browser.get(live_server.url + reverse('listing_detail', args=[test_offer_listing.pk]))
        d = test_offer_listing.date
        assert f"{d:%B} {d.day}, {d.year}" in logged_in_browser.page_source
        assert logged_in_browser.find_element(By.TAG_NAME, "h1").text == "Selenium Test Offer Listing"
        assert "Offering a service" in logged_in_browser.page_source
        assert "Tutoring" in logged_in_browser.page_source
        assert "Offer Test Description" in logged_in_browser.page_source
        assert "seltestuser" in logged_in_browser.page_source

    def test_listing_detail_button_text_offer(self, logged_in_browser, live_server, test_offer_listing) -> None:
        """
        Detail page detects that listing is an offer and Accept button text updates correctly.
        """
        logged_in_browser.get(live_server.url + reverse('listing_detail', args=[test_offer_listing.pk]))
        assert logged_in_browser.find_element(By.CSS_SELECTOR, "button.btn-primary").text == "Accept this offer"

    def test_listing_detail_button_text_request(self, logged_in_browser, live_server, test_request_listing) -> None:
        """
        Detail page detects that listing is a request and Accept button text updates correctly.
        """
        logged_in_browser.get(live_server.url + reverse('listing_detail', args=[test_request_listing.pk]))
        assert logged_in_browser.find_element(By.CSS_SELECTOR, "button.btn-primary").text == "Accept this request"

    def test_listing_detail_back_button(self, logged_in_browser, live_server, test_offer_listing, test_user) -> None:
        """
        Back button returns to the page the user came from.
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

        logged_in_browser.get(live_server.url + '/all_listings_view/?page=2')
        logged_in_browser.find_element(By.LINK_TEXT, "View").click()
        logged_in_browser.find_element(By.LINK_TEXT, "Back").click()

        WebDriverWait(logged_in_browser, 5).until(EC.url_contains('page=2'))
        assert "Page 2 of 2" in logged_in_browser.page_source

    def test_detail_nonexistent_listing(self, logged_in_browser, live_server) -> None:
        """
        Attempting to navigate directly to a listing detail page that doesn't exist gives a 404 page.
        """
        logged_in_browser.get(live_server.url + reverse('listing_detail', args=[99999]))
        assert "Not Found" in logged_in_browser.page_source