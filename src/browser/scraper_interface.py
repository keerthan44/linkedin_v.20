from abc import ABC, abstractmethod
from typing import List, Optional, Any
from .exceptions import BrowserError

class ScraperInterface(ABC):
    """
    Abstract interface for web scraping operations.
    Provides a common interface regardless of the underlying browser automation tool.
    """

    @abstractmethod
    async def launch_browser(self, **kwargs) -> None:
        """
        Launch and initialize the browser.
        
        Args:
            **kwargs: Browser configuration options
        """
        pass

    @abstractmethod
    async def close_browser(self) -> None:
        """Close the browser and cleanup resources."""
        pass

    @abstractmethod
    async def new_page(self, **kwargs) -> Any:
        """
        Create a new browser page/tab.
        
        Args:
            **kwargs: Page-specific configuration options
        
        Returns:
            Any: The page object
        """
        pass

    @abstractmethod
    async def navigate_to(self, url: str, timeout: Optional[int] = None) -> None:
        """
        Navigate to the specified URL.
        
        Args:
            url: The URL to navigate to
            timeout: Maximum time to wait for navigation in milliseconds
        
        Raises:
            BrowserError: If navigation fails or times out
        """
        pass

    @abstractmethod
    async def get_element_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """
        Get text content of an element.
        
        Args:
            selector: CSS or XPath selector
            timeout: Maximum time to wait for element in milliseconds
        
        Returns:
            str: Text content of the element
        
        Raises:
            BrowserError: If element not found or operation fails
        """
        pass

    @abstractmethod
    async def get_elements_text(self, selector: str, timeout: Optional[int] = None) -> List[str]:
        """
        Get text content of multiple elements.
        
        Args:
            selector: CSS or XPath selector
            timeout: Maximum time to wait for elements in milliseconds
        
        Returns:
            List[str]: List of text content from matching elements
        """
        pass

    @abstractmethod
    async def click_element(self, selector: str, timeout: Optional[int] = None) -> None:
        """
        Click on an element.
        
        Args:
            selector: CSS or XPath selector
            timeout: Maximum time to wait for element in milliseconds
        
        Raises:
            BrowserError: If element not found or click fails
        """
        pass

    @abstractmethod
    async def fill_input(self, selector: str, value: str, timeout: Optional[int] = None) -> None:
        """
        Fill an input field with text.
        
        Args:
            selector: CSS or XPath selector
            value: Text to enter into the field
            timeout: Maximum time to wait for element in milliseconds
        
        Raises:
            BrowserError: If element not found or operation fails
        """
        pass

    @abstractmethod
    async def evaluate_script(self, script: str, *args) -> Any:
        """
        Execute JavaScript in the browser context.
        
        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to the script
        
        Returns:
            Any: Result of the script execution
        """
        pass

    @abstractmethod
    async def get_element_attribute(self, selector: str, attribute: str, timeout: Optional[int] = None) -> Optional[str]:
        """
        Get the value of an element's attribute.
        
        Args:
            selector: CSS or XPath selector
            attribute: Name of the attribute
            timeout: Maximum time to wait for element in milliseconds
        
        Returns:
            Optional[str]: Attribute value or None if not found
        """
        pass

    @abstractmethod
    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None, visible: bool = True) -> None:
        """
        Wait for an element to appear in the DOM.
        
        Args:
            selector: CSS or XPath selector
            timeout: Maximum time to wait in milliseconds
            visible: Whether to wait for element to be visible
        
        Raises:
            BrowserError: If element not found within timeout
        """
        pass

    @abstractmethod
    async def wait_for_navigation(self, timeout: Optional[int] = None) -> None:
        """
        Wait for page navigation to complete.
        
        Args:
            timeout: Maximum time to wait in milliseconds
        
        Raises:
            BrowserError: If navigation times out
        """
        pass

    @abstractmethod
    async def is_element_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Check if an element is visible on the page.
        
        Args:
            selector: CSS or XPath selector
            timeout: Maximum time to wait for element in milliseconds
        
        Returns:
            bool: True if element is visible, False otherwise
        """
        pass

    @abstractmethod
    async def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the page."""
        pass

    @abstractmethod
    async def scroll_into_view(self, selector: str, timeout: Optional[int] = None) -> None:
        """
        Scroll an element into view.
        
        Args:
            selector: CSS or XPath selector
            timeout: Maximum time to wait for element in milliseconds
        
        Raises:
            BrowserError: If element not found
        """
        pass

    @abstractmethod
    async def scroll_to_height(self, height: int) -> None:
        """
        Scroll to a specific height on the page.
        
        Args:
            height: Vertical scroll position in pixels
        """
        pass

    @abstractmethod
    async def get_current_url(self) -> str:
        """
        Get the current page URL.
        
        Returns:
            str: The current page URL
            
        Raises:
            BrowserError: If page not initialized or operation fails
        """
        pass

    @abstractmethod
    async def get_element_html(self, selector: str) -> str:
        """
        Get the HTML content of an element.
        
        Args:
            selector: CSS or XPath selector for the element
            
        Returns:
            str: HTML content of the element
            
        Raises:
            BrowserError: If element not found or operation fails
        """
        pass

    @abstractmethod
    async def scroll_to_position(self, position: int) -> None:
        """
        Scroll to a specific vertical position on the page.
        
        Args:
            position: Vertical scroll position in pixels
            
        Raises:
            BrowserError: If scrolling fails
        """
        pass

    @abstractmethod
    async def close_page(self) -> None:
        """
        Close the current page/tab.
        
        Raises:
            BrowserError: If page closing fails
        """
        pass

    @abstractmethod
    async def set_content(self, html: str) -> None:
        """
        Set the HTML content of the page.
        
        Args:
            html: Raw HTML content to set
            
        Raises:
            BrowserError: If setting content fails
        """
        pass