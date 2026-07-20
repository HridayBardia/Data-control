import datetime
from typing import Dict, Any, List, Tuple

class PolicyRule:
    def __init__(self, rule_id: str, name: str, condition_type: str, config: Dict[str, Any]):
        self.rule_id = rule_id
        self.name = name
        self.condition_type = condition_type
        self.config = config


class EnterprisePolicyEngine:
    """Enterprise Policy Evaluator & Dry-Run Policy Simulator."""

    def __init__(self):
        self.active_policies: List[PolicyRule] = [
            PolicyRule("p1", "Finance Dept Only", "DEPARTMENT_MATCH", {"allowed_department": "Finance"}),
            PolicyRule("p2", "Business Hours Only", "TIME_WINDOW", {"start_hour": 0, "end_hour": 24}),
            PolicyRule("p3", "No RESTRICTED AI Access", "CLASSIFICATION_DENY", {"denied_classifications": ["RESTRICTED", "TOP_SECRET"]})
        ]

    def simulate_policy(self, user_context: Dict[str, Any], action: str, resource_metadata: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        is_allowed = True

        for policy in self.active_policies:
            passed = True
            reason = "Policy criteria satisfied"

            if policy.condition_type == "DEPARTMENT_MATCH":
                req_dept = policy.config.get("allowed_department")
                user_dept = user_context.get("department")
                if req_dept and user_dept != req_dept:
                    passed = False
                    reason = f"User department '{user_dept}' does not match required '{req_dept}'"

            elif policy.condition_type == "TIME_WINDOW":
                now_hour = datetime.datetime.now(datetime.timezone.utc).hour
                sh = policy.config.get("start_hour", 0)
                eh = policy.config.get("end_hour", 24)
                if not (sh <= now_hour <= eh):
                    passed = False
                    reason = f"Current UTC hour ({now_hour}) outside allowed window ({sh}:00 - {eh}:00)"

            elif policy.condition_type == "CLASSIFICATION_DENY":
                classification = resource_metadata.get("classification", "INTERNAL")
                denied = policy.config.get("denied_classifications", [])
                if classification in denied:
                    passed = False
                    reason = f"Resource classification '{classification}' is denied by policy"

            if not passed:
                is_allowed = False

            results.append({
                "policy_id": policy.rule_id,
                "policy_name": policy.name,
                "passed": passed,
                "reason": reason
            })

        return {
            "allowed": is_allowed,
            "simulated_action": action,
            "evaluated_policies": len(results),
            "policy_results": results
        }


policy_engine = EnterprisePolicyEngine()
