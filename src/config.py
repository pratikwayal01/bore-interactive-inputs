"""
Configuration module for Bore Interactive Inputs
"""

import os
import yaml
from typing import Dict, List, Any, Optional


class Config:
    """Configuration from environment variables"""
    
    def __init__(self):
        # Main inputs
        self.title = os.getenv('INPUT_TITLE', 'Interactive Inputs')
        self.timeout = int(os.getenv('INPUT_TIMEOUT', '300'))
        
        # Parse interactive fields from YAML
        interactive_yaml = os.getenv('INPUT_INTERACTIVE', '')
        self.interactive_fields = self._parse_interactive(interactive_yaml)
        
        # Bore tunnel settings
        self.bore_server = os.getenv('INPUT_BORE_SERVER', 'bore.pub')
        self.bore_port = int(os.getenv('INPUT_BORE_PORT', '0'))
        self.bore_secret = os.getenv('INPUT_BORE_SECRET', '')
        
        # GitHub settings
        self.github_token = os.getenv('INPUT_GITHUB_TOKEN', '')
        self.github_repository = os.getenv('GITHUB_REPOSITORY', '')
        self.github_run_id = os.getenv('GITHUB_RUN_ID', '')
        self.github_run_number = os.getenv('GITHUB_RUN_NUMBER', '')
        self.github_workflow = os.getenv('GITHUB_WORKFLOW', '')
        self.github_server_url = os.getenv('GITHUB_SERVER_URL', 'https://github.com')
        
        # Slack notifier settings
        self.notifier_slack_enabled = os.getenv('INPUT_NOTIFIER_SLACK_ENABLED', 'false').lower() == 'true'
        self.notifier_slack_token = os.getenv('INPUT_NOTIFIER_SLACK_TOKEN', '')
        self.notifier_slack_channel = os.getenv('INPUT_NOTIFIER_SLACK_CHANNEL', '#notifications')
        self.notifier_slack_thread_ts = os.getenv('INPUT_NOTIFIER_SLACK_THREAD_TS', '')
        self.notifier_slack_bot = os.getenv('INPUT_NOTIFIER_SLACK_BOT', 'Bore Interactive Inputs')
        
        # Discord notifier settings
        self.notifier_discord_enabled = os.getenv('INPUT_NOTIFIER_DISCORD_ENABLED', 'false').lower() == 'true'
        self.notifier_discord_webhook = os.getenv('INPUT_NOTIFIER_DISCORD_WEBHOOK', '')
        self.notifier_discord_thread_id = os.getenv('INPUT_NOTIFIER_DISCORD_THREAD_ID', '')
        self.notifier_discord_username = os.getenv('INPUT_NOTIFIER_DISCORD_USERNAME', 'Bore Interactive Inputs')
    
    def _parse_interactive(self, yaml_str: str) -> List[Dict[str, Any]]:
        """Parse interactive fields from YAML string"""
        if not yaml_str:
            return []
        
        try:
            data = yaml.safe_load(yaml_str)
            if isinstance(data, dict) and 'fields' in data:
                return data['fields']
            return []
        except yaml.YAMLError as e:
            print(f"Error parsing interactive YAML: {e}")
            return []
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables"""
        return cls()
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if not self.interactive_fields:
            errors.append("No interactive fields defined")
        
        if not self.bore_server:
            errors.append("Bore server address is required")
        
        if self.notifier_slack_enabled and not self.notifier_slack_token:
            errors.append("Slack token is required when Slack notifications are enabled")
        
        if self.notifier_discord_enabled and not self.notifier_discord_webhook:
            errors.append("Discord webhook is required when Discord notifications are enabled")
        
        return errors
