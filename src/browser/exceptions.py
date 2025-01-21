class BrowserError(Exception):
    """Base class for browser-related exceptions."""
    pass

class BrowserNotInitializedError(BrowserError):
    """Raised when trying to use browser before initialization."""
    pass

class BrowserConnectionError(BrowserError):
    """Raised when browser connection fails."""
    pass

class BrowserTimeoutError(BrowserError):
    """Raised when browser operation times out."""
    pass 