from backend.tools.test_case_tool import TestCaseTool

tool = TestCaseTool()

public_case = tool.create_test_case(
    input_data="5\n10 20 30 40 50",
    expected_output="50",
    test_type="public"
)

hidden_case = tool.create_test_case(
    input_data="4\n-5 -2 -10 -1",
    expected_output="-1",
    test_type="hidden"
)

edge_case = tool.create_test_case(
    input_data="1\n100",
    expected_output="100",
    test_type="edge"
)

boundary_case = tool.create_test_case(
    input_data="1000\n1 2 3 ...",
    expected_output="1000",
    test_type="boundary"
)

print(public_case)
print(hidden_case)
print(edge_case)
print(boundary_case)

print(tool.validate_test_case(public_case))