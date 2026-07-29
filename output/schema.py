from pydantic import BaseModel, Field
from typing import List, Optional

class ThemeOutputSchema(BaseModel):
    theme: str = Field(description="Name of the behavioral theme cluster")
    example_quotes: List[str] = Field(description="Representative customer quotes")
    frequency: int = Field(description="Total count of customer mentions in this theme")
    prevalence_score: float = Field(description="Prevalence score on 1-5 scale")
    signal_strength_score: float = Field(description="Signal strength score on 1-5 scale")
    sources: List[str] = Field(description="Data sources where this theme appeared")
    sentiment: str = Field(description="Sentiment distribution summary string")
    action: str = Field(description="Prioritization decision (Promote, Monitor, Niche, Drop)")
    suggested_insight: Optional[str] = Field(default="", description="1-sentence evidence-backed hypothesis")
    suggested_research_question: Optional[str] = Field(default="", description="Open-ended interview research question for PMs")

class EngineResultsSchema(BaseModel):
    total_feedback_analyzed: int
    promoted_themes_count: int
    results: List[ThemeOutputSchema]
