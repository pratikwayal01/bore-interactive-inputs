"""
Notification services for Slack and Discord
"""

import requests
from typing import Optional
from abc import ABC, abstractmethod


class Notifier(ABC):
    """Base notifier class"""
    
    @abstractmethod
    def send(self, status: str, message: str, url: Optional[str] = None, 
             workflow: str = '', repository: str = '', run_id: str = ''):
        """Send notification"""
        pass


class SlackNotifier(Notifier):
    """Slack notification handler"""
    
    def __init__(self, token: str, channel: str, thread_ts: str = '', bot_name: str = ''):
        self.token = token
        self.channel = channel
        self.thread_ts = thread_ts
        self.bot_name = bot_name or 'Bore Interactive Inputs'
    
    def send(self, status: str, message: str, url: Optional[str] = None,
             workflow: str = '', repository: str = '', run_id: str = ''):
        """Send Slack notification"""
        
        # Status emoji
        status_emoji = {
            'waiting': ':hourglass_flowing_sand:',
            'success': ':white_check_mark:',
            'error': ':x:',
            'timeout': ':warning:'
        }.get(status, ':information_source:')
        
        # Status color
        status_color = {
            'waiting': '#3498db',
            'success': '#2ecc71',
            'error': '#e74c3c',
            'timeout': '#f39c12'
        }.get(status, '#95a5a6')
        
        # Build message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{status_emoji} Interactive Inputs - {status.title()}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Workflow:* {workflow}\n*Repository:* {repository}\n*Message:* {message}"
                }
            }
        ]
        
        if url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{url}|Open Interactive Portal>"
                }
            })
        
        payload = {
            "channel": self.channel,
            "username": self.bot_name,
            "blocks": blocks,
            "attachments": [
                {
                    "color": status_color,
                    "text": f"Run ID: {run_id}"
                }
            ]
        }
        
        if self.thread_ts:
            payload["thread_ts"] = self.thread_ts
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            json=payload,
            headers=headers
        )
        
        if not response.ok:
            raise Exception(f"Slack API error: {response.text}")
        
        result = response.json()
        if not result.get('ok'):
            raise Exception(f"Slack API error: {result.get('error', 'Unknown error')}")


class DiscordNotifier(Notifier):
    """Discord notification handler"""
    
    def __init__(self, webhook_url: str, thread_id: str = '', username: str = ''):
        self.webhook_url = webhook_url
        self.thread_id = thread_id
        self.username = username or 'Bore Interactive Inputs'
    
    def send(self, status: str, message: str, url: Optional[str] = None,
             workflow: str = '', repository: str = '', run_id: str = ''):
        """Send Discord notification"""
        
        # Status color (Discord uses decimal color values)
        status_color = {
            'waiting': 3447003,    # Blue
            'success': 3066993,    # Green
            'error': 15158332,     # Red
            'timeout': 15844367    # Orange
        }.get(status, 9807270)     # Gray
        
        # Status emoji
        status_emoji = {
            'waiting': '⏳',
            'success': '✅',
            'error': '❌',
            'timeout': '⚠️'
        }.get(status, 'ℹ️')
        
        embed = {
            "title": f"{status_emoji} Interactive Inputs - {status.title()}",
            "description": message,
            "color": status_color,
            "fields": [
                {
                    "name": "Workflow",
                    "value": workflow,
                    "inline": True
                },
                {
                    "name": "Repository",
                    "value": repository,
                    "inline": True
                },
                {
                    "name": "Run ID",
                    "value": run_id,
                    "inline": False
                }
            ]
        }
        
        if url:
            embed["fields"].append({
                "name": "Portal URL",
                "value": f"[Open Interactive Portal]({url})",
                "inline": False
            })
        
        payload = {
            "username": self.username,
            "embeds": [embed]
        }
        
        # Add thread_id to URL if specified
        webhook_url = self.webhook_url
        if self.thread_id:
            webhook_url += f"?thread_id={self.thread_id}"
        
        response = requests.post(webhook_url, json=payload)
        
        if not response.ok:
            raise Exception(f"Discord webhook error: {response.text}")
