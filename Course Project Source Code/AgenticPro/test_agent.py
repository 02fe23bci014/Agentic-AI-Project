from backend.agents.test_case_agent import TestCaseAgent

agent = TestCaseAgent()

public_case = agent.create_test_case(
    input_data="5\n10 20 30 40 50",
    expected_output="50",
    test_type="public"
)

hidden_case = agent.create_test_case(
    input_data="4\n-5 -2 -10 -1",
    expected_output="-1",
    test_type="hidden"
)

edge_case = agent.create_test_case(
    input_data="1\n100",
    expected_output="100",
    test_type="edge"
)

print(public_case)
print(hidden_case)
print(edge_case)