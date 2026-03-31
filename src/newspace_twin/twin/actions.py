from __future__ import annotations


def recommend_action(severity_class: str, risk_level: str, uncertainty_score: float) -> str:
    severity_class = (severity_class or '').lower()
    risk_level = (risk_level or '').lower()

    if risk_level == 'critical':
        return 'immediate_field_review'
    if risk_level == 'high' and uncertainty_score < 0.35:
        return 'priority_intervention'
    if risk_level == 'high' and uncertainty_score >= 0.35:
        return 'urgent_validation'
    if severity_class in {'high', 'severe'}:
        return 'targeted_monitoring'
    if risk_level == 'medium':
        return 'scheduled_monitoring'
    return 'routine_monitoring'
