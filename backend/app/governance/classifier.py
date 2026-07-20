import re
from typing import Dict, Any, List

class DataClassifier:
    """Automatic PII, Secret, and Sensitive Data Classification Engine."""

    PII_PATTERNS = {
        "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "PHONE": r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        "SSN": r'\b\d{3}-\d{2}-\d{4}\b',
        "CREDIT_CARD": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        "API_KEY": r'\b(?:sk-[A-Za-z0-9]{20,}|ak_[A-Za-z0-9]{20,}|AIzaSy[A-Za-z0-9_-]{33})\b',
        "PASSWORD_FIELD": r'(?i)\b(?:password|passwd|secret_key)\s*[:=]\s*["\']?[^\s"\'\`]+["\']?'
    }

    def scan_and_classify(self, content: str) -> Dict[str, Any]:
        detected_findings: List[Dict[str, str]] = []

        for ptype, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, content)
            if matches:
                detected_findings.append({
                    "type": ptype,
                    "count": len(matches),
                    "sample": matches[0][:8] + "..." if len(matches[0]) > 8 else matches[0]
                })

        # Determine classification level based on findings
        classification = "INTERNAL"
        if any(f["type"] in ["SSN", "CREDIT_CARD", "API_KEY"] for f in detected_findings):
            classification = "RESTRICTED"
        elif any(f["type"] in ["EMAIL", "PHONE"] for f in detected_findings):
            classification = "CONFIDENTIAL"
        elif "top secret" in content.lower():
            classification = "TOP_SECRET"
        elif "public" in content.lower():
            classification = "PUBLIC"

        return {
            "classification": classification,
            "has_pii": len(detected_findings) > 0,
            "findings": detected_findings
        }


data_classifier = DataClassifier()
