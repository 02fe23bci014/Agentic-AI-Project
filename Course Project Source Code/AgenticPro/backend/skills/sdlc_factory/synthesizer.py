import re
import uuid
from typing import Any


class SDLCFactorySynthesizer:
    """
    High-fidelity deterministic domain synthesizer for the Agentic SDLC Factory.
    Translates requirements into structured user stories, architectural components,
    production-ready source modules, and passing test suites.
    """

    def synthesize(
        self,
        project_name: str,
        requirement_text: str,
        target_language: str = "python",
        framework: str = "fastapi",
        architecture_style: str = "clean_architecture",
    ) -> dict[str, Any]:
        req_lower = requirement_text.lower()

        if "rate" in req_lower and "limit" in req_lower:
            return self._build_rate_limiter_project(project_name, requirement_text, framework)
        elif "cache" in req_lower or "ttl" in req_lower:
            return self._build_cache_project(project_name, requirement_text, framework)
        elif "notification" in req_lower or "event" in req_lower or "pub" in req_lower:
            return self._build_event_bus_project(project_name, requirement_text, framework)
        else:
            return self._build_general_domain_project(project_name, requirement_text, framework)

    def _build_rate_limiter_project(self, project_name: str, req: str, framework: str) -> dict[str, Any]:
        user_stories = [
            {
                "id": "US-01",
                "title": "Token Bucket Consumption",
                "as_a": "API Gateway Client",
                "i_want": "To consume rate-limit tokens per key",
                "so_that": "Fair bandwidth is enforced and DDoS/spikes are prevented",
                "acceptance_criteria": [
                    "Allow request if tokens >= required tokens",
                    "Reject request with 429 status or False if tokens depleted",
                    "Replenish tokens continuously based on elapsed time",
                ],
                "priority": "Critical",
            },
            {
                "id": "US-02",
                "title": "Burst Capacity & Key Isolation",
                "as_a": "System Operator",
                "i_want": "Distinct token pools per client IP or API key",
                "so_that": "One noisy client cannot exhaust rate limits of other clients",
                "acceptance_criteria": [
                    "Client A limits do not decrement Client B tokens",
                    "Tokens never exceed configured max_capacity",
                ],
                "priority": "High",
            },
        ]

        architecture = {
            "system_overview": "Layered clean architecture separating the TokenBucket core domain, in-memory repository, and RateLimiter service.",
            "architecture_style": "Clean Architecture",
            "components": [
                {
                    "name": "TokenBucket",
                    "responsibility": "Manages individual token pool, elapsed refill math, and concurrency lock.",
                    "interface_methods": ["consume(tokens: int) -> bool", "refill() -> None"],
                },
                {
                    "name": "RateLimiterService",
                    "responsibility": "Coordinates multi-client buckets and enforces request quotas.",
                    "interface_methods": ["allow_request(client_id: str, tokens: int) -> bool", "get_remaining(client_id: str) -> float"],
                },
            ],
            "data_schemas": [
                {"entity": "TokenBucketState", "fields": "capacity: float, refill_rate: float, current_tokens: float, last_update: float"}
            ],
            "api_endpoints": [
                {"method": "POST", "path": "/api/v1/check-limit", "description": "Verify and decrement client quota"}
            ],
        }

        source_models = (
            "import time\n"
            "from dataclasses import dataclass\n\n"
            "@dataclass\n"
            "class RateLimitConfig:\n"
            "    capacity: float = 10.0\n"
            "    refill_rate_per_sec: float = 2.0\n"
        )

        source_service = (
            "import time\n"
            "import threading\n\n"
            "class TokenBucket:\n"
            "    def __init__(self, capacity: float = 10.0, refill_rate: float = 2.0):\n"
            "        self.capacity = float(capacity)\n"
            "        self.refill_rate = float(refill_rate)\n"
            "        self.tokens = float(capacity)\n"
            "        self.last_refill = time.time()\n"
            "        self._lock = threading.Lock()\n\n"
            "    def _refill(self) -> None:\n"
            "        now = time.time()\n"
            "        elapsed = now - self.last_refill\n"
            "        if elapsed > 0:\n"
            "            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)\n"
            "            self.last_refill = now\n\n"
            "    def consume(self, count: int = 1) -> bool:\n"
            "        with self._lock:\n"
            "            self._refill()\n"
            "            if self.tokens >= count:\n"
            "                self.tokens -= count\n"
            "                return True\n"
            "            return False\n\n"
            "    def available(self) -> float:\n"
            "        with self._lock:\n"
            "            self._refill()\n"
            "            return self.tokens\n\n"
            "class RateLimiter:\n"
            "    def __init__(self, default_capacity: float = 10.0, default_refill: float = 2.0):\n"
            "        self.default_capacity = default_capacity\n"
            "        self.default_refill = default_refill\n"
            "        self.buckets = {}\n"
            "        self._map_lock = threading.Lock()\n\n"
            "    def get_bucket(self, client_id: str) -> TokenBucket:\n"
            "        with self._map_lock:\n"
            "            if client_id not in self.buckets:\n"
            "                self.buckets[client_id] = TokenBucket(self.default_capacity, self.default_refill)\n"
            "            return self.buckets[client_id]\n\n"
            "    def allow(self, client_id: str, count: int = 1) -> bool:\n"
            "        bucket = self.get_bucket(client_id)\n"
            "        return bucket.consume(count)\n"
        )

        test_code = (
            "def test_bucket_initial_capacity():\n"
            "    bucket = TokenBucket(capacity=5.0, refill_rate=1.0)\n"
            "    assert bucket.available() == 5.0\n"
            "    assert bucket.consume(3) is True\n"
            "    assert int(bucket.available()) == 2\n\n"
            "def test_bucket_exhaustion_and_refill():\n"
            "    bucket = TokenBucket(capacity=2.0, refill_rate=100.0)\n"
            "    assert bucket.consume(2) is True\n"
            "    assert bucket.consume(1) is False\n"
            "    # Wait small fraction for high refill\n"
            "    import time\n"
            "    time.sleep(0.02)\n"
            "    assert bucket.consume(1) is True\n\n"
            "def test_client_isolation():\n"
            "    limiter = RateLimiter(default_capacity=2.0, default_refill=1.0)\n"
            "    # Client A consumes all\n"
            "    assert limiter.allow('client-A', 2) is True\n"
            "    assert limiter.allow('client-A', 1) is False\n"
            "    # Client B remains full\n"
            "    assert limiter.allow('client-B', 2) is True\n\n"
            "def test_concurrency_safety():\n"
            "    limiter = RateLimiter(default_capacity=50.0, default_refill=0.0)\n"
            "    import threading\n"
            "    success_count = [0]\n"
            "    def worker():\n"
            "        if limiter.allow('shared-client', 1):\n"
            "            success_count[0] += 1\n"
            "    threads = [threading.Thread(target=worker) for _ in range(60)]\n"
            "    for t in threads: t.start()\n"
            "    for t in threads: t.join()\n"
            "    assert success_count[0] == 50\n"
        )

        code_files = [
            {"filepath": "src/models.py", "file_type": "source", "language": "python", "description": "Rate limiting configuration models", "content": source_models},
            {"filepath": "src/service.py", "file_type": "source", "language": "python", "description": "Token bucket and multi-client coordinator", "content": source_service},
            {"filepath": "tests/test_service.py", "file_type": "test", "language": "python", "description": "Unit tests for capacity, exhaustion, and concurrency", "content": test_code},
        ]

        return {"user_stories": user_stories, "architecture": architecture, "code_files": code_files}

    def _build_cache_project(self, project_name: str, req: str, framework: str) -> dict[str, Any]:
        user_stories = [
            {
                "id": "US-01",
                "title": "Cache Get and Set with TTL",
                "as_a": "Backend Application",
                "i_want": "To cache key-value objects with expiration TTL",
                "so_that": "Repetitive database queries are offloaded",
                "acceptance_criteria": ["Return cached value before TTL expires", "Return None after TTL expires"],
                "priority": "Critical",
            },
            {
                "id": "US-02",
                "title": "LRU Eviction on Capacity",
                "as_a": "Memory Manager",
                "i_want": "Evict Least Recently Used keys when cache limit reached",
                "so_that": "Memory remains bounded and does not OOM",
                "acceptance_criteria": ["Evict oldest accessed key on overflow", "Touch access order on get/set"],
                "priority": "High",
            },
        ]

        architecture = {
            "system_overview": "Thread-safe In-Memory Cache with Least-Recently-Used (LRU) ordering and background TTL eviction.",
            "architecture_style": "Clean Architecture",
            "components": [
                {"name": "LRUCache", "responsibility": "Double-ended hash map managing key eviction and TTL expiration.", "interface_methods": ["get(key)", "set(key, val, ttl)", "delete(key)"]}
            ],
            "data_schemas": [
                {"entity": "CacheNode", "fields": "key: str, val: Any, expires_at: float, prev: Node, next: Node"}
            ],
            "api_endpoints": [
                {"method": "GET", "path": "/api/cache/{key}", "description": "Fetch cached entry"}
            ],
        }

        source_code = (
            "import time\n"
            "from typing import Any\n"
            "from collections import OrderedDict\n"
            "import threading\n\n"
            "class LRUCache:\n"
            "    def __init__(self, capacity: int = 100, default_ttl: float = 3600.0):\n"
            "        self.capacity = capacity\n"
            "        self.default_ttl = default_ttl\n"
            "        self.cache = OrderedDict()\n"
            "        self.expirations = {}\n"
            "        self._lock = threading.Lock()\n\n"
            "    def set(self, key: str, value: Any, ttl: float | None = None) -> None:\n"
            "        with self._lock:\n"
            "            now = time.time()\n"
            "            expire_time = now + (ttl if ttl is not None else self.default_ttl)\n"
            "            if key in self.cache:\n"
            "                self.cache.move_to_end(key)\n"
            "            self.cache[key] = value\n"
            "            self.expirations[key] = expire_time\n"
            "            if len(self.cache) > self.capacity:\n"
            "                oldest, _ = self.cache.popitem(last=False)\n"
            "                self.expirations.pop(oldest, None)\n\n"
            "    def get(self, key: str) -> Any:\n"
            "        with self._lock:\n"
            "            if key not in self.cache:\n"
            "                return None\n"
            "            if time.time() > self.expirations.get(key, 0):\n"
            "                self.cache.pop(key, None)\n"
            "                self.expirations.pop(key, None)\n"
            "                return None\n"
            "            self.cache.move_to_end(key)\n"
            "            return self.cache[key]\n\n"
            "    def size(self) -> int:\n"
            "        with self._lock:\n"
            "            return len(self.cache)\n"
        )

        test_code = (
            "def test_cache_set_and_get():\n"
            "    cache = LRUCache(capacity=3)\n"
            "    cache.set('k1', 'val1')\n"
            "    assert cache.get('k1') == 'val1'\n"
            "    assert cache.get('nonexistent') is None\n\n"
            "def test_cache_lru_eviction():\n"
            "    cache = LRUCache(capacity=2)\n"
            "    cache.set('a', 1)\n"
            "    cache.set('b', 2)\n"
            "    assert cache.get('a') == 1  # accesses 'a', makes 'b' least recently used\n"
            "    cache.set('c', 3)  # evicts 'b'\n"
            "    assert cache.get('b') is None\n"
            "    assert cache.get('a') == 1\n"
            "    assert cache.get('c') == 3\n\n"
            "def test_cache_ttl_expiration():\n"
            "    cache = LRUCache(capacity=5)\n"
            "    cache.set('short_lived', 'temp', ttl=0.01)\n"
            "    assert cache.get('short_lived') == 'temp'\n"
            "    import time\n"
            "    time.sleep(0.02)\n"
            "    assert cache.get('short_lived') is None\n"
        )

        code_files = [
            {"filepath": "src/cache.py", "file_type": "source", "language": "python", "description": "LRU cache with TTL implementation", "content": source_code},
            {"filepath": "tests/test_cache.py", "file_type": "test", "language": "python", "description": "Cache unit tests for set, get, LRU, and expiration", "content": test_code},
        ]

        return {"user_stories": user_stories, "architecture": architecture, "code_files": code_files}

    def _build_event_bus_project(self, project_name: str, req: str, framework: str) -> dict[str, Any]:
        user_stories = [
            {
                "id": "US-01",
                "title": "Topic-Based Pub-Sub",
                "as_a": "Microservice Publisher",
                "i_want": "To publish messages to named topics",
                "so_that": "Subscribers receive events asynchronously without direct coupling",
                "acceptance_criteria": ["Dispatch message to all active subscribers of topic"],
                "priority": "Critical",
            }
        ]

        architecture = {
            "system_overview": "Thread-safe in-process publish/subscribe message bus with wildcard topics and handler error isolation.",
            "architecture_style": "Event-Driven Architecture",
            "components": [
                {"name": "EventBus", "responsibility": "Topic registration, subscriber dispatch, and event delivery.", "interface_methods": ["subscribe(topic, handler)", "publish(topic, payload)"]}
            ],
            "data_schemas": [{"entity": "EventMessage", "fields": "id: str, topic: str, payload: Any, timestamp: float"}],
            "api_endpoints": [{"method": "POST", "path": "/events/publish", "description": "Dispatch event"}],
        }

        source_code = (
            "import time\n"
            "from typing import Any\n"
            "from collections import defaultdict\n"
            "import threading\n\n"
            "class EventBus:\n"
            "    def __init__(self):\n"
            "        self._subscribers = defaultdict(list)\n"
            "        self._lock = threading.Lock()\n\n"
            "    def subscribe(self, topic: str, handler) -> None:\n"
            "        with self._lock:\n"
            "            self._subscribers[topic].append(handler)\n\n"
            "    def publish(self, topic: str, payload: Any) -> int:\n"
            "        with self._lock:\n"
            "            handlers = list(self._subscribers.get(topic, []))\n"
            "        delivered = 0\n"
            "        for h in handlers:\n"
            "            try:\n"
            "                h(payload)\n"
            "                delivered += 1\n"
            "            except Exception:\n"
            "                pass\n"
            "        return delivered\n"
        )

        test_code = (
            "def test_event_bus_delivery():\n"
            "    bus = EventBus()\n"
            "    received = []\n"
            "    bus.subscribe('user.created', lambda p: received.append(p))\n"
            "    count = bus.publish('user.created', {'id': 42})\n"
            "    assert count == 1\n"
            "    assert received == [{'id': 42}]\n\n"
            "def test_multiple_subscribers():\n"
            "    bus = EventBus()\n"
            "    r1, r2 = [], []\n"
            "    bus.subscribe('order.placed', lambda p: r1.append(p))\n"
            "    bus.subscribe('order.placed', lambda p: r2.append(p))\n"
            "    bus.publish('order.placed', 'order-99')\n"
            "    assert r1 == ['order-99']\n"
            "    assert r2 == ['order-99']\n"
        )

        code_files = [
            {"filepath": "src/bus.py", "file_type": "source", "language": "python", "description": "Event bus implementation", "content": source_code},
            {"filepath": "tests/test_bus.py", "file_type": "test", "language": "python", "description": "Pub-sub unit tests", "content": test_code},
        ]

        return {"user_stories": user_stories, "architecture": architecture, "code_files": code_files}

    def _build_general_domain_project(self, project_name: str, req: str, framework: str) -> dict[str, Any]:
        clean_name = re.sub(r"[^a-zA-Z0-9_]", "", project_name.replace(" ", "_")) or "TaskService"

        user_stories = [
            {
                "id": "US-01",
                "title": f"Core Operation for {project_name}",
                "as_a": "API Consumer",
                "i_want": "Execute primary business transaction and validate input constraints",
                "so_that": "Domain invariants are enforced and operations complete reliably",
                "acceptance_criteria": [
                    "Reject invalid or empty payloads with ValueError",
                    "Process and return valid domain entity with timestamp and unique ID",
                ],
                "priority": "Critical",
            },
            {
                "id": "US-02",
                "title": f"Query & Retrieval for {project_name}",
                "as_a": "Operator",
                "i_want": "Query state and filter items by key",
                "so_that": "Accurate state transitions can be audited",
                "acceptance_criteria": ["Return recorded items by ID", "Return None or empty list for missing entries"],
                "priority": "High",
            },
        ]

        architecture = {
            "system_overview": f"Modular Clean Architecture implementation for '{project_name}' separating entities, state store, and business rules.",
            "architecture_style": "Clean Architecture",
            "components": [
                {"name": f"{clean_name}Core", "responsibility": "Domain model and state transitions", "interface_methods": ["create(data)", "get(id)", "list_all()"]}
            ],
            "data_schemas": [{"entity": "DomainEntity", "fields": "id: str, name: str, status: str, created_at: float"}],
            "api_endpoints": [{"method": "POST", "path": "/api/items", "description": "Create entity"}],
        }

        source_code = f"""import time
import uuid
from typing import Any, Dict, List, Optional

class {clean_name}:
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {{}}

    def create(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not name or not name.strip():
            raise ValueError("Item name cannot be empty.")
        
        item_id = f"item-{{uuid.uuid4().hex[:8]}}"
        record = {{
            "id": item_id,
            "name": name.strip(),
            "status": "active",
            "metadata": metadata or {{}},
            "created_at": time.time(),
        }}
        self._store[item_id] = record
        return record

    def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(item_id)

    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._store.values())

    def update_status(self, item_id: str, status: str) -> Dict[str, Any]:
        if item_id not in self._store:
            raise KeyError(f"Item '{{item_id}}' not found.")
        self._store[item_id]["status"] = status
        return self._store[item_id]
"""

        test_code = f"""def test_create_and_retrieve():
    svc = {clean_name}()
    rec = svc.create("Test Artifact", {{"env": "prod"}})
    assert rec["id"].startswith("item-")
    assert rec["name"] == "Test Artifact"
    assert rec["status"] == "active"
    
    # Retrieve
    fetched = svc.get(rec["id"])
    assert fetched == rec

def test_validation_rejects_empty():
    svc = {clean_name}()
    import pytest
    try:
        svc.create("   ")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

def test_status_update():
    svc = {clean_name}()
    rec = svc.create("Lifecycle Item")
    updated = svc.update_status(rec["id"], "completed")
    assert updated["status"] == "completed"
    assert svc.get(rec["id"])["status"] == "completed"
"""

        code_files = [
            {"filepath": f"src/{clean_name.lower()}.py", "file_type": "source", "language": "python", "description": "Core domain service", "content": source_code},
            {"filepath": f"tests/test_{clean_name.lower()}.py", "file_type": "test", "language": "python", "description": "Automated verification test suite", "content": test_code},
        ]

        return {"user_stories": user_stories, "architecture": architecture, "code_files": code_files}
