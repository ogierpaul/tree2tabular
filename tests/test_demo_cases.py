from tree2tabular import TreeBuilder
import os

import yaml

def handle_case(fd):
    fn = 'input_hierarchy.yml'
    fd = os.path.join(os.path.dirname(os.path.abspath(__file__)), fd)
    csv_output = 'tabular_hierarchy.csv'
    yaml_output = 'hierarchy_with_ids.yml'
    tree = TreeBuilder.from_yaml(os.path.join(fd, fn))
    tree.to_yaml(os.path.join(fd, yaml_output), overwrite=True)
    tree.to_csv(os.path.join(fd, csv_output), overwrite=True)
    return True
def test_case_readme():
    assert handle_case('demo_readme')

def test_case_no_id_provided():
    assert handle_case('demo_no_id_provided')

def test_case_id_provided():
    assert handle_case('demo_id_provided')

def test_case_some_id_provided():
    assert handle_case('demo_some_id_provided')

def test_case_id_incremental():
    assert handle_case('demo_id_incremental')





    #
    #
    #
    # # usage:
    #
    #
    # with open() as yaml_file:
    #
    # # df = tree.to_tabular()
    # # df.to_csv('airbus_hierarchy.csv', index=False)
