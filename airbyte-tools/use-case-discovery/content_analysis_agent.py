import re
from dataclasses import dataclass
from typing import List, Optional
from github_search_agent import Repository

@dataclass
class ProjectAnalysis:
    repository: Repository
    use_case: str
    integration_type: str  # connector, pipeline, platform, etc.
    key_features: List[str]
    target_audience: str
    complexity_level: str  # basic, intermediate, advanced
    interesting_aspects: List[str]

class ContentAnalysisAgent:
    """Agent for analyzing README content to understand Airbyte usage patterns."""
    
    def __init__(self):
        self.integration_patterns = {
            'connector': [
                r'airbyte\s+connector',
                r'source\s+connector',
                r'destination\s+connector',
                r'custom\s+connector'
            ],
            'pipeline': [
                r'data\s+pipeline',
                r'etl\s+pipeline',
                r'workflow',
                r'orchestration'
            ],
            'platform': [
                r'data\s+platform',
                r'integration\s+platform',
                r'infrastructure'
            ]
        }
        
        self.audience_indicators = {
            'developers': ['developer', 'engineer', 'coding', 'technical'],
            'data_teams': ['data scientist', 'data engineer', 'analyst', 'analytics'],
            'business': ['business user', 'stakeholder', 'no-code', 'low-code']
        }
    
    def analyze_repository(self, repo: Repository) -> Optional[ProjectAnalysis]:
        """
        Analyze a repository's README content to understand its Airbyte usage.
        
        Args:
            repo: Repository object containing README content
            
        Returns:
            ProjectAnalysis object if analysis is successful, None otherwise
        """
        if not repo.readme_content:
            return None
            
        content = repo.readme_content.lower()
        
        # Determine integration type
        integration_type = self._determine_integration_type(content)
        
        # Extract key features
        key_features = self._extract_key_features(content)
        
        # Determine target audience
        target_audience = self._determine_target_audience(content)
        
        # Determine complexity level
        complexity_level = self._determine_complexity(content, key_features)
        
        # Identify interesting aspects
        interesting_aspects = self._identify_interesting_aspects(content, repo)
        
        # Extract primary use case
        use_case = self._extract_use_case(content, repo.description)
        
        return ProjectAnalysis(
            repository=repo,
            use_case=use_case,
            integration_type=integration_type,
            key_features=key_features,
            target_audience=target_audience,
            complexity_level=complexity_level,
            interesting_aspects=interesting_aspects
        )
    
    def _determine_integration_type(self, content: str) -> str:
        """Determine the primary type of Airbyte integration."""
        type_counts = {
            itype: sum(1 for pattern in patterns if re.search(pattern, content))
            for itype, patterns in self.integration_patterns.items()
        }
        
        if not any(type_counts.values()):
            return "other"
            
        return max(type_counts.items(), key=lambda x: x[1])[0]
    
    def _extract_key_features(self, content: str) -> List[str]:
        """Extract key features from the README content."""
        content = self._clean_text(content)
        features = []
        
        # Airbyte-specific feature patterns
        airbyte_patterns = {
            'custom_connector': [
                r'custom\s+(?:airbyte\s+)?connector\s+(?:for|to)\s+([^.\n]+)',
                r'(?:built|created)\s+(?:a|an)\s+airbyte\s+connector\s+(?:for|to)\s+([^.\n]+)',
                r'airbyte\s+(?:source|destination)\s+connector\s+(?:for|to)\s+([^.\n]+)',
                r'connector\s+development\s+(?:for|with)\s+([^.\n]+)'
            ],
            'data_sync': [
                r'(?:incremental|full refresh)\s+sync\s+(?:for|with)\s+([^.\n]+)',
                r'synchroniz(?:e|ing)\s+data\s+(?:between|from|to)\s+([^.\n]+)',
                r'data\s+replication\s+(?:from|to)\s+([^.\n]+)',
                r'extract(?:ing)?\s+data\s+from\s+([^.\n]+)',
                r'load(?:ing)?\s+data\s+(?:into|to)\s+([^.\n]+)'
            ],
            'transformation': [
                r'data\s+transform(?:ation|ing)\s+(?:using|with)\s+([^.\n]+)',
                r'transform(?:s|ing)?\s+(?:the\s+)?data\s+(?:to|into|for)\s+([^.\n]+)'
            ],
            'integration': [
                r'integrat(?:e|ing|ion)\s+with\s+([^.\n]+)',
                r'connect(?:s|ing)?\s+to\s+([^.\n]+)'
            ],
            'orchestration': [
                r'orchestrat(?:e|ing|ion)\s+(?:of\s+)?([^.\n]+)',
                r'pipeline\s+(?:for|to)\s+([^.\n]+)'
            ]
        }
        
        for feature_type, patterns in airbyte_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    feature_desc = match.group(1).strip()
                    if feature_desc:
                        features.append(f"{feature_type.replace('_', ' ')}: {feature_desc}")
        
        # If no specific features found, look for general feature lists
        if not features:
            feature_sections = re.findall(
                r'(?:features|highlights|what it does)[:|-]\s*(?:\n\s*[-*]\s*.+)+',
                content,
                re.IGNORECASE
            )
            
            if feature_sections:
                for section in feature_sections:
                    features.extend(re.findall(r'[-*]\s*(.+)', section))
        
        # Deduplicate and limit features
        unique_features = []
        seen = set()
        for feature in features:
            feature_key = feature.lower()
            if feature_key not in seen and len(unique_features) < 5:
                seen.add(feature_key)
                unique_features.append(feature)
        
        return unique_features
    
    def _determine_target_audience(self, content: str) -> str:
        """Determine the primary target audience."""
        audience_counts = {
            audience: sum(1 for indicator in indicators if indicator in content)
            for audience, indicators in self.audience_indicators.items()
        }
        
        if not any(audience_counts.values()):
            return "general"
            
        return max(audience_counts.items(), key=lambda x: x[1])[0]
    
    def _determine_complexity(self, content: str, features: List[str]) -> str:
        """Determine the complexity level of the integration."""
        complexity_score = 0
        
        # Check for advanced features
        advanced_indicators = [
            'custom',
            'advanced',
            'complex',
            'enterprise',
            'scalable'
        ]
        
        # Check for basic features
        basic_indicators = [
            'simple',
            'basic',
            'easy',
            'straightforward',
            'quick'
        ]
        
        complexity_score += sum(2 for indicator in advanced_indicators 
                              if any(indicator in f.lower() for f in features))
        complexity_score -= sum(1 for indicator in basic_indicators 
                              if any(indicator in f.lower() for f in features))
        
        if complexity_score > 2:
            return "advanced"
        elif complexity_score < 0:
            return "basic"
        else:
            return "intermediate"
    
    def _identify_interesting_aspects(self, content: str, repo: Repository) -> List[str]:
        """Identify interesting aspects of the project."""
        aspects = []
        
        # Check for unique integration patterns
        if 'custom connector' in content:
            aspects.append("Custom Airbyte connector implementation")
        
        # Check for scale indicators
        if any(scale in content for scale in ['enterprise', 'scale', 'production']):
            aspects.append("Production-grade implementation")
        
        # Check for innovative uses
        if any(innovation in content for innovation in ['novel', 'unique', 'innovative']):
            aspects.append("Innovative use of Airbyte")
        
        # Check repository metrics
        if repo.stars > 1000:
            aspects.append(f"Popular project with {repo.stars} stars")
        
        return aspects
    
    def _clean_text(self, text: str) -> str:
        """Clean markdown and HTML content from text."""
        if not text:
            return ""
            
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove markdown links while keeping text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove code blocks
        text = re.sub(r'```[^`]*```', '', text)
        # Remove inline code
        text = re.sub(r'`[^`]+`', '', text)
        # Remove multiple newlines and extra whitespace
        text = re.sub(r'\n\s*\n', '\n', text)
        # Remove special characters and normalize whitespace
        text = re.sub(r'[|\\{}\[\]]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        return text.strip()

    def _extract_use_case(self, content: str, description: str) -> str:
        """Extract the primary use case from README content and description."""
        content = self._clean_text(content)
        
        # First look for Airbyte-specific use cases
        airbyte_patterns = [
            r'(?:using|with)\s+airbyte\s+to\s+([^.\n]+)',
            r'airbyte\s+(?:helps|enables)\s+([^.\n]+)',
            r'airbyte\s+integration\s+(?:for|that)\s+([^.\n]+)',
            r'(?:built|created|developed)\s+(?:with|using)\s+airbyte\s+(?:to|for)\s+([^.\n]+)',
            r'airbyte\s+connector\s+(?:that|which|to)\s+([^.\n]+)',
            r'data\s+pipeline\s+using\s+airbyte\s+(?:to|for)\s+([^.\n]+)'
        ]
        
        for pattern in airbyte_patterns:
            matches = re.search(pattern, content, re.IGNORECASE)
            if matches:
                return matches.group(1).strip()
        
        # Then try general use case statements
        use_case_patterns = [
            r'use case[s]?[:|-]\s*([^.\n]+)',
            r'designed (?:to|for)\s+([^.\n]+)',
            r'helps (?:to|with)\s+([^.\n]+)',
            r'enables\s+([^.\n]+)'
        ]
        
        for pattern in use_case_patterns:
            matches = re.search(pattern, content, re.IGNORECASE)
            if matches:
                return matches.group(1).strip()
        
        # If no explicit use case found, clean and use the description
        if description:
            clean_desc = self._clean_text(description)
            return clean_desc.split('.')[0].strip()
        
        return "General Airbyte integration"

if __name__ == "__main__":
    # Example usage
    from github_search_agent import GitHubSearchAgent
    
    # Get repositories
    search_agent = GitHubSearchAgent()
    repos = search_agent.search_airbyte_repos(min_stars=5)
    relevant_repos = search_agent.filter_relevant_repos(repos)
    
    # Analyze repositories
    analysis_agent = ContentAnalysisAgent()
    analyses = []
    
    print("\nAnalyzing repositories...")
    for repo in relevant_repos:
        analysis = analysis_agent.analyze_repository(repo)
        if analysis:
            analyses.append(analysis)
            print(f"\nRepository: {repo.full_name}")
            print(f"Use Case: {analysis.use_case}")
            print(f"Integration Type: {analysis.integration_type}")
            print(f"Key Features: {', '.join(analysis.key_features)}")
            print(f"Target Audience: {analysis.target_audience}")
            print(f"Complexity: {analysis.complexity_level}")
            if analysis.interesting_aspects:
                print(f"Interesting Aspects: {', '.join(analysis.interesting_aspects)}")
