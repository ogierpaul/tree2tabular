from tree2tabular import TreeBuilder
import os
import  pytest

@pytest.fixture
def directory_of_tests():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exception_cases')

def test_id_generation_wrong_value(directory_of_tests):
    with pytest.raises(ValueError) as e_info:
        TreeBuilder.from_yaml(os.path.join(directory_of_tests, 'id_generation_wrong.yml'))
    pass