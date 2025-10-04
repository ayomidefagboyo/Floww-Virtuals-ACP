"""
Usage tracking service for rate limiting agent requests.
Tracks daily usage per agent per user (IP-based for demo).
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from pathlib import Path

class UsageTracker:
    def __init__(self, data_file: str = "usage_data.json"):
        self.data_file = Path(data_file)
        self.daily_limit = 3
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load usage data from file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_data(self):
        """Save usage data to file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving usage data: {e}")
    
    def _get_user_key(self, user_ip: str) -> str:
        """Generate user key based on IP."""
        return f"user_{user_ip.replace('.', '_')}"
    
    def _get_date_key(self) -> str:
        """Get current date as string key."""
        return datetime.now().strftime("%Y-%m-%d")
    
    def _cleanup_old_data(self):
        """Remove data older than 7 days."""
        cutoff_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        for user_key in list(self.data.keys()):
            if user_key.startswith("user_"):
                for date_key in list(self.data[user_key].keys()):
                    if date_key < cutoff_date:
                        del self.data[user_key][date_key]
                if not self.data[user_key]:
                    del self.data[user_key]
    
    def can_make_request(self, user_ip: str, agent_name: str) -> tuple[bool, Dict]:
        """
        Check if user can make a request for the specified agent.
        Returns (can_request, usage_info)
        """
        self._cleanup_old_data()
        
        user_key = self._get_user_key(user_ip)
        date_key = self._get_date_key()
        
        # Initialize user data if not exists
        if user_key not in self.data:
            self.data[user_key] = {}
        
        if date_key not in self.data[user_key]:
            self.data[user_key][date_key] = {}
        
        # Get current usage for this agent
        agent_usage = self.data[user_key][date_key].get(agent_name, 0)
        
        can_request = agent_usage < self.daily_limit
        remaining = max(0, self.daily_limit - agent_usage)
        
        usage_info = {
            "agent": agent_name,
            "used_today": agent_usage,
            "daily_limit": self.daily_limit,
            "remaining": remaining,
            "can_request": can_request,
            "reset_time": self._get_reset_time()
        }
        
        return can_request, usage_info
    
    def record_request(self, user_ip: str, agent_name: str) -> Dict:
        """Record a request and return updated usage info."""
        user_key = self._get_user_key(user_ip)
        date_key = self._get_date_key()
        
        # Initialize if needed
        if user_key not in self.data:
            self.data[user_key] = {}
        if date_key not in self.data[user_key]:
            self.data[user_key][date_key] = {}
        
        # Increment usage
        self.data[user_key][date_key][agent_name] = self.data[user_key][date_key].get(agent_name, 0) + 1
        
        # Save data
        self._save_data()
        
        # Return updated usage info
        _, usage_info = self.can_make_request(user_ip, agent_name)
        return usage_info
    
    def get_usage_info(self, user_ip: str, agent_name: str) -> Dict:
        """Get current usage info without recording a request."""
        _, usage_info = self.can_make_request(user_ip, agent_name)
        return usage_info
    
    def _get_reset_time(self) -> str:
        """Get time when daily limit resets (next midnight)."""
        tomorrow = datetime.now() + timedelta(days=1)
        reset_time = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        return reset_time.isoformat()
    
    def get_all_usage(self, user_ip: str) -> Dict:
        """Get usage info for all agents for a user."""
        user_key = self._get_user_key(user_ip)
        date_key = self._get_date_key()
        
        if user_key not in self.data or date_key not in self.data[user_key]:
            return {}
        
        usage = {}
        for agent_name in self.data[user_key][date_key]:
            usage[agent_name] = self.get_usage_info(user_ip, agent_name)
        
        return usage

# Global instance
usage_tracker = UsageTracker()
