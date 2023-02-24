from tree2tabular import TreeBuilder
import os
import  pytest

@pytest.fixture
def directory_of_tests():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exception_cases')

def test_id_generation_wrong(directory_of_tests):
    with pytest.raises(ValueError) as e_info:
        TreeBuilder.from_yaml(os.path.join(directory_of_tests, 'id_generation_wrong.yml'))
    pass

def test_missing_id(directory_of_tests):
    with pytest.raises(KeyError) as e_info:
        TreeBuilder.from_yaml(os.path.join(directory_of_tests, 'missing_id.yml'))
    pass

def test_duplicate_names(directory_of_tests):
    with pytest.raises(KeyError) as e_info:
        TreeBuilder.from_yaml(os.path.join(directory_of_tests, 'duplicate_names.yml'))
    pass

def test_duplicate_ids(directory_of_tests):
    with pytest.raises(KeyError) as e_info:
        TreeBuilder.from_yaml(os.path.join(directory_of_tests, 'duplicate_ids.yml'))
    pass