# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import base64
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Repository:
    name: str
    full_name: str
    description: str
    url: str
    stars: int
    last_updated: datetime
    readme_content: str = ""


class GitHubSearchAgent:
    """Agent for searching GitHub repositories using Airbyte."""

    def __init__(self):
        """Initialize the GitHub search agent using gh CLI."""
        # Verify gh CLI is authenticated
        try:
            subprocess.run(["gh", "auth", "status"], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("GitHub CLI not authenticated") from e

    def search_airbyte_repos(self, min_stars: int = 5) -> List[Repository]:
        """
        Search for repositories using Airbyte with meaningful implementations.

        Args:
            min_stars: Minimum number of stars to filter repositories

        Returns:
            List of Repository objects containing relevant information
        """
        query = f"airbyte in:readme in:description stars:>={min_stars}"

        # Use gh search repos with --json flag to get structured output
        cmd = [
            "gh",
            "search",
            "repos",
            "--sort=stars",
            "--limit=30",
            "--json=name,fullName,description,url,stargazersCount,updatedAt",
            query,
        ]
        print(f"Executing search command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if not result.stdout.strip():
                print("No repositories found")
                return []
            repos_data = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error searching repositories: {e}")
            print(f"Error output: {e.stderr if hasattr(e, 'stderr') else 'No error output'}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw output: {result.stdout}")
            return []

        repos = []
        for item in repos_data:
            try:
                # Get README content using gh api
                readme_cmd = ["gh", "api", f"repos/{item['fullName']}/readme", "--jq", ".content", "--method", "GET"]
                try:
                    readme_result = subprocess.run(readme_cmd, capture_output=True, text=True, check=True)
                    readme_content = base64.b64decode(readme_result.stdout.strip()).decode("utf-8")
                except (subprocess.CalledProcessError, base64.binascii.Error) as e:
                    print(f"Warning: Could not fetch README for {item['fullName']}: {e}")
                    readme_content = ""

                repo = Repository(
                    name=item["name"],
                    full_name=item["fullName"],
                    description=item.get("description", ""),
                    url=item["url"],
                    stars=item["stargazersCount"],
                    last_updated=datetime.strptime(item["updatedAt"], "%Y-%m-%dT%H:%M:%SZ"),
                    readme_content=readme_content,
                )
                repos.append(repo)
            except Exception as e:
                print(f"Error processing repository {item['fullName']}: {e}")
                continue

        return repos

    def filter_relevant_repos(self, repos: List[Repository]) -> List[Repository]:
        """
        Filter repositories to find those with meaningful Airbyte implementations.

        Args:
            repos: List of repositories to filter

        Returns:
            Filtered list of repositories
        """
        relevant_repos = []

        for repo in repos:
            if not repo.readme_content:
                continue

            readme_content = repo.readme_content.lower()

            # Check for meaningful Airbyte-related content
            airbyte_indicators = [
                "airbyte connector",
                "airbyte integration",
                "airbyte pipeline",
                "airbyte configuration",
                "data pipeline",
                "etl",
                "data integration",
            ]

            # Count how many indicators are present
            indicator_count = sum(1 for indicator in airbyte_indicators if indicator in readme_content)

            # If at least 2 indicators are present, consider it relevant
            if indicator_count >= 2:
                relevant_repos.append(repo)

        return relevant_repos


if __name__ == "__main__":
    try:
        # Example usage
        agent = GitHubSearchAgent()
        print("Searching for Airbyte repositories...")
        repos = agent.search_airbyte_repos(min_stars=5)
        print(f"Found {len(repos)} repositories, filtering for relevant ones...")
        relevant_repos = agent.filter_relevant_repos(repos)

        print(f"\nFound {len(relevant_repos)} relevant repositories:")
        for repo in relevant_repos:
            print(f"\nRepository: {repo.full_name}")
            print(f"Description: {repo.description}")
            print(f"Stars: {repo.stars}")
            print(f"URL: {repo.url}")
    except Exception as e:
        print(f"Error: {e}")
