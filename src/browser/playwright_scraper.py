from typing import List, Optional, Any
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError, async_playwright, Browser, BrowserContext, Playwright
from .scraper_interface import ScraperInterface
from .exceptions import BrowserError, BrowserTimeoutError
from ..utils.simple_rate_limiter import SimpleRateLimiter
import asyncio
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PlaywrightScraper(ScraperInterface):
    """
    Playwright implementation of the ScraperInterface.
    Handles web scraping operations using Playwright.
    """

    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._default_timeout = 30000  # 30 seconds
        self._storage_state_path = Path("browser_state.json")  # Path to save browser state
        
        # Initialize rate limiter
        self._rate_limiter = SimpleRateLimiter(max_requests=200)

    async def launch_browser(self, headless: bool = True, user_agent: Optional[str] = None) -> None:
        """Launch browser instance."""
        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=headless)
            
            # Create a browser context with state restoration
            context_options = {}
            if self._storage_state_path.exists():
                context_options["storage_state"] = str(self._storage_state_path)
            if user_agent:
                context_options["user_agent"] = user_agent
            
            self._context = await self._browser.new_context(**context_options)
            
        except Exception as e:
            raise BrowserError(f"Failed to launch browser: {str(e)}")

    async def save_storage_state(self) -> None:
        """Save browser state for future sessions."""
        if self._context:
            try:
                # Ensure parent directory exists
                self._storage_state_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save the state
                await self._context.storage_state(path=str(self._storage_state_path))
                logger.info("Browser state saved successfully")
            except Exception as e:
                logger.error(f"Failed to save browser state: {str(e)}")

    async def close_browser(self) -> None:
        """Close the browser and cleanup resources."""
        try:
            # Save state before closing anything
            if self._context:
                await self.save_storage_state()
            
            # Close in reverse order of creation
            if self._page:
                await self._page.close()
                self._page = None
            
            if self._context:
                await self._context.close()
                self._context = None
            
            if self._browser:
                await self._browser.close()
                self._browser = None
            
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
                
        except Exception as e:
            logger.error(f"Error during browser cleanup: {str(e)}")

    async def new_page(self, **kwargs) -> Page:
        """Create a new browser page/tab."""
        try:
            if not self._context:
                raise BrowserError("Browser context not initialized")
            
            # Create new page
            self._page = await self._context.new_page()
            
            # Configure page timeout
            timeout = kwargs.get('timeout', self._default_timeout)
            self._page.set_default_timeout(timeout)
            
            return self._page
            
        except Exception as e:
            raise BrowserError(f"Failed to create new page: {str(e)}")

    async def navigate_to(self, url: str, timeout: Optional[int] = None) -> None:
        """Navigate to the specified URL with rate limiting."""
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            # Apply rate limiting before navigation
            await self._rate_limiter.acquire()
            
            await self._page.goto(
                url,
                timeout=timeout or self._default_timeout,
                wait_until='domcontentloaded'
            )
            
            await self._page.wait_for_selector(
                "main",
                timeout=timeout or self._default_timeout,
                state='visible'
            )
            
            await asyncio.sleep(1)
            
        except PlaywrightTimeoutError as e:
            raise BrowserTimeoutError(f"Navigation timeout: {str(e)}")
        except Exception as e:
            raise BrowserError(f"Navigation failed: {str(e)}")

    async def get_element_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """Get text content of an element."""
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            element = await self._page.wait_for_selector(
                selector,
                timeout=timeout or self._default_timeout
            )
            if not element:
                raise BrowserError(f"Element not found: {selector}")
            
            text = await element.text_content()  # Await the coroutine
            return text.strip() if text else ""
            
        except PlaywrightTimeoutError as e:
            raise BrowserTimeoutError(f"Timeout waiting for element: {str(e)}")
        except Exception as e:
            raise BrowserError(f"Failed to get element text: {str(e)}")

    async def get_elements_text(self, selector: str, timeout: Optional[int] = None) -> List[str]:
        """Get text content of multiple elements."""
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            elements = await self._page.query_selector_all(selector)
            texts = []
            for element in elements:
                text = await element.text_content()
                if text:
                    texts.append(text.strip())
            return texts
        except Exception as e:
            raise BrowserError(f"Failed to get elements text: {str(e)}")

    async def click_element(self, selector: str, timeout: Optional[int] = None) -> None:
        """Click on an element."""
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            await self._page.click(
                selector,
                timeout=timeout or self._default_timeout
            )
        except PlaywrightTimeoutError as e:
            raise BrowserTimeoutError(f"Timeout waiting for click: {str(e)}")
        except Exception as e:
            raise BrowserError(f"Failed to click element: {str(e)}")

    async def fill_input(self, selector: str, value: str, timeout: Optional[int] = None) -> None:
        """Fill an input field with text."""
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            await self._page.fill(
                selector,
                value,
                timeout=timeout or self._default_timeout
            )
        except PlaywrightTimeoutError as e:
            raise BrowserTimeoutError(f"Timeout waiting for input: {str(e)}")
        except Exception as e:
            raise BrowserError(f"Failed to fill input: {str(e)}")

    async def evaluate_script(self, script: str, *args) -> Any:
        """Execute JavaScript in the browser context."""
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            return await self._page.evaluate(script, *args)
        except Exception as e:
            raise BrowserError(f"Script evaluation failed: {str(e)}")

    async def get_element_attribute(self, selector: str, attribute: str, timeout: Optional[int] = None) -> Optional[str]:
        """Get the value of an element's attribute."""
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            element = await self._page.wait_for_selector(
                selector,
                timeout=timeout or self._default_timeout
            )
            if not element:
                return None
            return await element.get_attribute(attribute)
        except PlaywrightTimeoutError:
            return None
        except Exception as e:
            raise BrowserError(f"Failed to get attribute: {str(e)}")

    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None, visible: bool = True) -> None:
        """Wait for an element to appear in the DOM."""
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            await self._page.wait_for_selector(
                selector,
                timeout=timeout or self._default_timeout,
                state='visible' if visible else 'attached'
            )
        except PlaywrightTimeoutError as e:
            raise BrowserTimeoutError(f"Timeout waiting for selector: {str(e)}")
        except Exception as e:
            raise BrowserError(f"Failed to wait for selector: {str(e)}")

    async def wait_for_navigation(self, timeout: Optional[int] = None) -> None:
        """Wait for page navigation to complete."""
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            # Wait for domcontentloaded instead of networkidle
            await self._page.wait_for_load_state(
                'domcontentloaded',  # Changed from 'networkidle'
                timeout=timeout or self._default_timeout
            )
            
            # Wait for main content to be visible
            await self._page.wait_for_selector(
                "main",
                timeout=timeout or self._default_timeout,
                state='visible'
            )
            
            # Short pause to allow critical content to load
            await asyncio.sleep(1)
            
        except PlaywrightTimeoutError as e:
            raise BrowserTimeoutError(f"Navigation timeout: {str(e)}")
        except Exception as e:
            raise BrowserError(f"Navigation failed: {str(e)}")

    async def is_element_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Check if an element is visible on the page."""
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            element = await self._page.wait_for_selector(
                selector,
                timeout=timeout or 1000,  # Short timeout for visibility check
                state='visible'
            )
            return bool(element)
        except PlaywrightTimeoutError:
            return False
        except Exception as e:
            raise BrowserError(f"Visibility check failed: {str(e)}")

    async def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the page."""
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            await self._page.evaluate("""
                window.scrollTo({
                    top: document.body.scrollHeight,
                    behavior: 'smooth'
                });
            """)
        except Exception as e:
            raise BrowserError(f"Scroll to bottom failed: {str(e)}")

    async def scroll_into_view(self, selector: str, timeout: Optional[int] = None) -> None:
        """Scroll an element into view."""
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            element = await self._page.wait_for_selector(
                selector,
                timeout=timeout or self._default_timeout
            )
            if not element:
                raise BrowserError(f"Element not found: {selector}")
            await element.scroll_into_view_if_needed()
        except PlaywrightTimeoutError as e:
            raise BrowserTimeoutError(f"Timeout waiting for element: {str(e)}")
        except Exception as e:
            raise BrowserError(f"Scroll into view failed: {str(e)}")

    async def scroll_to_height(self, height: int) -> None:
        """Scroll to a specific height on the page."""
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            await self._page.evaluate(f"""
                window.scrollTo({{
                    top: {height},
                    behavior: 'smooth'
                }});
            """)
        except Exception as e:
            raise BrowserError(f"Scroll to height failed: {str(e)}")

    async def get_current_url(self) -> str:
        """
        Get the current page URL.
        
        Returns:
            str: The current page URL
            
        Raises:
            BrowserError: If page not initialized or operation fails
        """
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            return self._page.url
        except Exception as e:
            raise BrowserError(f"Failed to get current URL: {str(e)}")

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
        if not self._page:
            raise BrowserError("Page not initialized")
            
        try:
            # Handle both CSS and XPath selectors
            if selector.startswith('/'):
                # XPath selector
                element = await self._page.wait_for_selector(f"xpath={selector}", timeout=self._default_timeout)
            else:
                # CSS selector
                element = await self._page.wait_for_selector(selector, timeout=self._default_timeout)
                
            if not element:
                raise BrowserError(f"Element not found: {selector}")
                
            # Get the HTML content
            html = await element.inner_html()
            return html
            
        except PlaywrightTimeoutError as e:
            raise BrowserTimeoutError(f"Timeout waiting for element: {str(e)}")
        except Exception as e:
            raise BrowserError(f"Failed to get element HTML: {str(e)}")

    async def scroll_to_position(self, position: int) -> None:
        """
        Scroll to a specific vertical position on the page.
        
        Args:
            position: Vertical scroll position in pixels
            
        Raises:
            BrowserError: If scrolling fails
        """
        if not self._page:
            raise BrowserError("Page not initialized")
        
        try:
            await self._page.evaluate(f"""
                window.scrollTo({{
                    top: {position},
                    behavior: 'smooth'
                }});
            """)
            await asyncio.sleep(0.5)  # Short pause for smooth scrolling
        except Exception as e:
            raise BrowserError(f"Failed to scroll to position: {str(e)}")

    async def close_page(self) -> None:
        """
        Close the current page/tab.
        
        Raises:
            BrowserError: If page closing fails
        """
        try:
            if self._page:
                await self._page.close()
                self._page = None
        except Exception as e:
            raise BrowserError(f"Failed to close page: {str(e)}")

    async def set_content(self, html: str) -> None:
        """
        Set the HTML content of the page.
        
        Args:
            html: Raw HTML content to set
            
        Raises:
            BrowserError: If setting content fails
        """
        if not self._page:
            raise BrowserError("Page not initialized")
            
        try:
            await self._page.set_content(html)
            await asyncio.sleep(0.5)  # Short pause to let content render
        except Exception as e:
            raise BrowserError(f"Failed to set content: {str(e)}") 