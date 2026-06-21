"""Worker agents for NanoCorp - Phase 3 Complete"""
from .webdev_worker import WebDevWorker
from .marketing_worker import MarketingWorker
from .email_worker import EmailWorker
from .social_media_worker import SocialMediaWorker
from .document_worker import DocumentWorker
from .content_worker import ContentWorker
from .research_networker_workers import ResearcherWorker, NetworkerWorker
from .devops_worker import DevOpsWorker
from .sales_worker import SalesWorker
from .finance_worker import FinanceWorker
from .legal_worker import LegalWorker
from .hr_worker import HRWorker
from .support_worker import SupportWorker

__all__ = [
    # Original Workers
    "WebDevWorker",
    "MarketingWorker",
    "EmailWorker",
    "SocialMediaWorker",
    "DocumentWorker",
    "ContentWorker",
    "ResearcherWorker",
    "NetworkerWorker",
    
    # Phase 3 Elite Workers
    "DevOpsWorker",
    "SalesWorker",
    "FinanceWorker",
    "LegalWorker",
    "HRWorker",
    "SupportWorker",
]
