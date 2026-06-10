#!/usr/bin/env python3
"""
Generate real-time programming language statistics from GitHub repositories.
This script fetches all repositories and calculates language usage percentages.
"""

import os
import requests
from collections import defaultdict
from typing import Dict, List, Tuple

# Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = 'ChanSuvannet'
API_BASE_URL = 'https://api.github.com'

# Language bar configuration
BAR_LENGTH = 40
FULL_BLOCK = '█'
EMPTY_BLOCK = '░'

class LanguageStatsGenerator:
    def __init__(self, username: str, token: str = None):
        self.username = username
        self.token = token
        self.headers = self._get_headers()
        self.language_stats: Dict[str, int] = defaultdict(int)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests."""
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        return headers
    
    def fetch_repositories(self) -> List[Dict]:
        """Fetch all repositories for the user."""
        repos = []
        page = 1
        per_page = 100
        
        while True:
            url = f'{API_BASE_URL}/users/{self.username}/repos'
            params = {'page': page, 'per_page': per_page, 'type': 'owner'}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                break
            
            repos.extend(data)
            page += 1
        
        return repos
    
    def count_languages(self, repos: List[Dict]) -> Dict[str, int]:
        """Count primary languages across all repositories."""
        language_count = defaultdict(int)
        
        for repo in repos:
            language = repo.get('language')
            if language:
                language_count[language] += 1
        
        return dict(language_count)
    
    def calculate_percentages(self, language_count: Dict[str, int]) -> List[Tuple[str, float]]:
        """Calculate percentage for each language."""
        total = sum(language_count.values())
        if total == 0:
            return []
        
        percentages = [
            (lang, (count / total) * 100)
            for lang, count in language_count.items()
        ]
        
        # Sort by percentage descending
        percentages.sort(key=lambda x: x[1], reverse=True)
        return percentages
    
    def generate_bar(self, percentage: float) -> str:
        """Generate a visual progress bar for the percentage."""
        filled = int((percentage / 100) * BAR_LENGTH)
        empty = BAR_LENGTH - filled
        bar = FULL_BLOCK * filled + EMPTY_BLOCK * empty
        return bar
    
    def generate_markdown(self, language_stats: List[Tuple[str, float]]) -> str:
        """Generate markdown table with language statistics."""
        lines = [
            "### 📊 Most Used Programming Languages\n",
            "**Visual Breakdown**\n",
            "```"
        ]
        
        for language, percentage in language_stats:
            bar = self.generate_bar(percentage)
            lines.append(f"{language:<12} {bar} {percentage:>5.1f}%")
        
        lines.append("```")
        
        return '\n'.join(lines)
    
    def run(self) -> str:
        """Run the full generation process."""
        print(f"Fetching repositories for {self.username}...")
        repos = self.fetch_repositories()
        print(f"Found {len(repos)} repositories")
        
        print("Counting languages...")
        language_count = self.count_languages(repos)
        print(f"Found {len(language_count)} different languages")
        
        print("Calculating percentages...")
        language_stats = self.calculate_percentages(language_count)
        
        # Print stats to console
        for language, percentage in language_stats:
            count = language_count[language]
            print(f"  {language}: {count} repos ({percentage:.1f}%)")
        
        markdown = self.generate_markdown(language_stats)
        return markdown

def main():
    """Main entry point."""
    generator = LanguageStatsGenerator(GITHUB_USERNAME, GITHUB_TOKEN)
    markdown = generator.run()
    print("\n" + "="*50)
    print("Generated Markdown:\n")
    print(markdown)
    print("="*50)

if __name__ == '__main__':
    main()
