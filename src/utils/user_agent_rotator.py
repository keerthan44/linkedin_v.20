from fake_useragent import UserAgent
import random
import logging
from typing import Optional
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class UserAgentRotator:
    """
    Manages user agent rotation for browser requests.
    Uses fake-useragent library to generate realistic user agents.
    """

    def __init__(self, use_cache: bool = True):
        try:
            self._ua = UserAgent(use_cache_server=use_cache)
            self._fallback_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            ]
            self._log_file = Path('logs/user_agents.json')
            self._log_file.parent.mkdir(exist_ok=True)
            self._used_agents = self._load_used_agents()
        except Exception as e:
            logger.warning(f"Failed to initialize UserAgent: {str(e)}. Using fallback agents.")
            self._ua = None

    def _load_used_agents(self) -> list:
        """Load history of used user agents."""
        try:
            if self._log_file.exists():
                with open(self._log_file) as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Failed to load user agent history: {e}")
            return []

    def _log_user_agent(self, user_agent: str):
        """Log used user agent with timestamp."""
        try:
            self._used_agents.append({
                'user_agent': user_agent,
                'timestamp': datetime.now().isoformat(),
            })
            
            # Keep last 1000 entries
            self._used_agents = self._used_agents[-1000:]
            
            with open(self._log_file, 'w') as f:
                json.dump(self._used_agents, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to log user agent: {e}")

    def get_random_user_agent(self) -> str:
        """Get a random user agent string."""
        try:
            if self._ua:
                user_agent = self._ua.random
                logger.info(f"""
User Agent Selected:
------------------
Agent: {user_agent}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Used: {len(self._used_agents)}
                """)
                self._log_user_agent(user_agent)
                return user_agent
        except Exception as e:
            logger.warning(f"Error getting random user agent: {str(e)}. Using fallback.")
        
        user_agent = random.choice(self._fallback_agents)
        logger.info(f"Using fallback user agent: {user_agent}")
        self._log_user_agent(user_agent)
        return user_agent

    def get_chrome_user_agent(self) -> str:
        """Get a Chrome user agent string."""
        try:
            if self._ua:
                return self._ua.chrome
        except Exception:
            return self._fallback_agents[0]

    def get_firefox_user_agent(self) -> str:
        """Get a Firefox user agent string."""
        try:
            if self._ua:
                return self._ua.firefox
        except Exception:
            return self._fallback_agents[2]

    def get_safari_user_agent(self) -> str:
        """Get a Safari user agent string."""
        try:
            if self._ua:
                return self._ua.safari
        except Exception:
            return self._fallback_agents[3] 