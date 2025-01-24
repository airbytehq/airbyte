# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import List

from content_analysis_agent import ProjectAnalysis


@dataclass
class LinkedInPost:
    title: str
    content: str
    hashtags: List[str]
    repository_url: str


class ContentGenerationAgent:
    """Agent for generating LinkedIn posts about interesting Airbyte use cases."""

    def __init__(self):
        self.max_content_length = 1300  # LinkedIn's character limit
        self.hashtag_options = {
            "general": ["#DataEngineering", "#ETL", "#DataPipeline", "#OpenSource"],
            "connector": ["#DataIntegration", "#DataConnector", "#Airbyte"],
            "pipeline": ["#DataPipeline", "#ETL", "#DataOps", "#ModernDataStack"],
            "platform": ["#DataPlatform", "#DataInfrastructure", "#DataOps"],
        }

    def generate_post(self, analysis: ProjectAnalysis) -> LinkedInPost:
        """
        Generate a LinkedIn post from a project analysis.

        Args:
            analysis: ProjectAnalysis object containing repository insights

        Returns:
            LinkedInPost object with title, content, hashtags, and repository URL
        """
        # Generate title
        title = self._generate_title(analysis)

        # Generate content
        content = self._generate_content(analysis)

        # Select relevant hashtags
        hashtags = self._select_hashtags(analysis)

        return LinkedInPost(title=title, content=content, hashtags=hashtags, repository_url=analysis.repository.url)

    def _generate_title(self, analysis: ProjectAnalysis) -> str:
        """Generate an attention-grabbing title."""
        if "Custom Airbyte connector" in analysis.interesting_aspects:
            return f"🔌 Custom Airbyte Connector Spotlight: {analysis.repository.name}"
        elif analysis.integration_type == "pipeline":
            return f"🔄 Data Pipeline Innovation: {analysis.repository.name}"
        elif analysis.integration_type == "platform":
            return f"🚀 Data Platform Showcase: {analysis.repository.name}"
        else:
            return f"💡 Airbyte Integration Spotlight: {analysis.repository.name}"

    def _generate_content(self, analysis: ProjectAnalysis) -> str:
        """Generate a simplified post with just title, use case, and URL."""
        content_parts = [
            f"Discovered an interesting Airbyte implementation in {analysis.repository.full_name}!",
            f"\n🎯 Use Case: {analysis.use_case}",
        ]

        # Combine parts
        content = "\n".join(content_parts)

        # Ensure we don't exceed LinkedIn's character limit
        if len(content) > self.max_content_length:
            # Truncate content and add ellipsis
            content = content[: self.max_content_length - 3] + "..."

        return content

    def _select_hashtags(self, analysis: ProjectAnalysis) -> List[str]:
        """Select relevant hashtags based on the analysis."""
        hashtags = set()

        # Add general hashtags
        hashtags.update(self.hashtag_options["general"][:2])

        # Add integration type specific hashtags
        type_hashtags = self.hashtag_options.get(analysis.integration_type, [])
        hashtags.update(type_hashtags[:2])

        # Add audience specific hashtags
        if analysis.target_audience == "developers":
            hashtags.add("#Developer")
        elif analysis.target_audience == "data_teams":
            hashtags.add("#DataScience")

        # Always include Airbyte
        hashtags.add("#Airbyte")

        # Convert to list and limit to 6 hashtags
        return sorted(list(hashtags))[:6]


if __name__ == "__main__":
    # Example usage
    from content_analysis_agent import ContentAnalysisAgent
    from github_search_agent import GitHubSearchAgent

    # Get repositories
    search_agent = GitHubSearchAgent()
    repos = search_agent.search_airbyte_repos(min_stars=5)
    relevant_repos = search_agent.filter_relevant_repos(repos)

    # Analyze repositories
    analysis_agent = ContentAnalysisAgent()
    generation_agent = ContentGenerationAgent()

    print("\nGenerating LinkedIn posts for interesting Airbyte implementations...")
    for repo in relevant_repos:
        analysis = analysis_agent.analyze_repository(repo)
        if analysis:
            post = generation_agent.generate_post(analysis)
            print(f"\n{'='*50}")
            print(f"{post.title}")
            print(f"{'='*50}")
            print(post.content)
            print(f"\n{' '.join(post.hashtags)}")
            print(f"\nRead more: {post.repository_url}")
