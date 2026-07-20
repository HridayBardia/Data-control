from abc import ABC, abstractmethod
from typing import Any, Dict, List, Generator
from sqlalchemy.orm import Session
from app.models.entities import ConnectorInstance, KnowledgeNode, KnowledgeEdge

class BaseConnector(ABC):
    """
    Abstract Base Class defining the Project Atlas Connector SDK.
    Every enterprise source connector must implement this interface.
    """
    
    def __init__(self, instance: ConnectorInstance, db: Session):
        self.instance = instance
        self.db = db
        self.config = instance.config

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Verify connection and validate oauth2 tokens/credentials against the external service.
        Returns True if authenticated, raises exception or returns False otherwise.
        """
        pass

    @abstractmethod
    def discover(self) -> List[Dict[str, Any]]:
        """
        Discover accessible entities/collections available from the resource (e.g. lists of Slack channels, Git repos).
        """
        pass

    @abstractmethod
    def sync(self) -> Generator[Dict[str, Any], None, None]:
        """
        Perform extraction/incremental sync of data records from the source.
        Yields raw records to be normalized.
        """
        pass

    @abstractmethod
    def normalize(self, raw_data: Dict[str, Any]) -> tuple[KnowledgeNode, List[KnowledgeEdge]]:
        """
        Converts the source-specific raw JSON data into the standardized
        Project Atlas KnowledgeNode and list of related KnowledgeEdges.
        """
        pass

    @abstractmethod
    def permissions(self, external_user_ref: str) -> List[str]:
        """
        Retrieves the access permissions (ACLs) from the source system for a user identifier.
        Enables permissions-aware query filtering.
        """
        pass

    @abstractmethod
    def webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes real-time change events sent from the remote source.
        """
        pass

    @abstractmethod
    def health(self) -> bool:
        """
        Check connectivity and rate-limit state of the API.
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Revokes remote tokens and performs local teardown cleanup.
        """
        pass
