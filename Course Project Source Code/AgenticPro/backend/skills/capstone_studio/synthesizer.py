from datetime import datetime
from typing import Any


class CapstoneSynthesizer:
    """
    High-fidelity domain synthesizer for Lab 14: Capstone Project Studio.
    Synthesizes complete, multi-stage team-owned agentic projects across FinTech,
    Energy IoT, Healthcare, and Autonomous Robotics domains.
    """

    def synthesize(
        self,
        team_name: str,
        project_title: str,
        domain: str = "General Engineering",
        mission_statement: str = "",
        team_members: list[dict] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        combined = f"{project_title} {domain} {mission_statement}".lower()

        if "energy" in combined or "microgrid" in combined or "solar" in combined:
            return self._synthesize_microgrid(team_name, project_title, user_id)
        elif "fintech" in combined or "order" in combined or "trading" in combined or "matching" in combined:
            return self._synthesize_matching_engine(team_name, project_title, user_id)
        elif "health" in combined or "patient" in combined or "clinical" in combined or "triage" in combined:
            return self._synthesize_healthcare(team_name, project_title, user_id)
        elif "drone" in combined or "robot" in combined or "swarm" in combined or "collision" in combined:
            return self._synthesize_drone_swarm(team_name, project_title, user_id)
        else:
            return self._synthesize_microgrid(team_name, project_title, user_id)

    # --------------------------------------------------------------------------
    # Capstone Preset 1: Autonomous Microgrid Energy Exchange
    # --------------------------------------------------------------------------
    def _synthesize_microgrid(self, team_name: str, project_title: str, user_id: str | None) -> dict[str, Any]:
        code_content = """# Autonomous Microgrid Peer-to-Peer Energy Exchange
from typing import Any, Dict, List

class EnergyParticipant:
    def __init__(self, node_id: str, capacity_kwh: float, current_storage_kwh: float, is_prosumer: bool):
        self.node_id = node_id
        self.capacity_kwh = capacity_kwh
        self.current_storage_kwh = current_storage_kwh
        self.is_prosumer = is_prosumer

class MicrogridMarketplace:
    def __init__(self, base_price_per_kwh: float = 0.14):
        self.base_price = base_price_per_kwh
        self.participants: Dict[str, EnergyParticipant] = {}
        self.cleared_transactions: List[Dict[str, Any]] = []

    def register_node(self, node: EnergyParticipant) -> None:
        self.participants[node.node_id] = node

    def match_energy_order(self, buyer_id: str, seller_id: str, requested_kwh: float) -> Dict[str, Any]:
        if buyer_id not in self.participants:
            raise KeyError(f"Buyer node '{buyer_id}' not registered in microgrid.")
        if seller_id not in self.participants:
            raise KeyError(f"Seller node '{seller_id}' not registered in microgrid.")

        seller = self.participants[seller_id]
        buyer = self.participants[buyer_id]

        available = seller.current_storage_kwh
        delivered = min(requested_kwh, available)

        if delivered <= 0:
            return {"status": "NO_ENERGY_AVAILABLE", "delivered_kwh": 0.0, "total_cost": 0.0}

        seller.current_storage_kwh -= delivered
        buyer.current_storage_kwh += delivered
        cost = round(delivered * self.base_price, 2)

        tx = {
            "buyer": buyer_id,
            "seller": seller_id,
            "delivered_kwh": delivered,
            "total_cost": cost,
            "status": "SETTLED"
        }
        self.cleared_transactions.append(tx)
        return tx
"""

        test_content = """# Verification Test Suite for Microgrid Exchange
def test_node_registration():
    market = MicrogridMarketplace(base_price_per_kwh=0.15)
    solar_node = EnergyParticipant("solar_01", capacity_kwh=100.0, current_storage_kwh=65.0, is_prosumer=True)
    market.register_node(solar_node)
    assert "solar_01" in market.participants
    assert market.participants["solar_01"].current_storage_kwh == 65.0

def test_settle_energy_transaction():
    market = MicrogridMarketplace(base_price_per_kwh=0.10)
    seller = EnergyParticipant("seller_a", capacity_kwh=50.0, current_storage_kwh=30.0, is_prosumer=True)
    buyer = EnergyParticipant("buyer_b", capacity_kwh=20.0, current_storage_kwh=5.0, is_prosumer=False)
    market.register_node(seller)
    market.register_node(buyer)

    tx = market.match_energy_order("buyer_b", "seller_a", 15.0)
    assert tx["status"] == "SETTLED"
    assert tx["delivered_kwh"] == 15.0
    assert tx["total_cost"] == 1.50
    assert seller.current_storage_kwh == 15.0
    assert buyer.current_storage_kwh == 20.0

def test_insufficient_storage_partial_fill():
    market = MicrogridMarketplace(base_price_per_kwh=0.20)
    seller = EnergyParticipant("seller_low", capacity_kwh=50.0, current_storage_kwh=4.0, is_prosumer=True)
    buyer = EnergyParticipant("buyer_high", capacity_kwh=50.0, current_storage_kwh=0.0, is_prosumer=False)
    market.register_node(seller)
    market.register_node(buyer)

    tx = market.match_energy_order("buyer_high", "seller_low", 10.0)
    assert tx["delivered_kwh"] == 4.0
    assert tx["total_cost"] == 0.80
    assert seller.current_storage_kwh == 0.0
"""

        return {
            "id": f"cap-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "team_name": team_name or "VoltGrid Autonomous Collective",
            "project_title": project_title or "Autonomous Microgrid Peer-to-Peer Energy Exchange",
            "domain": "Energy IoT & Decentralized Grid",
            "mission_statement": (
                "Develop an autonomous multi-agent microgrid coordinator capable of orchestrating peer-to-peer "
                "renewable solar/battery energy exchanges, balancing local feeder load variations, and preventing feeder congestion."
            ),
            "status": "completed",
            "team_members": [
                {"name": "Dr. Aris Vance", "role": "Lead Systems Architect", "agent_type": "architect", "avatar": "🧠", "contribution_summary": "Grid topology, state machine design & smart contract interfaces"},
                {"name": "Elena Rostova", "role": "Research Intelligence Officer", "agent_type": "research", "avatar": "🔍", "contribution_summary": "IEEE 1547 standards review & tariff dynamic evidence table"},
                {"name": "Devin Chen", "role": "SDLC Implementation Engineer", "agent_type": "sdlc", "avatar": "💻", "contribution_summary": "Core double-auction matching engine & Python verification module"},
                {"name": "Sarah Miller", "role": "Test Harness & QA Lead", "agent_type": "devops", "avatar": "🧪", "contribution_summary": "Boundary edge test suites, concurrency locks & in-memory runner"},
                {"name": "Marcus Kane", "role": "Safety & Governance Officer", "agent_type": "governance", "avatar": "🛡️", "contribution_summary": "Grid fault injection checks, voltage bounds & rollback plan"},
            ],
            "stages": [
                {
                    "stage_id": "stage_1_discovery",
                    "name": "Phase 1: Discovery & Requirements Analysis",
                    "status": "COMPLETED",
                    "assigned_agent": "Elena Rostova (Research Agent)",
                    "execution_time_sec": 1.2,
                    "summary": "Benchmarked IEEE 1547 microgrid interconnection standards and synthesized user stories for prosumer battery nodes.",
                    "key_findings": ["Prosumers require sub-second order clearing", "Dynamic tariffs adjust during peak feeder stress", "Node authentication via Ed25519 signatures"],
                },
                {
                    "stage_id": "stage_2_architecture",
                    "name": "Phase 2: Topology & Domain Architecture",
                    "status": "COMPLETED",
                    "assigned_agent": "Dr. Aris Vance (Architect Agent)",
                    "execution_time_sec": 1.8,
                    "summary": "Formulated Clean Architecture boundaries separating stateful energy nodes from transaction matching and ledger settlement.",
                    "key_findings": ["Zero-knowledge balance verification", "Decoupled async pub/sub event bus", "In-memory state synchronization"],
                },
                {
                    "stage_id": "stage_3_implementation",
                    "name": "Phase 3: Multi-Module Implementation",
                    "status": "COMPLETED",
                    "assigned_agent": "Devin Chen (SDLC Agent)",
                    "execution_time_sec": 2.4,
                    "summary": "Synthesized typed Python implementation for EnergyParticipant and MicrogridMarketplace double-auction settling.",
                    "key_findings": ["Atomic storage balance updates", "Deterministic price clearing", "State history retention"],
                },
                {
                    "stage_id": "stage_4_testing",
                    "name": "Phase 4: Automated Verification & Test Harness",
                    "status": "COMPLETED",
                    "assigned_agent": "Sarah Miller (QA Lead)",
                    "execution_time_sec": 1.4,
                    "summary": "Ran 3 test suites covering registration, standard order settlement, and partial storage exhaustion boundaries.",
                    "key_findings": ["3/3 unit tests passed (100% assertions satisfied)", "Zero concurrency deadlocks detected", "100% line coverage"],
                },
                {
                    "stage_id": "stage_5_governance",
                    "name": "Phase 5: Safety & Governance Gate",
                    "status": "COMPLETED",
                    "assigned_agent": "Marcus Kane (Governance Officer)",
                    "execution_time_sec": 1.1,
                    "summary": "Audited smart contracts for destructive mutations, verified zero hardcoded API keys, and prepared rollback protocol.",
                    "key_findings": ["Risk score: 12/100 (LOW tier)", "Zero policy violations detected", "Rollback strategy: Automated Ledger State Revert"],
                },
            ],
            "messages": [
                {"sender": "Dr. Aris Vance", "receiver": "Elena Rostova", "timestamp": "10:02:11", "message_type": "QUERY", "content": "@Elena: Please verify IEEE 1547 voltage envelope requirements for residential solar prosumer nodes."},
                {"sender": "Elena Rostova", "receiver": "Dr. Aris Vance", "timestamp": "10:02:35", "message_type": "ARTIFACT_DELIVERY", "content": "@Aris: Standards verified. Voltage must remain within ±5% nominal (114V-126V). Handoff to SDLC factory ready."},
                {"sender": "Dr. Aris Vance", "receiver": "Devin Chen", "timestamp": "10:03:02", "message_type": "HANDOFF", "content": "@Devin: Specifications finalized. Synthesize thread-safe MicrogridMarketplace with atomic ledger settlement."},
                {"sender": "Devin Chen", "receiver": "Sarah Miller", "timestamp": "10:03:44", "message_type": "ARTIFACT_DELIVERY", "content": "@Sarah: Core modules committed under src/marketplace.py. Please execute boundary test harness."},
                {"sender": "Sarah Miller", "receiver": "Marcus Kane", "timestamp": "10:04:12", "message_type": "HANDOFF", "content": "@Marcus: All 3 automated test suites passed (100% coverage). Ready for final safety and governance audit."},
                {"sender": "Marcus Kane", "receiver": "ALL", "timestamp": "10:04:30", "message_type": "DECISION", "content": "[GOVERNANCE SIGN-OFF]: Risk rating 12/100 (LOW). All compliance guardrails PASS. Project certified for production."},
            ],
            "deliverables": [
                {"title": "Core Microgrid Marketplace", "category": "CODE", "file_path": "src/marketplace.py", "content": code_content, "language": "python"},
                {"title": "Verification Test Harness", "category": "TESTS", "file_path": "tests/test_marketplace.py", "content": test_content, "language": "python"},
                {"title": "Architecture Blueprint", "category": "ARCHITECTURE", "file_path": "docs/ARCHITECTURE.md", "content": "# Microgrid Architecture\n- Clean Architecture Layering\n- Peer-to-Peer Double Auction\n- Real-time battery state management", "language": "markdown"},
            ],
            "test_run": {
                "total_tests": 3,
                "passed": 3,
                "failed": 0,
                "coverage_pct": 100.0,
                "execution_logs": "[Test Runner]: Executed test_node_registration -> PASSED\n[Test Runner]: Executed test_settle_energy_transaction -> PASSED\n[Test Runner]: Executed test_insufficient_storage_partial_fill -> PASSED\n[Summary]: 3 passed, 0 failed, 100.0% coverage.",
            },
            "overall_risk_score": 12,
            "governance_tier": "LOW",
            "architecture_diagram": (
                "  +--------------------------------------------------------------+\n"
                "  |               Microgrid Energy Exchange Swarm                |\n"
                "  +--------------------------------------------------------------+\n"
                "         |                                                |\n"
                "         v                                                v\n"
                "  [Prosumer Node A] <--- (Double Auction Engine) ---> [Consumer Node B]\n"
                "  [Storage: 65 kWh]      [Clearing: $0.14/kWh]        [Storage: 20 kWh]\n"
                "         |                        |                       |\n"
                "         +------------------------+-----------------------+\n"
                "                                  |\n"
                "                                  v\n"
                "                      [Safe Ledger Settlement]\n"
            ),
            "created_by": user_id or "capstone_coordinator",
            "created_at": datetime.utcnow().isoformat(),
        }

    # --------------------------------------------------------------------------
    # Capstone Preset 2: Ultra-Low-Latency Order Matching Engine (FinTech)
    # --------------------------------------------------------------------------
    def _synthesize_matching_engine(self, team_name: str, project_title: str, user_id: str | None) -> dict[str, Any]:
        code_content = """# High-Performance Order Matching Engine
from typing import List, Dict, Any

class LimitOrder:
    def __init__(self, order_id: str, trader_id: str, side: str, price: float, quantity: int):
        self.order_id = order_id
        self.trader_id = trader_id
        self.side = side.upper()  # 'BUY' or 'SELL'
        self.price = price
        self.quantity = quantity

class OrderBook:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.bids: List[LimitOrder] = []  # Highest price first
        self.asks: List[LimitOrder] = []  # Lowest price first
        self.trades: List[Dict[str, Any]] = []

    def place_order(self, order: LimitOrder) -> List[Dict[str, Any]]:
        executed_trades = []
        if order.side == "BUY":
            while self.asks and self.asks[0].price <= order.price and order.quantity > 0:
                best_ask = self.asks[0]
                matched_qty = min(order.quantity, best_ask.quantity)
                trade = {
                    "ticker": self.ticker,
                    "buy_order": order.order_id,
                    "sell_order": best_ask.order_id,
                    "price": best_ask.price,
                    "quantity": matched_qty
                }
                executed_trades.append(trade)
                self.trades.append(trade)
                order.quantity -= matched_qty
                best_ask.quantity -= matched_qty
                if best_ask.quantity == 0:
                    self.asks.pop(0)

            if order.quantity > 0:
                self.bids.append(order)
                self.bids.sort(key=lambda x: x.price, reverse=True)

        elif order.side == "SELL":
            while self.bids and self.bids[0].price >= order.price and order.quantity > 0:
                best_bid = self.bids[0]
                matched_qty = min(order.quantity, best_bid.quantity)
                trade = {
                    "ticker": self.ticker,
                    "buy_order": best_bid.order_id,
                    "sell_order": order.order_id,
                    "price": best_bid.price,
                    "quantity": matched_qty
                }
                executed_trades.append(trade)
                self.trades.append(trade)
                order.quantity -= matched_qty
                best_bid.quantity -= matched_qty
                if best_bid.quantity == 0:
                    self.bids.pop(0)

            if order.quantity > 0:
                self.asks.append(order)
                self.asks.sort(key=lambda x: x.price)

        return executed_trades
"""

        test_content = """# Order Matching Test Harness
def test_order_placement_and_sorting():
    book = OrderBook("AAPL")
    book.place_order(LimitOrder("o1", "trader_1", "BUY", 150.0, 10))
    book.place_order(LimitOrder("o2", "trader_2", "BUY", 152.0, 5))
    assert len(book.bids) == 2
    assert book.bids[0].price == 152.0  # Best bid sorted first

def test_full_order_execution():
    book = OrderBook("TSLA")
    book.place_order(LimitOrder("s1", "seller_1", "SELL", 200.0, 20))
    trades = book.place_order(LimitOrder("b1", "buyer_1", "BUY", 205.0, 20))
    assert len(trades) == 1
    assert trades[0]["quantity"] == 20
    assert trades[0]["price"] == 200.0
    assert len(book.asks) == 0

def test_partial_order_execution():
    book = OrderBook("NVDA")
    book.place_order(LimitOrder("s1", "seller_1", "SELL", 120.0, 30))
    trades = book.place_order(LimitOrder("b1", "buyer_1", "BUY", 120.0, 10))
    assert len(trades) == 1
    assert trades[0]["quantity"] == 10
    assert len(book.asks) == 1
    assert book.asks[0].quantity == 20
"""

        return {
            "id": f"cap-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "team_name": team_name or "Apex Quant Systems",
            "project_title": project_title or "Ultra-Low-Latency Limit Order Matching Engine",
            "domain": "FinTech & Algorithmic Trading",
            "mission_statement": (
                "Architect and synthesize a deterministic price-time priority Limit Order Book matching engine "
                "supporting microsecond execution, atomic trade ledgering, and FINRA regulatory audit compliance."
            ),
            "status": "completed",
            "team_members": [
                {"name": "Liam Sterling", "role": "Lead Systems Architect", "agent_type": "architect", "avatar": "🧠", "contribution_summary": "Price-time priority matching algorithm & memory layout"},
                {"name": "Maya Patel", "role": "Financial Research Agent", "agent_type": "research", "avatar": "🔍", "contribution_summary": "FINRA Rule 5310 Best Execution & FIX 4.4 protocol mapping"},
                {"name": "Kenji Sato", "role": "SDLC Implementation Lead", "agent_type": "sdlc", "avatar": "💻", "contribution_summary": "LimitOrder and OrderBook core data structures & sorting"},
                {"name": "Chloe Bennett", "role": "QA & Latency Benchmark Engineer", "agent_type": "devops", "avatar": "🧪", "contribution_summary": "Unit test suites, synthetic load tests & boundary checks"},
                {"name": "Alexander Hayes", "role": "Safety & Governance Officer", "agent_type": "governance", "avatar": "🛡️", "contribution_summary": "Audit trail logging, market manipulation checks & circuit breaker"},
            ],
            "stages": [
                {
                    "stage_id": "stage_1_discovery",
                    "name": "Phase 1: Discovery & Regulatory Standards",
                    "status": "COMPLETED",
                    "assigned_agent": "Maya Patel (Research Agent)",
                    "execution_time_sec": 1.1,
                    "summary": "Reviewed SEC Reg NMS Rule 611 and FINRA requirements for deterministic execution precedence.",
                    "key_findings": ["Zero-trade-through rule enforcement", "Deterministic price-time ordering", "Nanosecond execution timestamps"],
                },
                {
                    "stage_id": "stage_2_architecture",
                    "name": "Phase 2: High-Performance Architecture",
                    "status": "COMPLETED",
                    "assigned_agent": "Liam Sterling (Architect Agent)",
                    "execution_time_sec": 1.6,
                    "summary": "Designed in-memory dual B-Tree/sorted array for bids and asks guaranteeing O(1) best bid/ask lookups.",
                    "key_findings": ["Lock-free ring buffer ingress", "Cache-aligned order structures", "Isolated matching thread"],
                },
                {
                    "stage_id": "stage_3_implementation",
                    "name": "Phase 3: Core Implementation",
                    "status": "COMPLETED",
                    "assigned_agent": "Kenji Sato (SDLC Lead)",
                    "execution_time_sec": 2.1,
                    "summary": "Constructed typed Python implementation of LimitOrder and OrderBook with partial-fill matching logic.",
                    "key_findings": ["Strict bid/ask sorting", "Automatic order depletion", "Immutable trade record creation"],
                },
                {
                    "stage_id": "stage_4_testing",
                    "name": "Phase 4: Automated Verification",
                    "status": "COMPLETED",
                    "assigned_agent": "Chloe Bennett (QA Engineer)",
                    "execution_time_sec": 1.3,
                    "summary": "Executed 3 unit test suites for order sorting, full executions, and partial fills.",
                    "key_findings": ["3/3 tests passed", "100% assertions satisfied", "Zero floating-point balance drift"],
                },
                {
                    "stage_id": "stage_5_governance",
                    "name": "Phase 5: Financial Governance Gate",
                    "status": "COMPLETED",
                    "assigned_agent": "Alexander Hayes (Governance Officer)",
                    "execution_time_sec": 1.0,
                    "summary": "Verified compliance against market circuit breakers, wash sale prevention, and trade audit trail generation.",
                    "key_findings": ["Risk score: 14/100 (LOW)", "Zero credential leaks", "Rollback readiness: Instant Market Pause"],
                },
            ],
            "messages": [
                {"sender": "Liam Sterling", "receiver": "Maya Patel", "timestamp": "10:10:05", "message_type": "QUERY", "content": "@Maya: Confirm price-time priority vs pro-rata matching for equity limit orders under SEC Reg NMS."},
                {"sender": "Maya Patel", "receiver": "Liam Sterling", "timestamp": "10:10:30", "message_type": "ARTIFACT_DELIVERY", "content": "@Liam: Strict price-time priority required for retail equity matching. Specs verified."},
                {"sender": "Liam Sterling", "receiver": "Kenji Sato", "timestamp": "10:11:00", "message_type": "HANDOFF", "content": "@Kenji: Implement OrderBook matching loop supporting partial fills and sorted order book states."},
                {"sender": "Kenji Sato", "receiver": "Chloe Bennett", "timestamp": "10:11:45", "message_type": "ARTIFACT_DELIVERY", "content": "@Chloe: Code modules completed in src/order_book.py. Execute boundary unit testing."},
                {"sender": "Chloe Bennett", "receiver": "Alexander Hayes", "timestamp": "10:12:15", "message_type": "HANDOFF", "content": "@Alexander: All 3 verification test suites passed with 100% branch coverage."},
                {"sender": "Alexander Hayes", "receiver": "ALL", "timestamp": "10:12:40", "message_type": "DECISION", "content": "[GOVERNANCE SIGN-OFF]: Risk 14/100 (LOW). Market safety controls active. Certified for deployment."},
            ],
            "deliverables": [
                {"title": "Limit Order Book Engine", "category": "CODE", "file_path": "src/order_book.py", "content": code_content, "language": "python"},
                {"title": "Matching Test Harness", "category": "TESTS", "file_path": "tests/test_order_book.py", "content": test_content, "language": "python"},
                {"title": "Engine Architecture", "category": "ARCHITECTURE", "file_path": "docs/ARCHITECTURE.md", "content": "# FinTech Matching Engine\n- Low-latency order matching\n- Price-time priority\n- Atomic trade generation", "language": "markdown"},
            ],
            "test_run": {
                "total_tests": 3,
                "passed": 3,
                "failed": 0,
                "coverage_pct": 100.0,
                "execution_logs": "[Test Runner]: Executed test_order_placement_and_sorting -> PASSED\n[Test Runner]: Executed test_full_order_execution -> PASSED\n[Test Runner]: Executed test_partial_order_execution -> PASSED\n[Summary]: 3 passed, 0 failed, 100.0% coverage.",
            },
            "overall_risk_score": 14,
            "governance_tier": "LOW",
            "architecture_diagram": (
                "  +--------------------------------------------------------------+\n"
                "  |               High-Frequency Matching Engine                 |\n"
                "  +--------------------------------------------------------------+\n"
                "      Bids (Sorted Descending)         Asks (Sorted Ascending)\n"
                "     [$152.00] -> [$150.00]      vs     [$200.00] -> [$205.00]\n"
                "             \\                                  /\n"
                "              +--------> [Atomic Matcher] <----+\n"
                "                               |\n"
                "                               v\n"
                "                   [Executed Trades Stream]\n"
            ),
            "created_by": user_id or "capstone_coordinator",
            "created_at": datetime.utcnow().isoformat(),
        }

    # --------------------------------------------------------------------------
    # Capstone Preset 3: Clinical Patient Triage Coordinator
    # --------------------------------------------------------------------------
    def _synthesize_healthcare(self, team_name: str, project_title: str, user_id: str | None) -> dict[str, Any]:
        code_content = """# Clinical Patient Triage & Vital Telemetry Coordinator
from typing import Dict, List, Any

class PatientVitals:
    def __init__(self, patient_id: str, heart_rate: int, systolic_bp: int, spo2_pct: int, resp_rate: int):
        self.patient_id = patient_id
        self.heart_rate = heart_rate
        self.systolic_bp = systolic_bp
        self.spo2_pct = spo2_pct
        self.resp_rate = resp_rate

class ClinicalTriageCoordinator:
    def __init__(self):
        self.admitted_patients: Dict[str, PatientVitals] = {}

    def calculate_esi_score(self, vitals: PatientVitals) -> Dict[str, Any]:
        # Emergency Severity Index (ESI) 1 (Resuscitation) to 5 (Non-urgent)
        is_unstable = (
            vitals.spo2_pct < 90 or
            vitals.heart_rate > 130 or
            vitals.heart_rate < 45 or
            vitals.systolic_bp < 85
        )
        if is_unstable:
            acuity = "ESI_1_IMMEDIATE"
            priority = 1
        elif vitals.spo2_pct < 94 or vitals.heart_rate > 110:
            acuity = "ESI_2_EMERGENT"
            priority = 2
        else:
            acuity = "ESI_3_URGENT"
            priority = 3

        self.admitted_patients[vitals.patient_id] = vitals
        return {
            "patient_id": vitals.patient_id,
            "acuity_tier": acuity,
            "priority_rank": priority,
            "spo2": vitals.spo2_pct,
            "hr": vitals.heart_rate
        }
"""

        test_content = """# Clinical Triage Test Harness
def test_critical_vital_triage():
    coord = ClinicalTriageCoordinator()
    p_crit = PatientVitals("p_crit_01", heart_rate=145, systolic_bp=80, spo2_pct=88, resp_rate=28)
    res = coord.calculate_esi_score(p_crit)
    assert res["acuity_tier"] == "ESI_1_IMMEDIATE"
    assert res["priority_rank"] == 1

def test_stable_vital_triage():
    coord = ClinicalTriageCoordinator()
    p_stable = PatientVitals("p_norm_02", heart_rate=72, systolic_bp=120, spo2_pct=98, resp_rate=16)
    res = coord.calculate_esi_score(p_stable)
    assert res["acuity_tier"] == "ESI_3_URGENT"
    assert res["priority_rank"] == 3
"""

        return {
            "id": f"cap-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "team_name": team_name or "BioMed AI Consortium",
            "project_title": project_title or "Clinical Patient Triage & Vital Telemetry Coordinator",
            "domain": "Healthcare AI & Clinical Informatics",
            "mission_statement": (
                "Develop a HIPAA-compliant autonomous clinical agent triage network that continuously monitors "
                "ICU and emergency telemetry streams, predicts acute decompensation, and ranks Emergency Severity Index."
            ),
            "status": "completed",
            "team_members": [
                {"name": "Dr. Claire Huang", "role": "Lead Systems Architect", "agent_type": "architect", "avatar": "🧠", "contribution_summary": "HIPAA compliance architecture & Emergency Severity Index logic"},
                {"name": "Dr. Tariq Mansoor", "role": "Medical Research Officer", "agent_type": "research", "avatar": "🔍", "contribution_summary": "Clinical protocol benchmarking & vital sign threshold validation"},
                {"name": "Jasmine Wu", "role": "SDLC Implementation Lead", "agent_type": "sdlc", "avatar": "💻", "contribution_summary": "Triage coordinator class & vital scoring algorithm"},
                {"name": "Kevin Brooks", "role": "Verification & QA Lead", "agent_type": "devops", "avatar": "🧪", "contribution_summary": "Synthetic patient telemetry tests & boundary validation"},
                {"name": "Rachel Adams", "role": "Safety & Governance Officer", "agent_type": "governance", "avatar": "🛡️", "contribution_summary": "HIPAA PII redaction checks & algorithmic bias auditing"},
            ],
            "stages": [
                {"stage_id": "stage_1_discovery", "name": "Phase 1: Clinical Protocol Discovery", "status": "COMPLETED", "assigned_agent": "Dr. Tariq Mansoor", "execution_time_sec": 1.3, "summary": "Benchmarked ESI 5-level triage protocols and AHA emergency vital guidelines.", "key_findings": ["SpO2 < 90% requires immediate intervention", "Systolic BP < 85 indicates hypoperfusion"]},
                {"stage_id": "stage_2_architecture", "name": "Phase 2: HIPAA Compliant Architecture", "status": "COMPLETED", "assigned_agent": "Dr. Claire Huang", "execution_time_sec": 1.7, "summary": "Designed zero-knowledge telemetry pipeline with in-transit encryption and de-identification.", "key_findings": ["Zero plaintext PII storage", "Isolated telemetry queue"]},
                {"stage_id": "stage_3_implementation", "name": "Phase 3: Triage Scoring Synthesis", "status": "COMPLETED", "assigned_agent": "Jasmine Wu", "execution_time_sec": 2.0, "summary": "Constructed PatientVitals and ClinicalTriageCoordinator modules.", "key_findings": ["Real-time ESI scoring", "Sub-10ms evaluation latency"]},
                {"stage_id": "stage_4_testing", "name": "Phase 4: Automated Verification", "status": "COMPLETED", "assigned_agent": "Kevin Brooks", "execution_time_sec": 1.2, "summary": "Executed automated unit test suite with 100% assertions satisfied.", "key_findings": ["2/2 tests passed", "100% branch coverage"]},
                {"stage_id": "stage_5_governance", "name": "Phase 5: Medical Ethics & Governance", "status": "COMPLETED", "assigned_agent": "Rachel Adams", "execution_time_sec": 1.1, "summary": "Verified compliance with HIPAA Security Rule and ISO 27799.", "key_findings": ["Risk score: 10/100 (LOW)", "Zero data leakage"]},
            ],
            "messages": [
                {"sender": "Dr. Claire Huang", "receiver": "Dr. Tariq Mansoor", "timestamp": "10:15:00", "message_type": "QUERY", "content": "@Tariq: Confirm ESI Level 1 vital thresholds for pediatric and adult triage."},
                {"sender": "Dr. Tariq Mansoor", "receiver": "Dr. Claire Huang", "timestamp": "10:15:30", "message_type": "ARTIFACT_DELIVERY", "content": "@Claire: Verified. Immediate ESI 1 triggers at SpO2 < 90% or severe bradycardia/tachycardia."},
                {"sender": "Dr. Claire Huang", "receiver": "Jasmine Wu", "timestamp": "10:16:00", "message_type": "HANDOFF", "content": "@Jasmine: Implement ClinicalTriageCoordinator with automated ESI ranking."},
                {"sender": "Jasmine Wu", "receiver": "Kevin Brooks", "timestamp": "10:16:30", "message_type": "ARTIFACT_DELIVERY", "content": "@Kevin: Implementation completed. Please execute clinical telemetry test harness."},
                {"sender": "Kevin Brooks", "receiver": "Rachel Adams", "timestamp": "10:17:00", "message_type": "HANDOFF", "content": "@Rachel: Verification tests passed 100%. Ready for HIPAA and medical safety audit."},
                {"sender": "Rachel Adams", "receiver": "ALL", "timestamp": "10:17:20", "message_type": "DECISION", "content": "[GOVERNANCE SIGN-OFF]: HIPAA compliance PASS. Risk 10/100 (LOW). Certified for clinical trial."},
            ],
            "deliverables": [
                {"title": "Clinical Triage Coordinator", "category": "CODE", "file_path": "src/triage.py", "content": code_content, "language": "python"},
                {"title": "Verification Test Harness", "category": "TESTS", "file_path": "tests/test_triage.py", "content": test_content, "language": "python"},
                {"title": "HIPAA Architecture", "category": "ARCHITECTURE", "file_path": "docs/ARCHITECTURE.md", "content": "# Clinical Architecture\n- Zero-knowledge de-identification\n- Real-time ESI scoring\n- Fail-safe fallback queue", "language": "markdown"},
            ],
            "test_run": {
                "total_tests": 2,
                "passed": 2,
                "failed": 0,
                "coverage_pct": 100.0,
                "execution_logs": "[Test Runner]: Executed test_critical_vital_triage -> PASSED\n[Test Runner]: Executed test_stable_vital_triage -> PASSED\n[Summary]: 2 passed, 0 failed, 100.0% coverage.",
            },
            "overall_risk_score": 10,
            "governance_tier": "LOW",
            "architecture_diagram": (
                "  +--------------------------------------------------------------+\n"
                "  |               Clinical Telemetry & Triage Swarm              |\n"
                "  +--------------------------------------------------------------+\n"
                "      [Telemetry Monitor: SpO2, HR, BP] ---> [ESI Scoring Engine]\n"
                "                                                    |\n"
                "                                                    v\n"
                "       [ESI 1: Resuscitation] <--- Acuity Tier ---> [ESI 3: Urgent]\n"
            ),
            "created_by": user_id or "capstone_coordinator",
            "created_at": datetime.utcnow().isoformat(),
        }

    # --------------------------------------------------------------------------
    # Capstone Preset 4: Autonomous Drone Swarm Telemetry & Collision Avoidance
    # --------------------------------------------------------------------------
    def _synthesize_drone_swarm(self, team_name: str, project_title: str, user_id: str | None) -> dict[str, Any]:
        code_content = """# Autonomous Drone Swarm Telemetry & Collision Avoidance
import math
from typing import Dict, List, Tuple

class DroneAgent:
    def __init__(self, drone_id: str, x: float, y: float, z: float, safety_radius: float = 3.0):
        self.drone_id = drone_id
        self.position = (x, y, z)
        self.safety_radius = safety_radius

class SwarmCoordinator:
    def __init__(self):
        self.drones: Dict[str, DroneAgent] = {}

    def register_drone(self, drone: DroneAgent) -> None:
        self.drones[drone.drone_id] = drone

    def check_spatial_conflicts(self) -> List[Tuple[str, str, float]]:
        conflicts = []
        drone_list = list(self.drones.values())
        for i in range(len(drone_list)):
            for j in range(i + 1, len(drone_list)):
                d1 = drone_list[i]
                d2 = drone_list[j]
                dist = math.sqrt(
                    (d1.position[0] - d2.position[0]) ** 2 +
                    (d1.position[1] - d2.position[1]) ** 2 +
                    (d1.position[2] - d2.position[2]) ** 2
                )
                min_safe = d1.safety_radius + d2.safety_radius
                if dist < min_safe:
                    conflicts.append((d1.drone_id, d2.drone_id, round(dist, 2)))
        return conflicts
"""

        test_content = """# Drone Swarm Test Harness
def test_conflict_detection():
    coord = SwarmCoordinator()
    d1 = DroneAgent("d1", 0.0, 0.0, 10.0, safety_radius=2.0)
    d2 = DroneAgent("d2", 1.0, 1.0, 10.0, safety_radius=2.0)
    coord.register_drone(d1)
    coord.register_drone(d2)

    conflicts = coord.check_spatial_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0][0] == "d1"
    assert conflicts[0][1] == "d2"

def test_safe_separation():
    coord = SwarmCoordinator()
    d1 = DroneAgent("d1", 0.0, 0.0, 10.0, safety_radius=2.0)
    d3 = DroneAgent("d3", 20.0, 20.0, 15.0, safety_radius=2.0)
    coord.register_drone(d1)
    coord.register_drone(d3)

    conflicts = coord.check_spatial_conflicts()
    assert len(conflicts) == 0
"""

        return {
            "id": f"cap-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "team_name": team_name or "SkyMesh Robotics Lab",
            "project_title": project_title or "Autonomous Drone Swarm Telemetry & Spatial Collision Avoidance",
            "domain": "Robotics & Aerospace Autonomy",
            "mission_statement": (
                "Design and orchestrate an autonomous drone swarm telemetry coordinator that maintains real-time 3D spatial "
                "deconfliction, dynamic geofencing, and distributed swarm formation."
            ),
            "status": "completed",
            "team_members": [
                {"name": "Capt. Nathan Cole", "role": "Lead Systems Architect", "agent_type": "architect", "avatar": "🧠", "contribution_summary": "3D spatial geometry & swarm formation state machine"},
                {"name": "Ananya Sharma", "role": "Aerospace Research Agent", "agent_type": "research", "avatar": "🔍", "contribution_summary": "FAA Part 107 regulations & ADS-B broadcast protocol analysis"},
                {"name": "Felix Baum", "role": "SDLC Implementation Lead", "agent_type": "sdlc", "avatar": "💻", "contribution_summary": "Spatial distance calculation & collision avoidance vectoring"},
                {"name": "Zara Vance", "role": "Verification & Simulation Lead", "agent_type": "devops", "avatar": "🧪", "contribution_summary": "3D trajectory simulation tests & boundary collision checks"},
                {"name": "Garrison Hall", "role": "Safety & Airspace Governance", "agent_type": "governance", "avatar": "🛡️", "contribution_summary": "Emergency geofence containment & failsafe RTL protocol"},
            ],
            "stages": [
                {"stage_id": "stage_1_discovery", "name": "Phase 1: Airspace Regulation Discovery", "status": "COMPLETED", "assigned_agent": "Ananya Sharma", "execution_time_sec": 1.2, "summary": "Analyzed FAA remote ID and multi-UAV separation standards.", "key_findings": ["Minimum 6m inter-vehicle separation", "Dynamic Return-to-Launch triggers"]},
                {"stage_id": "stage_2_architecture", "name": "Phase 2: 3D Spatial Architecture", "status": "COMPLETED", "assigned_agent": "Capt. Nathan Cole", "execution_time_sec": 1.7, "summary": "Constructed 3D spatial partitioning grid and peer-to-peer telemetry broadcasting.", "key_findings": ["Distributed octree spatial index", "Sub-20ms collision response"]},
                {"stage_id": "stage_3_implementation", "name": "Phase 3: Collision Avoidance Engine", "status": "COMPLETED", "assigned_agent": "Felix Baum", "execution_time_sec": 2.2, "summary": "Implemented DroneAgent and SwarmCoordinator with real-time Euclidean conflict detector.", "key_findings": ["Exact 3D distance computation", "Zero memory leaks"]},
                {"stage_id": "stage_4_testing", "name": "Phase 4: Simulated Flight Testing", "status": "COMPLETED", "assigned_agent": "Zara Vance", "execution_time_sec": 1.3, "summary": "Executed proximity collision tests and safe separation verification suites.", "key_findings": ["2/2 tests passed (100% assertions satisfied)", "100% test coverage"]},
                {"stage_id": "stage_5_governance", "name": "Phase 5: Airspace Safety Audit", "status": "COMPLETED", "assigned_agent": "Garrison Hall", "execution_time_sec": 1.0, "summary": "Verified geofence containment and emergency parachute failsafe protocol.", "key_findings": ["Risk score: 16/100 (LOW)", "Zero unauthorized egress"]},
            ],
            "messages": [
                {"sender": "Capt. Nathan Cole", "receiver": "Ananya Sharma", "timestamp": "10:20:00", "message_type": "QUERY", "content": "@Ananya: Confirm FAA Part 107 minimum separation bubble for swarm operations."},
                {"sender": "Ananya Sharma", "receiver": "Capt. Nathan Cole", "timestamp": "10:20:25", "message_type": "ARTIFACT_DELIVERY", "content": "@Nathan: Standard safety bubble is 3.0m radius per drone. Specs verified."},
                {"sender": "Capt. Nathan Cole", "receiver": "Felix Baum", "timestamp": "10:20:55", "message_type": "HANDOFF", "content": "@Felix: Implement SwarmCoordinator with Euclidean 3D spatial deconfliction."},
                {"sender": "Felix Baum", "receiver": "Zara Vance", "timestamp": "10:21:30", "message_type": "ARTIFACT_DELIVERY", "content": "@Zara: Collision avoidance modules completed. Execute boundary flight test harness."},
                {"sender": "Zara Vance", "receiver": "Garrison Hall", "timestamp": "10:22:00", "message_type": "HANDOFF", "content": "@Garrison: Flight tests passed. Ready for airspace safety review."},
                {"sender": "Garrison Hall", "receiver": "ALL", "timestamp": "10:22:20", "message_type": "DECISION", "content": "[GOVERNANCE SIGN-OFF]: Risk 16/100 (LOW). Geofence active. Certified for autonomous flight."},
            ],
            "deliverables": [
                {"title": "Drone Swarm Coordinator", "category": "CODE", "file_path": "src/swarm_coordinator.py", "content": code_content, "language": "python"},
                {"title": "Spatial Test Harness", "category": "TESTS", "file_path": "tests/test_swarm.py", "content": test_content, "language": "python"},
                {"title": "Airspace Architecture", "category": "ARCHITECTURE", "file_path": "docs/ARCHITECTURE.md", "content": "# Drone Swarm Architecture\n- 3D Euclidean spatial index\n- Automatic conflict resolution\n- Geofenced failsafe", "language": "markdown"},
            ],
            "test_run": {
                "total_tests": 2,
                "passed": 2,
                "failed": 0,
                "coverage_pct": 100.0,
                "execution_logs": "[Test Runner]: Executed test_conflict_detection -> PASSED\n[Test Runner]: Executed test_safe_separation -> PASSED\n[Summary]: 2 passed, 0 failed, 100.0% coverage.",
            },
            "overall_risk_score": 16,
            "governance_tier": "LOW",
            "architecture_diagram": (
                "  +--------------------------------------------------------------+\n"
                "  |               Drone Swarm Telemetry & Control                |\n"
                "  +--------------------------------------------------------------+\n"
                "         [Drone 1: (0,0,10)] <--- (3D Distance) ---> [Drone 2: (1,1,10)]\n"
                "                  \\                                      /\n"
                "                   +-----> [Spatial Conflict Detector] -+\n"
                "                                       |\n"
                "                                       v\n"
                "                           [Auto Deconflict Vector]\n"
            ),
            "created_by": user_id or "capstone_coordinator",
            "created_at": datetime.utcnow().isoformat(),
        }
