# models package
from src.models.cv_models import (
    CVData,
    Education,
    WorkExperience,
    Project,
    Language,
    LanguageLevel,
)
from src.models.job_models import JobListing
from src.models.analysis_models import (
    MarketRequirements,
    SkillFrequency,
    GapAnalysis,
    Gap,
    GapType,
)
from src.models.report_models import (
    Recommendation,
    RecommendationType,
    FinalReport,
)

__all__ = [
    "CVData",
    "Education",
    "WorkExperience",
    "Project",
    "Language",
    "LanguageLevel",
    "JobListing",
    "MarketRequirements",
    "SkillFrequency",
    "GapAnalysis",
    "Gap",
    "GapType",
    "Recommendation",
    "RecommendationType",
    "FinalReport",
]
