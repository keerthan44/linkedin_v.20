class LinkedInSelectors:
    """Base selectors for LinkedIn authentication and session management."""
    
    # Login page selectors
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "button[type='submit']"
    
    # Session validation selectors
    LOGGED_IN_INDICATOR = ".global-nav"  # LinkedIn's navigation bar, only visible when logged in

class PeopleSelectors:
    """CSS selectors for LinkedIn profile pages."""
    
    # Profile intro panel (name and location)
    NAME_LOCATION_PANEL = "//*[@class='mt2 relative']"
    NAME = "h1"  # Name is in h1 tag within intro panel
    LOCATION = "//*[@class='text-body-small inline t-black--light break-words']"  # found in intro panel
    TITLE = "[data-generated-suggestion-target]"
    
    # About section
    ABOUT_SECTION = "//*[@id='about'][1]/.."  # Selector for the About section

    # Experience section
    EXPERIENCE_SECTION = ".pvs-list__container"
    EXPERIENCE_LIST = "ul"
    EXPERIENCE_ITEM = "> .pvs-list__paged-list-item"
    EXPERIENCE_SPAN = 'span[class="visually-hidden"]'
    
    # Education section
    EDUCATION_SECTION = ".pvs-list__container"
    EDUCATION_LIST = "ul"
    EDUCATION_ITEM = "> .pvs-list__paged-list-item"
    EDUCATION_CONTAINER = "div[data-view-name='profile-component-entity']"
    EDUCATION_DETAILS = "> *"
    EDUCATION_SUMMARY = "span"

    
class SearchSelectors:
    """Selectors for LinkedIn search and profile link extraction."""
    
    # Search results
    SEARCH_RESULTS = "div.search-marvel-srp"
    PROFILE_LINKS = "div.search-marvel-srp > div:nth-of-type(1) a[data-test-app-aware-link], " + \
                   "div.search-marvel-srp > div:nth-of-type(2) a[data-test-app-aware-link]"
    INSIGHTS_LINKS = "div.entity-result__insights.t-12 a"
    
    # Pagination
    NEXT_BUTTON = "button[aria-label='Next']"
    RESULTS_COUNT = ".search-results__total"
    
    # Connections page
    CONNECTIONS_CONTAINER = ".mn-connections"
    CONNECTION_CARD = ".mn-connection-card"
    CONNECTION_NAME = ".mn-connection-card__name"
    CONNECTION_OCCUPATION = ".mn-connection-card__occupation"
    CONNECTION_LINK = ".mn-connection-card__link"
    