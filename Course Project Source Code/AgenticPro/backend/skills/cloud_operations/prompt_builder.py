class CloudOpsPromptBuilder:
    """
    Builds structured diagnostic and remediation prompts for Cloud Operations.
    """

    def build(
        self,
        service_name: str,
        environment: str,
        deployment_target: str,
        raw_logs: str,
        deployment_config: str | None = None,
        incident_type: str | None = None,
    ) -> str:
        config_context = f"\n\nCURRENT DEPLOYMENT CONFIGURATION:\n```\n{deployment_config}\n```" if deployment_config else ""
        incident_context = f"\nINCIDENT TYPE HINT: {incident_type}" if incident_type else ""

        return f"""You are a Principal Cloud Site Reliability Engineer (SRE) and DevOps Architect.
Analyze the following deployment failure incident and formulate an actionable diagnosis, root cause analysis (RCA), step-by-step remediation plan, and code/config patch.

SERVICE: {service_name}
ENVIRONMENT: {environment}
DEPLOYMENT TARGET: {deployment_target}{incident_context}

RAW DEPLOYMENT & CRASH LOGS:
```
{raw_logs}
```{config_context}

Respond ONLY with a valid JSON object matching this schema:
{{
  "rca": {{
    "summary": "Executive summary of why the deployment crashed",
    "error_category": "OOMKilled | CrashLoopBackOff | ConfigMissing | PortConflict | MigrationError | IAMForbidden | ImagePullError",
    "severity": "Low | Medium | High | Critical",
    "failing_service": "{service_name}",
    "triggering_event": "Exact error log line or signal that initiated crash",
    "affected_dependencies": ["list", "of", "services"]
  }},
  "remediation_steps": [
    {{
      "step_number": 1,
      "action": "Imperative action name",
      "explanation": "Why this fixes the problem",
      "command_or_snippet": "CLI command or patch snippet",
      "risk_level": "Low | Medium | High",
      "is_automated": true
    }}
  ],
  "patches": [
    {{
      "filename": "k8s-deployment.yaml or Dockerfile",
      "file_type": "yaml | dockerfile | json | env",
      "original_snippet": "Faulty section of configuration",
      "patched_snippet": "Corrected section with fix applied",
      "diff_patch": "unified diff string"
    }}
  ],
  "verification_steps": [
    "Run kubectl rollout status...",
    "Check memory consumption below 80% threshold"
  ],
  "preventive_recommendations": [
    "Set up pod autoscaling (HPA)",
    "Implement automated liveness probe tuning"
  ]
}}
"""
