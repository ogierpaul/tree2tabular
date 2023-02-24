from tree2tabular import TreeBuilder
import os
import pytest

@pytest.fixture
def directory_of_tests():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parent_child')

def test_parent_child(directory_of_tests):
    tree = TreeBuilder.from_yaml(os.path.join(directory_of_tests, 'input_hierarchy.yml'))
    df_with_ids = tree.to_parent_child(use_names=False)
    df_with_ids.to_csv(os.path.join(directory_of_tests, 'parent_child_ids.csv'), index=False)
    df_with_names = tree.to_parent_child(use_names=True)
    df_with_names.to_csv(os.path.join(directory_of_tests, 'parent_child_names.csv'), index=False)