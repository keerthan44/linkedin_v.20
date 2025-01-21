import asyncio
import random
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SimpleRateLimiter:
    """
    A burst-style rate limiter that sends requests in small clusters followed by longer breaks.
    Designed to look more natural by mimicking human browsing patterns.
    """
    
    def __init__(self, max_requests: int = 200):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed per 24-hour period
        """
        self._max_requests = max_requests
        self._requests = []
        self._state_file = Path('logs/rate_limiter_state.json')
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Burst configuration
        self._burst_size = random.randint(3, 5)  # Requests per burst
        self._current_burst = 0
        self._last_burst_time = 0
        
        # Calculate delays
        day_seconds = 24 * 60 * 60
        bursts_per_day = max_requests / self._burst_size
        
        # # Delays between requests in same burst
        # self._burst_min_delay = 5  # 5 seconds minimum between requests in burst
        # self._burst_max_delay = 15  # 15 seconds maximum between requests in burst
        
        # # Delays between bursts
        # self._break_min_delay = day_seconds / (bursts_per_day * 2)  # Minimum break between bursts
        # self._break_max_delay = day_seconds / bursts_per_day  # Maximum break between bursts

        # Delays between requests in same burst
        self._burst_min_delay = 0  # 5 seconds minimum between requests in burst
        self._burst_max_delay = 0  # 15 seconds maximum between requests in burst
        
        # Delays between bursts
        self._break_min_delay = 0 
        self._break_max_delay = 0 
        
        logger.info(f"""
Rate Limiter Configuration:
-------------------------
Max Requests: {max_requests} per day
Burst Size: {self._burst_size} requests
Burst Delays: {self._burst_min_delay}-{self._burst_max_delay}s
Break Delays: {self._break_min_delay/60:.1f}-{self._break_max_delay/60:.1f} minutes
State File: {self._state_file}
        """)
        
        self._load_state()

    def _load_state(self):
        """Load previous request timestamps."""
        try:
            if self._state_file.exists():
                with open(self._state_file) as f:
                    data = json.load(f)
                    self._requests = [ts for ts in data['requests'] 
                                    if time.time() - ts < 24*60*60]
                    self._last_burst_time = data.get('last_burst_time', 0)
                    self._current_burst = data.get('current_burst', 0)
                logger.info(f"Loaded {len(self._requests)} previous requests")
        except Exception as e:
            logger.error(f"Failed to load rate limiter state: {e}")
            self._requests = []

    def _save_state(self):
        """Save current state."""
        try:
            state = {
                'requests': self._requests,
                'last_burst_time': self._last_burst_time,
                'current_burst': self._current_burst
            }
            with open(self._state_file, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            logger.error(f"Failed to save rate limiter state: {e}")

    def _clean_old_requests(self):
        """Remove requests older than 24 hours."""
        now = time.time()
        self._requests = [ts for ts in self._requests if now - ts < 24*60*60]

    def _get_delay(self) -> float:
        """Calculate delay based on burst pattern."""
        now = time.time()
        
        # If this is the first request or we're starting a new burst
        if not self._requests or self._current_burst >= self._burst_size:
            # Calculate break time between bursts
            self._current_burst = 0
            self._burst_size = random.randint(3, 5)  # Randomize next burst size
            
            # Add randomness to break duration
            base_break = random.uniform(self._break_min_delay, self._break_max_delay)
            jitter = random.uniform(0.8, 1.2)  # ±20% variation
            return base_break * jitter
        
        # If we're in the middle of a burst
        return random.uniform(self._burst_min_delay, self._burst_max_delay)

    async def acquire(self):
        """Wait appropriate time before allowing next request."""
        try:
            self._clean_old_requests()
            
            # Check daily limit
            if len(self._requests) >= self._max_requests:
                oldest = min(self._requests)
                wait_time = oldest + (24*60*60) - time.time()
                if wait_time > 0:
                    logger.warning(f"Daily limit reached. Waiting {wait_time/3600:.1f} hours")
                    await asyncio.sleep(wait_time)
                    self._clean_old_requests()
            
            # Get and apply delay
            delay = self._get_delay()
            
            # Log what's happening
            if self._current_burst == 0:
                logger.info(f"Starting new burst of {self._burst_size} requests after {delay/60:.1f} minute break")
            else:
                logger.debug(f"Burst request {self._current_burst + 1}/{self._burst_size}, delay: {delay:.1f}s")
            
            await asyncio.sleep(delay)
            
            # Update state
            self._current_burst += 1
            self._last_burst_time = time.time()
            self._requests.append(self._last_burst_time)
            self._save_state()
            
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            await asyncio.sleep(self._burst_max_delay) 