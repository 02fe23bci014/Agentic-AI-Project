from backend.database.connection import get_connection


DSA_SCENARIO_QUESTIONS = [
    # ==========================================================================
    # 1. ARRAYS
    # ==========================================================================
    {
        "id": "question-dsa-arr-l1",
        "title": "E-Commerce Checkout Voucher Pairing",
        "domain": "Arrays",
        "difficulty": "L1",
        "points": 5,
        "language": "python",
        "prompt": (
            "Scenario: An e-commerce platform offers a promotional shopping voucher of exact value T. "
            "A shopper wants to purchase exactly two items from their cart such that their combined price equals T. "
            "Given the item prices in the cart, find the 0-indexed positions of the two items. "
            "Output the smaller index first separated by a space.\n\n"
            "Input format:\n"
            "Line 1: Target voucher value T (integer)\n"
            "Line 2: Space-separated item prices\n\n"
            "Output format:\n"
            "Two space-separated indices.\n\n"
            "Sample Input:\n9\n2 7 11 15\nSample Output:\n0 1"
        ),
        "test_cases": [
            {"id": "tc-arr-l1-1", "stdin": "9\n2 7 11 15", "expected_stdout": "0 1", "points": 2.5, "is_hidden": 0},
            {"id": "tc-arr-l1-2", "stdin": "6\n3 2 4", "expected_stdout": "1 2", "points": 2.5, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-arr-l2",
        "title": "Smart Meter Power Consumption Target Window",
        "domain": "Arrays",
        "difficulty": "L2",
        "points": 10,
        "language": "python",
        "prompt": (
            "Scenario: An electrical grid smart meter records power consumption spikes every hour. "
            "An analyst wants to detect all continuous time windows during which the total power consumed "
            "equals an exact target threshold K megawatt-hours. "
            "Count the total number of continuous sub-arrays whose sum equals K.\n\n"
            "Input format:\n"
            "Line 1: Target power threshold K (integer)\n"
            "Line 2: Space-separated hourly power readings\n\n"
            "Output format:\n"
            "An integer count of matching time windows.\n\n"
            "Sample Input:\n2\n1 1 1\nSample Output:\n2"
        ),
        "test_cases": [
            {"id": "tc-arr-l2-1", "stdin": "2\n1 1 1", "expected_stdout": "2", "points": 5.0, "is_hidden": 0},
            {"id": "tc-arr-l2-2", "stdin": "3\n1 2 3", "expected_stdout": "2", "points": 5.0, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-arr-l3",
        "title": "Smart City Skyline Rooftop Stormwater Retention",
        "domain": "Arrays",
        "difficulty": "L3",
        "points": 15,
        "language": "python",
        "prompt": (
            "Scenario: Civil environmental sensors monitor a skyscraper skyline elevation profile where adjacent building heights "
            "form vertical barriers of width 1 meter. During torrential rainfall, rainwater accumulates between taller roofs. "
            "Calculate the total trapped stormwater volume (in cubic meters) that the building retention basins will hold.\n\n"
            "Input format:\n"
            "A single line of space-separated non-negative integers representing rooftop heights.\n\n"
            "Output format:\n"
            "An integer denoting total trapped water units.\n\n"
            "Sample Input:\n0 1 0 2 1 0 1 3 2 1 2 1\nSample Output:\n6"
        ),
        "test_cases": [
            {"id": "tc-arr-l3-1", "stdin": "0 1 0 2 1 0 1 3 2 1 2 1", "expected_stdout": "6", "points": 7.5, "is_hidden": 0},
            {"id": "tc-arr-l3-2", "stdin": "4 2 0 3 2 5", "expected_stdout": "9", "points": 7.5, "is_hidden": 1},
        ],
    },

    # ==========================================================================
    # 2. STRINGS
    # ==========================================================================
    {
        "id": "question-dsa-str-l1",
        "title": "Cryptographic Anagram Authentication",
        "domain": "Strings",
        "difficulty": "L1",
        "points": 5,
        "language": "python",
        "prompt": (
            "Scenario: A secure access terminal verifies user passphrases using character transposition hashing. "
            "The system checks if a submitted credential string t is a valid anagram of the master passkey s "
            "(meaning t contains the exact same characters with identical frequencies, rearranged in any order).\n\n"
            "Input format:\n"
            "Line 1: Master passkey string s\n"
            "Line 2: Submitted credential string t\n\n"
            "Output format:\n"
            "'true' if valid anagram, 'false' otherwise.\n\n"
            "Sample Input:\nanagram\nnagaram\nSample Output:\ntrue"
        ),
        "test_cases": [
            {"id": "tc-str-l1-1", "stdin": "anagram\nnagaram", "expected_stdout": "true", "points": 2.5, "is_hidden": 0},
            {"id": "tc-str-l1-2", "stdin": "rat\ncar", "expected_stdout": "false", "points": 2.5, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-str-l2",
        "title": "Telecommunications Signal Unique Packet Window",
        "domain": "Strings",
        "difficulty": "L2",
        "points": 10,
        "language": "python",
        "prompt": (
            "Scenario: A 5G satellite antenna decodes a continuous raw radio telemetry string s. "
            "To prevent demodulation cross-talk, the receiver must identify the maximum duration (length) "
            "of a contiguous transmission window that contains zero repeating signal characters.\n\n"
            "Input format:\n"
            "A single line containing the transmission string s.\n\n"
            "Output format:\n"
            "An integer denoting maximum length.\n\n"
            "Sample Input:\nabcabcbb\nSample Output:\n3"
        ),
        "test_cases": [
            {"id": "tc-str-l2-1", "stdin": "abcabcbb", "expected_stdout": "3", "points": 5.0, "is_hidden": 0},
            {"id": "tc-str-l2-2", "stdin": "bbbbb", "expected_stdout": "1", "points": 5.0, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-str-l3",
        "title": "Bioinformatics Genomic Sequence Mutation Distance",
        "domain": "Strings",
        "difficulty": "L3",
        "points": 15,
        "language": "python",
        "prompt": (
            "Scenario: A computational genomics pipeline compares two virus strain RNA sequences (word1 and word2). "
            "Each mutation corresponds to either an insertion, deletion, or substitution of a single nucleotide. "
            "Calculate the minimum number of mutation steps needed to transform word1 into word2 (Levenshtein distance).\n\n"
            "Input format:\n"
            "Line 1: Target RNA sequence word1\n"
            "Line 2: Source RNA sequence word2\n\n"
            "Output format:\n"
            "An integer denoting minimum mutation operations.\n\n"
            "Sample Input:\nhorse\nros\nSample Output:\n3"
        ),
        "test_cases": [
            {"id": "tc-str-l3-1", "stdin": "horse\nros", "expected_stdout": "3", "points": 7.5, "is_hidden": 0},
            {"id": "tc-str-l3-2", "stdin": "intention\nexecution", "expected_stdout": "5", "points": 7.5, "is_hidden": 1},
        ],
    },

    # ==========================================================================
    # 3. STACKS
    # ==========================================================================
    {
        "id": "question-dsa-stk-l1",
        "title": "Cloud IDE Compiler Scope Delimiter Validator",
        "domain": "Stacks",
        "difficulty": "L1",
        "points": 5,
        "language": "python",
        "prompt": (
            "Scenario: A web-based code editor's syntax parser checks code snippets before sending them to the compiler. "
            "The parser must verify that all opening brackets '(', '{', '[' are properly closed by their corresponding "
            "matching delimiters in the correct LIFO nesting order.\n\n"
            "Input format:\n"
            "A single line of brackets.\n\n"
            "Output format:\n"
            "'true' if validly nested, 'false' otherwise.\n\n"
            "Sample Input:\n()[]{}\nSample Output:\ntrue"
        ),
        "test_cases": [
            {"id": "tc-stk-l1-1", "stdin": "()[]{}", "expected_stdout": "true", "points": 2.5, "is_hidden": 0},
            {"id": "tc-stk-l1-2", "stdin": "(]", "expected_stdout": "false", "points": 2.5, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-stk-l2",
        "title": "FinTech Stock Market Next Breakout Day",
        "domain": "Stacks",
        "difficulty": "L2",
        "points": 10,
        "language": "python",
        "prompt": (
            "Scenario: An algorithmic trading desk monitors daily closing share prices. "
            "For each trading day, an automated alert must notify brokers of the very next trading day in the future "
            "that sees a higher stock price. If no higher price occurs in the remaining days, output -1 for that day. "
            "Solve in linear time using a monotonic stack.\n\n"
            "Input format:\n"
            "Line 1: Total trading days N\n"
            "Line 2: N space-separated daily prices\n\n"
            "Output format:\n"
            "Space-separated next breakout price values.\n\n"
            "Sample Input:\n4\n4 5 2 25\nSample Output:\n5 25 25 -1"
        ),
        "test_cases": [
            {"id": "tc-stk-l2-1", "stdin": "4\n4 5 2 25", "expected_stdout": "5 25 25 -1", "points": 5.0, "is_hidden": 0},
            {"id": "tc-stk-l2-2", "stdin": "3\n13 7 6", "expected_stdout": "-1 -1 -1", "points": 5.0, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-stk-l3",
        "title": "Urban Advertising Skyline Billboard Optimization",
        "domain": "Stacks",
        "difficulty": "L3",
        "points": 15,
        "language": "python",
        "prompt": (
            "Scenario: A digital billboard company wants to mount a rectangular LED video wall across adjacent downtown skyscrapers. "
            "Each building has a width of 1 unit and a measured height. The billboard banner must be a single contiguous rectangle "
            "supported by consecutive building rooftops. Find the maximum possible display area.\n\n"
            "Input format:\n"
            "Line 1: Number of buildings N\n"
            "Line 2: N space-separated building heights\n\n"
            "Output format:\n"
            "An integer denoting maximum contiguous billboard area.\n\n"
            "Sample Input:\n6\n2 1 5 6 2 3\nSample Output:\n10"
        ),
        "test_cases": [
            {"id": "tc-stk-l3-1", "stdin": "6\n2 1 5 6 2 3", "expected_stdout": "10", "points": 7.5, "is_hidden": 0},
            {"id": "tc-stk-l3-2", "stdin": "2\n2 4", "expected_stdout": "4", "points": 7.5, "is_hidden": 1},
        ],
    },

    # ==========================================================================
    # 4. QUEUES
    # ==========================================================================
    {
        "id": "question-dsa-que-l1",
        "title": "Cloud Print Spooler & Buffer Dispatch",
        "domain": "Queues",
        "difficulty": "L1",
        "points": 5,
        "language": "python",
        "prompt": (
            "Scenario: An enterprise document spooler schedules incoming print tasks using a first-in, first-out (FIFO) queue. "
            "The spooler processes operations: 'PUSH doc_id' (enqueues job), 'POP' (dispatches and prints front job id), "
            "and 'FRONT' (inspects next job in line without dispatching).\n\n"
            "Input format:\n"
            "Line 1: Number of spooler operations N\n"
            "Next N lines: Command string\n\n"
            "Output format:\n"
            "Outputs of POP and FRONT commands on separate lines.\n\n"
            "Sample Input:\n4\nPUSH 10\nPUSH 20\nPOP\nFRONT\nSample Output:\n10\n20"
        ),
        "test_cases": [
            {"id": "tc-que-l1-1", "stdin": "4\nPUSH 10\nPUSH 20\nPOP\nFRONT", "expected_stdout": "10\n20", "points": 2.5, "is_hidden": 0},
            {"id": "tc-que-l1-2", "stdin": "3\nPUSH 5\nFRONT\nPOP", "expected_stdout": "5\n5", "points": 2.5, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-que-l2",
        "title": "Customer Support Live Chat Unique Agent Dispatch",
        "domain": "Queues",
        "difficulty": "L2",
        "points": 10,
        "language": "python",
        "prompt": (
            "Scenario: A high-concurrency customer support chat server receives keystroke events in a stream string s. "
            "To detect novel operator requests, find the 0-based index of the very first character that does not repeat "
            "anywhere else in the stream. If every character repeats, return -1.\n\n"
            "Input format:\n"
            "A single line containing keystroke string s.\n\n"
            "Output format:\n"
            "The 0-based index of the first non-repeating character.\n\n"
            "Sample Input:\nleetcode\nSample Output:\n0"
        ),
        "test_cases": [
            {"id": "tc-que-l2-1", "stdin": "leetcode", "expected_stdout": "0", "points": 5.0, "is_hidden": 0},
            {"id": "tc-que-l2-2", "stdin": "loveleetcode", "expected_stdout": "2", "points": 5.0, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-que-l3",
        "title": "Network Edge Router Sliding Window Peak Burst Traffic",
        "domain": "Queues",
        "difficulty": "L3",
        "points": 15,
        "language": "python",
        "prompt": (
            "Scenario: A telecommunications gateway router monitors incoming megabit packet bursts in sliding observation "
            "windows of size k. As the observation window slides across the timeline from left to right, determine the peak "
            "bandwidth spike observed in every window position. Compute in O(N) using a monotonic deque.\n\n"
            "Input format:\n"
            "Line 1: Sliding window duration k (integer)\n"
            "Line 2: Space-separated packet burst measurements\n\n"
            "Output format:\n"
            "Space-separated maximum traffic values for each consecutive window.\n\n"
            "Sample Input:\n3\n1 3 -1 -3 5 3 6 7\nSample Output:\n3 3 5 5 6 7"
        ),
        "test_cases": [
            {"id": "tc-que-l3-1", "stdin": "3\n1 3 -1 -3 5 3 6 7", "expected_stdout": "3 3 5 5 6 7", "points": 7.5, "is_hidden": 0},
            {"id": "tc-que-l3-2", "stdin": "1\n1", "expected_stdout": "1", "points": 7.5, "is_hidden": 1},
        ],
    },

    # ==========================================================================
    # 5. LINKED LISTS
    # ==========================================================================
    {
        "id": "question-dsa-ll-l1",
        "title": "Browser Navigation Trail History Reversal",
        "domain": "Linked Lists",
        "difficulty": "L1",
        "points": 5,
        "language": "python",
        "prompt": (
            "Scenario: An embedded web browser tracks page visit history as a singly linked forward trail: A -> B -> C. "
            "When the user selects 'Reverse Navigation Session', the browser must flip all internal pointer links in-place "
            "so the last visited page becomes the head of the trail.\n\n"
            "Input format:\n"
            "Line 1: Number of visited pages N\n"
            "Line 2: N space-separated page IDs\n\n"
            "Output format:\n"
            "Space-separated reversed page sequence.\n\n"
            "Sample Input:\n5\n1 2 3 4 5\nSample Output:\n5 4 3 2 1"
        ),
        "test_cases": [
            {"id": "tc-ll-l1-1", "stdin": "5\n1 2 3 4 5", "expected_stdout": "5 4 3 2 1", "points": 2.5, "is_hidden": 0},
            {"id": "tc-ll-l1-2", "stdin": "2\n1 2", "expected_stdout": "2 1", "points": 2.5, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-ll-l2",
        "title": "Supply Chain Sorted Inventory Feed Merge",
        "domain": "Linked Lists",
        "difficulty": "L2",
        "points": 10,
        "language": "python",
        "prompt": (
            "Scenario: An automated logistics hub receives two real-time supplier parts streams, each pre-sorted in ascending SKU order. "
            "The warehouse intake belt must splice the two streams into a single unified sorted sequence without re-sorting from scratch.\n\n"
            "Input format:\n"
            "Line 1: Space-separated sorted integers of Stream 1\n"
            "Line 2: Space-separated sorted integers of Stream 2\n\n"
            "Output format:\n"
            "Space-separated merged sorted integers.\n\n"
            "Sample Input:\n1 2 4\n1 3 4\nSample Output:\n1 1 2 3 4 4"
        ),
        "test_cases": [
            {"id": "tc-ll-l2-1", "stdin": "1 2 4\n1 3 4", "expected_stdout": "1 1 2 3 4 4", "points": 5.0, "is_hidden": 0},
            {"id": "tc-ll-l2-2", "stdin": "1 5\n2 3 6", "expected_stdout": "1 2 3 5 6", "points": 5.0, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-ll-l3",
        "title": "Microservice RPC Call Chain Deadlock Loop Detection",
        "domain": "Linked Lists",
        "difficulty": "L3",
        "points": 15,
        "language": "python",
        "prompt": (
            "Scenario: In a microservices architecture, asynchronous event requests pass sequentially from service to service. "
            "A routing misconfiguration can cause a service to forward an event back to a previously visited node, causing an infinite loop. "
            "Given the node sequence and a pos pointer index (-1 if terminal, or 0-indexed destination where the tail loops to), "
            "detect whether a cycle exists using Floyd's algorithm.\n\n"
            "Input format:\n"
            "Line 1: Space-separated service IDs\n"
            "Line 2: Loop target index pos (-1 for no cycle)\n\n"
            "Output format:\n"
            "'true' if cycle detected, 'false' otherwise.\n\n"
            "Sample Input:\n3 2 0 -4\n1\nSample Output:\ntrue"
        ),
        "test_cases": [
            {"id": "tc-ll-l3-1", "stdin": "3 2 0 -4\n1", "expected_stdout": "true", "points": 7.5, "is_hidden": 0},
            {"id": "tc-ll-l3-2", "stdin": "1\n-1", "expected_stdout": "false", "points": 7.5, "is_hidden": 1},
        ],
    },

    # ==========================================================================
    # 6. TREES
    # ==========================================================================
    {
        "id": "question-dsa-tree-l1",
        "title": "Corporate Org Chart Management Hierarchy Depth",
        "domain": "Trees",
        "difficulty": "L1",
        "points": 5,
        "language": "python",
        "prompt": (
            "Scenario: An enterprise HR system represents managerial reporting chains as a binary tree where the CEO is at the root. "
            "Given the organization hierarchy in level-order format (with 'null' representing unfilled subordinate positions), "
            "determine the maximum management depth (number of levels from executive leadership to front-line contributors).\n\n"
            "Input format:\n"
            "A single line of space-separated tokens in level-order.\n\n"
            "Output format:\n"
            "An integer depth.\n\n"
            "Sample Input:\n3 9 20 null null 15 7\nSample Output:\n3"
        ),
        "test_cases": [
            {"id": "tc-tree-l1-1", "stdin": "3 9 20 null null 15 7", "expected_stdout": "3", "points": 2.5, "is_hidden": 0},
            {"id": "tc-tree-l1-2", "stdin": "1 null 2", "expected_stdout": "2", "points": 2.5, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-tree-l2",
        "title": "Autonomous Warehouse Drone Shelf Tier Scan",
        "domain": "Trees",
        "difficulty": "L2",
        "points": 10,
        "language": "python",
        "prompt": (
            "Scenario: An automated warehouse inventory drone scans vertical rack storage racks modeled as a binary tree. "
            "To synchronize the laser barcode scanner, the drone must report package barcodes level by level from the top tier down, "
            "printing each shelf level's items on a separate line.\n\n"
            "Input format:\n"
            "A single line of space-separated tree tokens in level-order (with 'null' for empty slots).\n\n"
            "Output format:\n"
            "Values on each shelf tier separated by spaces, one tier per line.\n\n"
            "Sample Input:\n3 9 20 null null 15 7\nSample Output:\n3\n9 20\n15 7"
        ),
        "test_cases": [
            {"id": "tc-tree-l2-1", "stdin": "3 9 20 null null 15 7", "expected_stdout": "3\n9 20\n15 7", "points": 5.0, "is_hidden": 0},
            {"id": "tc-tree-l2-2", "stdin": "1", "expected_stdout": "1", "points": 5.0, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-tree-l3",
        "title": "Distributed DNS Server Lowest Common Authority",
        "domain": "Trees",
        "difficulty": "L3",
        "points": 15,
        "language": "python",
        "prompt": (
            "Scenario: In a worldwide Domain Name System (DNS) namespace tree, network requests for two disparate domain endpoints p and q "
            "must be resolved by a mutual authoritative server. Find the Lowest Common Ancestor (LCA) node in the tree that manages both p and q.\n\n"
            "Input format:\n"
            "Line 1: Space-separated tree tokens in level-order\n"
            "Line 2: Two space-separated target server IDs p and q\n\n"
            "Output format:\n"
            "The ID value of the lowest common authority node.\n\n"
            "Sample Input:\n3 5 1 6 2 0 8 null null 7 4\n5 1\nSample Output:\n3"
        ),
        "test_cases": [
            {"id": "tc-tree-l3-1", "stdin": "3 5 1 6 2 0 8 null null 7 4\n5 1", "expected_stdout": "3", "points": 7.5, "is_hidden": 0},
            {"id": "tc-tree-l3-2", "stdin": "3 5 1 6 2 0 8 null null 7 4\n5 4", "expected_stdout": "5", "points": 7.5, "is_hidden": 1},
        ],
    },

    # ==========================================================================
    # 7. GRAPHS
    # ==========================================================================
    {
        "id": "question-dsa-graph-l1",
        "title": "Smart City Telemetry Hub Direct Link Degree",
        "domain": "Graphs",
        "difficulty": "L1",
        "points": 5,
        "language": "python",
        "prompt": (
            "Scenario: A municipal fiber optic network connects N telemetry junction hubs (labeled 0 to N-1) via M bidirectional cables. "
            "For bandwidth provisioning, compute the direct connection degree (number of connected cables) for each junction from 0 to N-1.\n\n"
            "Input format:\n"
            "Line 1: N M (integers)\n"
            "Next M lines: u v (cable connecting hub u and hub v)\n\n"
            "Output format:\n"
            "Space-separated connection degrees for hubs 0 through N-1.\n\n"
            "Sample Input:\n3 2\n0 1\n1 2\nSample Output:\n1 2 1"
        ),
        "test_cases": [
            {"id": "tc-graph-l1-1", "stdin": "3 2\n0 1\n1 2", "expected_stdout": "1 2 1", "points": 2.5, "is_hidden": 0},
            {"id": "tc-graph-l1-2", "stdin": "4 3\n0 1\n0 2\n0 3", "expected_stdout": "3 1 1 1", "points": 2.5, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-graph-l2",
        "title": "Social Network Isolated Community Cluster Detection",
        "domain": "Graphs",
        "difficulty": "L2",
        "points": 10,
        "language": "python",
        "prompt": (
            "Scenario: A social media intelligence engine analyzes friendship graphs on a university campus of N students (0 to N-1). "
            "Due to privacy preferences, certain student groups have no mutual ties with other groups. Using Breadth-First or Depth-First search, "
            "determine the total count of completely isolated, disjoint social communities (connected components).\n\n"
            "Input format:\n"
            "Line 1: N M (integers)\n"
            "Next M lines: u v (friendship edge between student u and v)\n\n"
            "Output format:\n"
            "An integer count of isolated communities.\n\n"
            "Sample Input:\n5 2\n0 1\n1 2\nSample Output:\n3"
        ),
        "test_cases": [
            {"id": "tc-graph-l2-1", "stdin": "5 2\n0 1\n1 2", "expected_stdout": "3", "points": 5.0, "is_hidden": 0},
            {"id": "tc-graph-l2-2", "stdin": "4 3\n0 1\n1 2\n2 3", "expected_stdout": "1", "points": 5.0, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-graph-l3",
        "title": "Emergency Medical Ambulance GPS Routing",
        "domain": "Graphs",
        "difficulty": "L3",
        "points": 15,
        "language": "python",
        "prompt": (
            "Scenario: An emergency 911 dispatch console calculates the lowest-latency transit route from an ambulance station S "
            "to a critical accident site D across a directed road grid with traffic delays (weights w). "
            "Implement Dijkstra's algorithm to compute the shortest travel time. If destination D is unreachable, output -1.\n\n"
            "Input format:\n"
            "Line 1: N M S D (integers)\n"
            "Next M lines: u v w (directed road segment from u to v with latency w)\n\n"
            "Output format:\n"
            "An integer representing the minimum travel time.\n\n"
            "Sample Input:\n4 4 0 3\n0 1 1\n1 2 2\n2 3 1\n0 3 5\nSample Output:\n4"
        ),
        "test_cases": [
            {"id": "tc-graph-l3-1", "stdin": "4 4 0 3\n0 1 1\n1 2 2\n2 3 1\n0 3 5", "expected_stdout": "4", "points": 7.5, "is_hidden": 0},
            {"id": "tc-graph-l3-2", "stdin": "3 2 0 2\n0 1 4\n1 2 3", "expected_stdout": "7", "points": 7.5, "is_hidden": 1},
        ],
    },

    # ==========================================================================
    # 8. DYNAMIC PROGRAMMING
    # ==========================================================================
    {
        "id": "question-dsa-dp-l1",
        "title": "Mars Exploration Rover Stepping Motor Configurations",
        "domain": "Dynamic Programming",
        "difficulty": "L1",
        "points": 5,
        "language": "python",
        "prompt": (
            "Scenario: An autonomous Mars rover climbs an incline of n geological rock steps. "
            "Its robotic articulation allows it to stride either 1 or 2 steps per motor cycle. "
            "Calculate how many unique stride sequences can deliver the rover to the top of step n.\n\n"
            "Input format:\n"
            "A single integer n (1 <= n <= 45).\n\n"
            "Output format:\n"
            "An integer denoting distinct traversal configurations.\n\n"
            "Sample Input:\n2\nSample Output:\n2"
        ),
        "test_cases": [
            {"id": "tc-dp-l1-1", "stdin": "2", "expected_stdout": "2", "points": 2.5, "is_hidden": 0},
            {"id": "tc-dp-l1-2", "stdin": "3", "expected_stdout": "3", "points": 2.5, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-dp-l2",
        "title": "Smart Banking ATM Cash Dispenser Currency Optimization",
        "domain": "Dynamic Programming",
        "difficulty": "L2",
        "points": 10,
        "language": "python",
        "prompt": (
            "Scenario: An automated bank ATM vault holds infinite reserves of several paper currency bill denominations. "
            "When a customer enters a withdrawal amount A, the ATM cash dispenser must minimize mechanical bill transfers "
            "by dispensing the exact amount with the fewest total bills. If the amount cannot be formed, return -1.\n\n"
            "Input format:\n"
            "Line 1: Target cash withdrawal amount A\n"
            "Line 2: Space-separated available bill denominations\n\n"
            "Output format:\n"
            "An integer bill count.\n\n"
            "Sample Input:\n11\n1 2 5\nSample Output:\n3"
        ),
        "test_cases": [
            {"id": "tc-dp-l2-1", "stdin": "11\n1 2 5", "expected_stdout": "3", "points": 5.0, "is_hidden": 0},
            {"id": "tc-dp-l2-2", "stdin": "3\n2", "expected_stdout": "-1", "points": 5.0, "is_hidden": 1},
        ],
    },
    {
        "id": "question-dsa-dp-l3",
        "title": "Commercial Satellite Rocket Payload Value Maximization",
        "domain": "Dynamic Programming",
        "difficulty": "L3",
        "points": 15,
        "language": "python",
        "prompt": (
            "Scenario: A commercial space launch vehicle has a strict payload weight capacity W kilograms. "
            "Mission control has N science instruments, each with a known mass and scientific value. "
            "Select the combination of instruments that yields the maximum total mission value without exceeding launch payload capacity W.\n\n"
            "Input format:\n"
            "Line 1: Launch payload capacity W and number of candidate instruments N\n"
            "Line 2: N space-separated instrument scientific values\n"
            "Line 3: N space-separated instrument masses in kg\n\n"
            "Output format:\n"
            "An integer denoting maximum achievable scientific value.\n\n"
            "Sample Input:\n4 3\n1 2 3\n4 5 1\nSample Output:\n3"
        ),
        "test_cases": [
            {"id": "tc-dp-l3-1", "stdin": "4 3\n1 2 3\n4 5 1", "expected_stdout": "3", "points": 7.5, "is_hidden": 0},
            {"id": "tc-dp-l3-2", "stdin": "50 3\n60 100 120\n10 20 30", "expected_stdout": "220", "points": 7.5, "is_hidden": 1},
        ],
    },
]


def seed_domain_questions() -> None:
    """Populate database with rich scenario-based DSA questions across 8 domains and 3 difficulty tiers."""
    with get_connection() as connection:
        # Re-tag starter questions with scenario-based titles
        connection.execute(
            """
            UPDATE questions
            SET title = 'Cashier Checkout Dual-Item Subtotal',
                prompt = 'Scenario: A retail point-of-sale scanner scans two barcode prices and prints the combined bill subtotal.\n\nInput format:\nTwo space- or newline-separated integers.\n\nOutput format:\nTheir integer sum.',
                domain = 'Arrays',
                difficulty = 'L1'
            WHERE id = 'question-test-001'
            """
        )
        connection.execute(
            """
            UPDATE questions
            SET title = 'Cloud Server Telemetry Peak CPU Spike Detector',
                prompt = 'Scenario: A cloud infrastructure monitoring daemon tracks server CPU loads and must detect the maximum peak spike observed.\n\nInput format:\nLine 1: Server count N\nLine 2: N space-separated CPU load values\n\nOutput format:\nMaximum CPU integer.',
                domain = 'Arrays',
                difficulty = 'L1'
            WHERE id = 'question-test-002'
            """
        )
        connection.execute(
            """
            UPDATE questions
            SET title = 'Biochemical DNA Strand Palindromic Symmetry Validator',
                prompt = 'Scenario: A bioinformatics research lab verifies whether a DNA nucleotide sequence has palindromic symmetry for restriction enzyme cleavage.\n\nInput format:\nA single line with alphanumeric DNA sequence.\n\nOutput format:\n\"true\" if palindromic, \"false\" otherwise.',
                domain = 'Strings',
                difficulty = 'L1'
            WHERE id = 'question-test-003'
            """
        )

        # Seed all 24 scenario-based questions
        for q in DSA_SCENARIO_QUESTIONS:
            connection.execute(
                """
                INSERT INTO questions (id, title, prompt, language, points, difficulty, domain)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    prompt = excluded.prompt,
                    language = excluded.language,
                    points = excluded.points,
                    difficulty = excluded.difficulty,
                    domain = excluded.domain
                """,
                (
                    q["id"],
                    q["title"],
                    q["prompt"],
                    q["language"],
                    q["points"],
                    q["difficulty"],
                    q["domain"],
                ),
            )

            # Seed test cases
            for tc in q.get("test_cases", []):
                connection.execute(
                    """
                    INSERT INTO test_cases (id, question_id, stdin, expected_stdout, points, is_hidden)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        question_id = excluded.question_id,
                        stdin = excluded.stdin,
                        expected_stdout = excluded.expected_stdout,
                        points = excluded.points,
                        is_hidden = excluded.is_hidden
                    """,
                    (
                        tc["id"],
                        q["id"],
                        tc["stdin"],
                        tc["expected_stdout"],
                        tc["points"],
                        tc["is_hidden"],
                    ),
                )
