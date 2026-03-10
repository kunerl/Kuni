"""SharePoint-Datentransfer-Modul via Microsoft Graph API."""

import os
from dataclasses import dataclass, field
from datetime import datetime

import msal
import requests


@dataclass
class SharePointConfig:
    """Konfiguration für die SharePoint-Verbindung."""

    client_id: str = ""
    client_secret: str = ""
    tenant_id: str = ""
    site_url: str = ""  # z.B. "contoso.sharepoint.com:/sites/MeineSite"

    @classmethod
    def from_env(cls) -> "SharePointConfig":
        """Lädt die Konfiguration aus Umgebungsvariablen."""
        return cls(
            client_id=os.environ.get("MS365_CLIENT_ID", ""),
            client_secret=os.environ.get("MS365_CLIENT_SECRET", ""),
            tenant_id=os.environ.get("MS365_TENANT_ID", ""),
            site_url=os.environ.get("MS365_SITE_URL", ""),
        )

    @property
    def is_configured(self) -> bool:
        return all([self.client_id, self.client_secret, self.tenant_id, self.site_url])


@dataclass
class FileActivity:
    """Eine einzelne Dateiaktivität auf SharePoint."""

    name: str
    path: str
    action: str  # "erstellt", "geändert", "gelöscht"
    modified_by: str
    modified_at: datetime
    size: int = 0
    web_url: str = ""


@dataclass
class SharePointTransferReport:
    """Bericht über SharePoint-Datentransfers."""

    site_name: str = ""
    site_url: str = ""
    activities: list[FileActivity] = field(default_factory=list)
    total_files: int = 0
    total_size_bytes: int = 0
    last_sync: datetime | None = None
    error: str = ""


class SharePointClient:
    """Client für die SharePoint-Integration via Microsoft Graph API."""

    GRAPH_BASE = "https://graph.microsoft.com/v1.0"
    SCOPE = ["https://graph.microsoft.com/.default"]

    def __init__(self, config: SharePointConfig):
        self.config = config
        self._token: str | None = None

    def _get_token(self) -> str:
        """Holt ein Access-Token via Client Credentials Flow."""
        if self._token:
            return self._token

        authority = f"https://login.microsoftonline.com/{self.config.tenant_id}"
        app = msal.ConfidentialClientApplication(
            self.config.client_id,
            authority=authority,
            client_credential=self.config.client_secret,
        )

        result = app.acquire_token_for_client(scopes=self.SCOPE)
        if "access_token" not in result:
            error_desc = result.get("error_description", "Unbekannter Fehler")
            raise RuntimeError(f"Token-Fehler: {error_desc}")

        self._token = result["access_token"]
        return self._token

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

    def _get_site_id(self) -> str:
        """Ermittelt die Site-ID aus der konfigurierten Site-URL."""
        url = f"{self.GRAPH_BASE}/sites/{self.config.site_url}"
        resp = requests.get(url, headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()["id"]

    def get_recent_activities(self, limit: int = 50) -> SharePointTransferReport:
        """Holt die letzten Dateiaktivitäten vom SharePoint-Drive."""
        report = SharePointTransferReport(last_sync=datetime.now())

        try:
            site_id = self._get_site_id()

            # Site-Infos laden
            site_url = f"{self.GRAPH_BASE}/sites/{site_id}"
            site_resp = requests.get(site_url, headers=self._headers(), timeout=30)
            site_resp.raise_for_status()
            site_data = site_resp.json()
            report.site_name = site_data.get("displayName", "Unbekannt")
            report.site_url = site_data.get("webUrl", "")

            # Standard-Drive-ID holen
            drives_url = f"{self.GRAPH_BASE}/sites/{site_id}/drives"
            drives_resp = requests.get(
                drives_url, headers=self._headers(), timeout=30
            )
            drives_resp.raise_for_status()
            drives = drives_resp.json().get("value", [])
            if not drives:
                report.error = "Keine Dokumentbibliothek gefunden."
                return report

            drive_id = drives[0]["id"]

            # Letzte Änderungen via Delta-Query
            delta_url = (
                f"{self.GRAPH_BASE}/drives/{drive_id}/root/delta"
                f"?$top={limit}&$orderby=lastModifiedDateTime desc"
            )
            delta_resp = requests.get(
                delta_url, headers=self._headers(), timeout=30
            )
            delta_resp.raise_for_status()
            items = delta_resp.json().get("value", [])

            for item in items:
                # Ordner überspringen
                if "folder" in item:
                    continue

                name = item.get("name", "Unbekannt")
                path = item.get("parentReference", {}).get("path", "")
                # Pfad bereinigen
                if "/root:" in path:
                    path = path.split("/root:")[-1]
                elif "/root" in path:
                    path = "/"
                full_path = f"{path}/{name}" if path else f"/{name}"

                size = item.get("size", 0)
                web_url = item.get("webUrl", "")

                # Aktion bestimmen
                if item.get("deleted"):
                    action = "gelöscht"
                elif item.get("createdDateTime") == item.get("lastModifiedDateTime"):
                    action = "erstellt"
                else:
                    action = "geändert"

                # Benutzer ermitteln
                modified_by_data = item.get("lastModifiedBy", {}).get("user", {})
                modified_by = modified_by_data.get(
                    "displayName", modified_by_data.get("email", "Unbekannt")
                )

                # Zeitstempel parsen
                modified_str = item.get("lastModifiedDateTime", "")
                try:
                    modified_at = datetime.fromisoformat(
                        modified_str.replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    modified_at = datetime.now()

                report.activities.append(
                    FileActivity(
                        name=name,
                        path=full_path,
                        action=action,
                        modified_by=modified_by,
                        modified_at=modified_at,
                        size=size,
                        web_url=web_url,
                    )
                )

            report.total_files = len(report.activities)
            report.total_size_bytes = sum(a.size for a in report.activities)

        except requests.exceptions.RequestException as e:
            report.error = f"API-Fehler: {e}"
        except RuntimeError as e:
            report.error = str(e)

        return report


def get_demo_report() -> SharePointTransferReport:
    """Erzeugt einen Demo-Bericht wenn keine MS365-Credentials konfiguriert sind."""
    return SharePointTransferReport(
        site_name="Demo SharePoint Site",
        site_url="https://example.sharepoint.com/sites/demo",
        activities=[
            FileActivity(
                name="Quartalsbericht_Q1_2026.xlsx",
                path="/Dokumente/Berichte/Quartalsbericht_Q1_2026.xlsx",
                action="geändert",
                modified_by="Max Mustermann",
                modified_at=datetime(2026, 3, 10, 14, 30),
                size=245_760,
                web_url="https://example.sharepoint.com/sites/demo/Dokumente/Berichte/Quartalsbericht_Q1_2026.xlsx",
            ),
            FileActivity(
                name="Projektplan_2026.pptx",
                path="/Dokumente/Projekte/Projektplan_2026.pptx",
                action="erstellt",
                modified_by="Anna Schmidt",
                modified_at=datetime(2026, 3, 10, 11, 15),
                size=1_048_576,
                web_url="https://example.sharepoint.com/sites/demo/Dokumente/Projekte/Projektplan_2026.pptx",
            ),
            FileActivity(
                name="Meetingnotizen_09-03.docx",
                path="/Dokumente/Meetings/Meetingnotizen_09-03.docx",
                action="geändert",
                modified_by="Max Mustermann",
                modified_at=datetime(2026, 3, 9, 16, 45),
                size=52_224,
                web_url="https://example.sharepoint.com/sites/demo/Dokumente/Meetings/Meetingnotizen_09-03.docx",
            ),
            FileActivity(
                name="Budget_Alt.xlsx",
                path="/Dokumente/Finanzen/Budget_Alt.xlsx",
                action="gelöscht",
                modified_by="Anna Schmidt",
                modified_at=datetime(2026, 3, 9, 10, 0),
                size=102_400,
                web_url="",
            ),
            FileActivity(
                name="Logo_Neu.png",
                path="/Dokumente/Marketing/Logo_Neu.png",
                action="erstellt",
                modified_by="Tom Weber",
                modified_at=datetime(2026, 3, 8, 9, 20),
                size=512_000,
                web_url="https://example.sharepoint.com/sites/demo/Dokumente/Marketing/Logo_Neu.png",
            ),
        ],
        total_files=5,
        total_size_bytes=1_960_960,
        last_sync=datetime(2026, 3, 10, 15, 0),
    )
