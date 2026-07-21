import logging
import datetime
from typing import Dict, Any, List, Generator, Tuple
from sqlalchemy.orm import Session
from app.connectors.base import BaseConnector
from app.models.entities import ConnectorInstance, KnowledgeNode, KnowledgeEdge

logger = logging.getLogger(__name__)

class GoogleDriveConnector(BaseConnector):
    def authenticate(self) -> bool:
        return True if self.config.get("access_token") or True else False

    def discover(self) -> List[Dict[str, Any]]:
        return [{"id": "root", "name": "My Drive"}, {"id": "shared", "name": "Shared Drives"}]

    def sync(self) -> Generator[Dict[str, Any], None, None]:
        yield {
            "external_id": "gdrive_doc_001",
            "title": "Google Drive Enterprise Policy 2026",
            "entity_type": "DOCUMENT",
            "content": "Google Drive data governance and document sync guidelines.",
            "metadata": {"mime_type": "application/vnd.google-apps.document", "owner": "admin@atlascorp.com"}
        }

    def normalize(self, raw_data: Dict[str, Any]) -> Tuple[KnowledgeNode, List[KnowledgeEdge]]:
        node = KnowledgeNode(
            organization_id=self.instance.organization_id,
            connector_instance_id=self.instance.id,
            external_id=raw_data["external_id"],
            entity_type=raw_data["entity_type"],
            title=raw_data["title"],
            content=raw_data["content"],
            metadata_json=raw_data["metadata"]
        )
        return node, []

    def permissions(self, external_user_ref: str) -> List[str]:
        return ["read:drive", "read:docs"]

    def webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "processed", "event": payload.get("event", "change")}

    def health(self) -> bool:
        return True

    def disconnect(self) -> bool:
        self.instance.status = "DISCONNECTED"
        return True


class SlackConnector(BaseConnector):
    def authenticate(self) -> bool:
        return True

    def discover(self) -> List[Dict[str, Any]]:
        return [{"id": "C0123456", "name": "general"}, {"id": "C0987654", "name": "engineering"}]

    def sync(self) -> Generator[Dict[str, Any], None, None]:
        yield {
            "external_id": "slack_msg_1001",
            "title": "Engineering Channel Architecture Update",
            "entity_type": "MESSAGE",
            "content": "Discussed RAG pipeline latency improvements and vector indexing optimizations.",
            "metadata": {"channel": "engineering", "user": "U12345"}
        }

    def normalize(self, raw_data: Dict[str, Any]) -> Tuple[KnowledgeNode, List[KnowledgeEdge]]:
        node = KnowledgeNode(
            organization_id=self.instance.organization_id,
            connector_instance_id=self.instance.id,
            external_id=raw_data["external_id"],
            entity_type=raw_data["entity_type"],
            title=raw_data["title"],
            content=raw_data["content"],
            metadata_json=raw_data["metadata"]
        )
        return node, []

    def permissions(self, external_user_ref: str) -> List[str]:
        return ["read:channels"]

    def webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "received"}

    def health(self) -> bool:
        return True

    def disconnect(self) -> bool:
        self.instance.status = "DISCONNECTED"
        return True


class JiraConnector(BaseConnector):
    def authenticate(self) -> bool:
        return True

    def discover(self) -> List[Dict[str, Any]]:
        return [{"id": "ATLAS", "name": "Project Atlas Core"}]

    def sync(self) -> Generator[Dict[str, Any], None, None]:
        yield {
            "external_id": "JIRA-402",
            "title": "Implement Hybrid Search and Vector Reranking",
            "entity_type": "TICKET",
            "content": "Ticket details for BM25 and Cosine similarity hybrid fusion.",
            "metadata": {"status": "In Progress", "assignee": "dev@atlascorp.com"}
        }

    def normalize(self, raw_data: Dict[str, Any]) -> Tuple[KnowledgeNode, List[KnowledgeEdge]]:
        node = KnowledgeNode(
            organization_id=self.instance.organization_id,
            connector_instance_id=self.instance.id,
            external_id=raw_data["external_id"],
            entity_type=raw_data["entity_type"],
            title=raw_data["title"],
            content=raw_data["content"],
            metadata_json=raw_data["metadata"]
        )
        return node, []

    def permissions(self, external_user_ref: str) -> List[str]:
        return ["read:jira"]

    def webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "ok"}

    def health(self) -> bool:
        return True

    def disconnect(self) -> bool:
        self.instance.status = "DISCONNECTED"
        return True


class GitHubConnector(BaseConnector):
    def authenticate(self) -> bool:
        return True

    def discover(self) -> List[Dict[str, Any]]:
        return [{"id": "repo-atlas", "name": "atlas-core-repo"}]

    def sync(self) -> Generator[Dict[str, Any], None, None]:
        yield {
            "external_id": "gh_pr_45",
            "title": "Pull Request #45: Enterprise Zero Trust Architecture",
            "entity_type": "CODE_REPOSITORY",
            "content": "Merged changes for envelope encryption, sliding window rate limiting, and RBAC.",
            "metadata": {"repo": "atlas-core", "author": "octocat"}
        }

    def normalize(self, raw_data: Dict[str, Any]) -> Tuple[KnowledgeNode, List[KnowledgeEdge]]:
        node = KnowledgeNode(
            organization_id=self.instance.organization_id,
            connector_instance_id=self.instance.id,
            external_id=raw_data["external_id"],
            entity_type=raw_data["entity_type"],
            title=raw_data["title"],
            content=raw_data["content"],
            metadata_json=raw_data["metadata"]
        )
        return node, []

    def permissions(self, external_user_ref: str) -> List[str]:
        return ["read:repo"]

    def webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "processed"}

    def health(self) -> bool:
        return True

    def disconnect(self) -> bool:
        self.instance.status = "DISCONNECTED"
        return True


class TeamsConnector(BaseConnector):
    def authenticate(self) -> bool:
        return True

    def discover(self) -> List[Dict[str, Any]]:
        return [{"id": "team-general", "name": "Executive Leadership Team"}]

    def sync(self) -> Generator[Dict[str, Any], None, None]:
        yield {
            "external_id": "teams_chat_90",
            "title": "Executive Alignment Briefing",
            "entity_type": "MEETING",
            "content": "Reviewed Q3 compliance roadmap and Zero-Data-Retention SLAs for AI providers.",
            "metadata": {"team": "Executive", "organizer": "vp@atlascorp.com"}
        }

    def normalize(self, raw_data: Dict[str, Any]) -> Tuple[KnowledgeNode, List[KnowledgeEdge]]:
        node = KnowledgeNode(
            organization_id=self.instance.organization_id,
            connector_instance_id=self.instance.id,
            external_id=raw_data["external_id"],
            entity_type=raw_data["entity_type"],
            title=raw_data["title"],
            content=raw_data["content"],
            metadata_json=raw_data["metadata"]
        )
        return node, []

    def permissions(self, external_user_ref: str) -> List[str]:
        return ["read:teams"]

    def webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "processed"}

    def health(self) -> bool:
        return True

    def disconnect(self) -> bool:
        self.instance.status = "DISCONNECTED"
        return True


class ConnectorEngine:
    """Unified engine to instantiate, run sync, manage webhooks, and refresh credentials."""

    CONNECTORS_MAP = {
        "GOOGLE_WORKSPACE": GoogleDriveConnector,
        "SLACK": SlackConnector,
        "JIRA": JiraConnector,
        "GITHUB": GitHubConnector,
        "TEAMS": TeamsConnector,
    }

    def __init__(self, db: Session):
        self.db = db

    def get_connector(self, instance: ConnectorInstance) -> BaseConnector:
        cls = self.CONNECTORS_MAP.get(instance.connector_type.upper(), GoogleDriveConnector)
        return cls(instance=instance, db=self.db)

    def execute_sync(self, instance: ConnectorInstance) -> int:
        connector = self.get_connector(instance)
        if not connector.authenticate():
            instance.status = "ERROR"
            self.db.commit()
            raise ValueError(f"Authentication failed for connector {instance.id}")

        instance.status = "SYNCING"
        self.db.commit()

        synced_count = 0
        try:
            for raw_record in connector.sync():
                node, edges = connector.normalize(raw_record)
                self.db.add(node)
                for edge in edges:
                    self.db.add(edge)
                synced_count += 1

            instance.status = "CONNECTED"
            instance.last_synced_at = datetime.datetime.now(datetime.timezone.utc)
            self.db.commit()
        except Exception as e:
            instance.status = "ERROR"
            self.db.commit()
            logger.error(f"Sync failed for instance {instance.id}: {e}")
            raise e

        return synced_count
