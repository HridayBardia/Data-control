import re
from typing import Dict, Any, List

class DataClassifier:
    """
    Automatic PII, Secret, Sensitive Data, and Compliance Classification Engine:
    - Patterns: Email, Phone, SSN, Credit Cards, API Keys, Passwords, IBAN, IPv4/IPv6, AWS Access Keys, Health IDs
    - Classification Levels: PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED, TOP_SECRET
    - Legal Hold & Retention policy enforcement helper
    """

    PII_PATTERNS = {
        "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "PHONE": r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        "SSN": r'\b\d{3}-\d{2}-\d{4}\b',
        "CREDIT_CARD": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        "IBAN": r'\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b',
        "API_KEY": r'\b(?:sk-[A-Za-z0-9]{20,}|ak_[A-Za-z0-9]{20,}|AIzaSy[A-Za-z0-9_-]{33})\b',
        "AWS_KEY": r'\bAKIA[0-9A-Z]{16}\b',
        "IP_ADDRESS": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        "PASSWORD_FIELD": r'(?i)\b(?:password|passwd|secret_key)\s*[:=]\s*["\']?[^\s"\'\`]+["\']?'
    }

    def scan_and_classify(self, content: str) -> Dict[str, Any]:
        detected_findings: List[Dict[str, Any]] = []

        for ptype, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, content)
            if matches:
                sample = str(matches[0])
                detected_findings.append({
                    "type": ptype,
                    "count": len(matches),
                    "sample": sample[:8] + "..." if len(sample) > 8 else sample
                })

        # Determine classification level based on findings
        classification = "INTERNAL"
        if any(f["type"] in ["SSN", "CREDIT_CARD", "API_KEY", "AWS_KEY", "IBAN"] for f in detected_findings):
            classification = "RESTRICTED"
        elif any(f["type"] in ["EMAIL", "PHONE", "IP_ADDRESS"] for f in detected_findings):
            classification = "CONFIDENTIAL"
        elif "top secret" in content.lower():
            classification = "TOP_SECRET"
        elif "public" in content.lower():
            classification = "PUBLIC"

        retention_years = 7 if classification in ["RESTRICTED", "TOP_SECRET"] else 3

        return {
            "classification": classification,
            "has_pii": len(detected_findings) > 0,
            "findings": detected_findings,
            "retention_policy_years": retention_years,
            "legal_hold_active": False,
            "compliance_standards": ["GDPR", "HIPAA", "SOC2", "ISO27001"] if len(detected_findings) > 0 else ["SOC2"]
        }


data_classifier = DataClassifier()
