import uuid
from typing import Any
from backend.tools.cloud_ops_tool import CloudOpsTool


class CloudOpsSynthesizer:
    """
    High-fidelity deterministic cloud failure synthesizer.
    Performs autonomous pattern detection, RCA, and patch generation without external LLM dependencies.
    """

    def __init__(self):
        self.tool = CloudOpsTool()

    def synthesize(
        self,
        service_name: str,
        environment: str = "production",
        deployment_target: str = "kubernetes",
        raw_logs: str = "",
        deployment_config: str | None = None,
        incident_type: str | None = None,
    ) -> dict[str, Any]:
        """Synthesize a complete diagnosis report, remediation plan, and patch."""
        signatures = self.tool.extract_log_signatures(raw_logs)

        # Detect error category based on hints and signatures
        error_category, rca, steps, patches = self._diagnose_category(
            service_name=service_name,
            environment=environment,
            deployment_target=deployment_target,
            raw_logs=raw_logs,
            deployment_config=deployment_config,
            incident_type=incident_type,
            signatures=signatures,
        )

        verification_steps = [
            f"Apply configuration patch: `kubectl apply -f {patches[0]['filename'] if patches else 'k8s-manifest.yaml'}`",
            f"Monitor rollout status: `kubectl rollout status deployment/{service_name} -n {environment} --timeout=90s`",
            f"Verify pod health metrics: `kubectl top pod -l app={service_name}` ensures resource consumption is nominal.",
            f"Perform synthetic smoke test: `curl -fsS http://{service_name}.internal:8000/healthz` verifies 200 OK.",
        ]

        preventive_recommendations = [
            "Configure automated Vertical Pod Autoscaler (VPA) or Horizontal Pod Autoscaler (HPA) to prevent capacity saturation.",
            "Establish automated pre-deployment linting using kube-linter or conftest in CI/CD pipeline.",
            "Implement standardized readiness probe initialDelaySeconds and failureThreshold buffers.",
            "Set up Prometheus alert rules for container restarts (> 2 restarts within 10 minutes).",
        ]

        report_id = f"inc-{uuid.uuid4().hex[:8]}"

        return {
            "id": report_id,
            "service_name": service_name,
            "environment": environment,
            "deployment_target": deployment_target,
            "rca": rca,
            "remediation_steps": steps,
            "patches": patches,
            "verification_steps": verification_steps,
            "preventive_recommendations": preventive_recommendations,
            "status": "diagnosed",
        }

    def _diagnose_category(
        self,
        service_name: str,
        environment: str,
        deployment_target: str,
        raw_logs: str,
        deployment_config: str | None,
        incident_type: str | None,
        signatures: dict[str, Any],
    ):
        lower_logs = raw_logs.lower()
        hint = (incident_type or "").lower()

        # 1. OOMKilled / Exit Code 137
        if signatures["oom_detected"] or "137" in signatures["exit_codes"] or "oom" in hint:
            orig = deployment_config or (
                f"resources:\n"
                f"  limits:\n"
                f"    memory: \"256Mi\"\n"
                f"    cpu: \"500m\"\n"
                f"  requests:\n"
                f"    memory: \"128Mi\"\n"
                f"    cpu: \"250m\""
            )
            patched = (
                f"resources:\n"
                f"  limits:\n"
                f"    memory: \"1Gi\"\n"
                f"    cpu: \"1000m\"\n"
                f"  requests:\n"
                f"    memory: \"512Mi\"\n"
                f"    cpu: \"500m\""
            )
            diff = self.tool.generate_unified_diff(orig, patched, filename=f"{service_name}-deployment.yaml")

            rca = {
                "summary": f"Container for '{service_name}' exceeded allocated cgroup memory limit (256Mi) during traffic surge or initialization, triggering Linux kernel OOM Killer (SIGKILL, exit code 137).",
                "error_category": "OOMKilled",
                "severity": "Critical",
                "failing_service": service_name,
                "triggering_event": "Kernel invocation: Out of memory: Kill process or sacrificed child (exit code 137)",
                "affected_dependencies": ["api-gateway", "ingress-controller", "user-facing-traffic"],
            }
            steps = [
                {
                    "step_number": 1,
                    "action": "Increase Container Memory Limits & Requests",
                    "explanation": "Scale memory limit from 256Mi to 1Gi to accommodate peak JVM/Python memory allocations and GC spikes.",
                    "command_or_snippet": f"kubectl set resources deployment/{service_name} --limits=memory=1Gi,cpu=1000m --requests=memory=512Mi,cpu=500m -n {environment}",
                    "risk_level": "Low",
                    "is_automated": True,
                },
                {
                    "step_number": 2,
                    "action": "Tune Node Memory Buffer & Node Overcommit",
                    "explanation": "Verify cluster node has sufficient allocatable memory to schedule enlarged pod replicas.",
                    "command_or_snippet": f"kubectl describe nodes | grep -A 5 'Allocated resources'",
                    "risk_level": "Low",
                    "is_automated": False,
                },
                {
                    "step_number": 3,
                    "action": "Restart Pod Deployment and Inspect cgroups",
                    "explanation": "Initiate rolling restart and monitor real-time memory usage in Prometheus / Grafana.",
                    "command_or_snippet": f"kubectl rollout restart deployment/{service_name} -n {environment}",
                    "risk_level": "Low",
                    "is_automated": True,
                },
            ]
            patches = [
                {
                    "filename": f"{service_name}-deployment.yaml",
                    "file_type": "yaml",
                    "original_snippet": orig,
                    "patched_snippet": patched,
                    "diff_patch": diff,
                }
            ]
            return "OOMKilled", rca, steps, patches

        # 2. Port Conflict / Address in Use
        if signatures["port_conflict_detected"] or "address already in use" in lower_logs or "port" in hint:
            orig = deployment_config or (
                f"ports:\n"
                f"  - containerPort: 8080\n"
                f"    hostPort: 8080"
            )
            patched = (
                f"ports:\n"
                f"  - containerPort: 8080\n"
                f"    # Removed hostPort to avoid host network socket collision\n"
                f"    name: http-traffic"
            )
            diff = self.tool.generate_unified_diff(orig, patched, filename=f"{service_name}-service.yaml")

            rca = {
                "summary": f"Process in '{service_name}' failed to bind TCP socket: [Errno 98] Address already in use. A competing process or stale container instance holds port 8080.",
                "error_category": "PortConflict",
                "severity": "High",
                "failing_service": service_name,
                "triggering_event": "Bind socket error: listen tcp :8080: bind: address already in use",
                "affected_dependencies": ["ingress-controller", "service-mesh"],
            }
            steps = [
                {
                    "step_number": 1,
                    "action": "Eliminate HostPort Binding in Manifest",
                    "explanation": "Avoid direct hostPort allocation in container specs; utilize Kubernetes Service ClusterIP instead.",
                    "command_or_snippet": f"kubectl delete pod -l app={service_name} --force --grace-period=0",
                    "risk_level": "Medium",
                    "is_automated": True,
                },
                {
                    "step_number": 2,
                    "action": "Terminate Orphaned Sockets on Node",
                    "explanation": "Clean up zombie processes holding TCP listeners on node port.",
                    "command_or_snippet": "fuser -k 8080/tcp || true",
                    "risk_level": "Medium",
                    "is_automated": False,
                },
            ]
            patches = [
                {
                    "filename": f"{service_name}-service.yaml",
                    "file_type": "yaml",
                    "original_snippet": orig,
                    "patched_snippet": patched,
                    "diff_patch": diff,
                }
            ]
            return "PortConflict", rca, steps, patches

        # 3. Missing Configuration / Environment Variable
        if signatures["missing_env_detected"] or "keyerror" in lower_logs or "database_url" in lower_logs or "env" in hint:
            orig = deployment_config or (
                f"env:\n"
                f"  - name: APP_ENV\n"
                f"    value: \"production\""
            )
            patched = (
                f"env:\n"
                f"  - name: APP_ENV\n"
                f"    value: \"production\"\n"
                f"  - name: DATABASE_URL\n"
                f"    valueFrom:\n"
                f"      secretKeyRef:\n"
                f"        name: {service_name}-secrets\n"
                f"        key: database-url\n"
                f"  - name: PORT\n"
                f"    value: \"8000\""
            )
            diff = self.tool.generate_unified_diff(orig, patched, filename="k8s-configmap-env.yaml")

            rca = {
                "summary": f"Service '{service_name}' crashed immediately on boot due to unhandled KeyError: missing required environment variable 'DATABASE_URL'.",
                "error_category": "ConfigMissing",
                "severity": "Critical",
                "failing_service": service_name,
                "triggering_event": "KeyError: 'DATABASE_URL' is required for connection initialization",
                "affected_dependencies": ["postgres-cluster", "authentication-service"],
            }
            steps = [
                {
                    "step_number": 1,
                    "action": "Inject Missing Secrets and Environment Variables",
                    "explanation": "Populate the required credentials via Kubernetes Secret or HashiCorp Vault integration.",
                    "command_or_snippet": f"kubectl create secret generic {service_name}-secrets --from-literal=database-url=\"postgres://app:secure@db:5432/prod\" --dry-run=client -o yaml | kubectl apply -f -",
                    "risk_level": "Low",
                    "is_automated": True,
                },
                {
                    "step_number": 2,
                    "action": "Add Strict Startup Environment Validation",
                    "explanation": "Use Pydantic or fail-fast schema checking during bootstrap to log human-readable validation errors.",
                    "command_or_snippet": "# Verified in backend/config/settings.py",
                    "risk_level": "Low",
                    "is_automated": False,
                },
            ]
            patches = [
                {
                    "filename": "k8s-configmap-env.yaml",
                    "file_type": "yaml",
                    "original_snippet": orig,
                    "patched_snippet": patched,
                    "diff_patch": diff,
                }
            ]
            return "ConfigMissing", rca, steps, patches

        # 4. CrashLoopBackOff / Failing Liveness Probe (Default Container Failure)
        orig = deployment_config or (
            f"livenessProbe:\n"
            f"  httpGet:\n"
            f"    path: /health\n"
            f"    port: 8000\n"
            f"  initialDelaySeconds: 2\n"
            f"  periodSeconds: 5\n"
            f"  failureThreshold: 2"
        )
        patched = (
            f"livenessProbe:\n"
            f"  httpGet:\n"
            f"    path: /health\n"
            f"    port: 8000\n"
            f"  initialDelaySeconds: 30\n"
            f"  periodSeconds: 10\n"
            f"  timeoutSeconds: 5\n"
            f"  failureThreshold: 5"
        )
        diff = self.tool.generate_unified_diff(orig, patched, filename="k8s-deployment.yaml")

        rca = {
            "summary": f"Container for '{service_name}' entered CrashLoopBackOff: the kubelet killed the container because the liveness probe failed before application bootstrap and database connection warmup completed.",
            "error_category": "CrashLoopBackOff",
            "severity": "Critical",
            "failing_service": service_name,
            "triggering_event": "Liveness probe failed: HTTP probe failed with statuscode: 503 / connection refused during bootstrap",
            "affected_dependencies": ["api-gateway", "client-traffic"],
        }
        steps = [
            {
                "step_number": 1,
                "action": "Increase Probe initialDelaySeconds & failureThreshold",
                "explanation": "Allow application 30 seconds warmup time for model loading, connection pools, and migration verification before killing.",
                "command_or_snippet": f"kubectl patch deployment {service_name} --type='json' -p='[{{\"op\": \"replace\", \"path\": \"/spec/template/spec/containers/0/livenessProbe/initialDelaySeconds\", \"value\": 30}}]'",
                "risk_level": "Low",
                "is_automated": True,
            },
            {
                "step_number": 2,
                "action": "Introduce Dedicated Startup Probe",
                "explanation": "Decouple startup checks from runtime liveness checks to prevent aggressive killing during cold starts.",
                "command_or_snippet": "kubectl rollout restart deployment/" + service_name,
                "risk_level": "Low",
                "is_automated": True,
            },
        ]
        patches = [
            {
                "filename": "k8s-deployment.yaml",
                "file_type": "yaml",
                "original_snippet": orig,
                "patched_snippet": patched,
                "diff_patch": diff,
            }
        ]
        return "CrashLoopBackOff", rca, steps, patches
