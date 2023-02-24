# tree2tabular
# ===============
# Purpose:
Convert a tree structure to a tabular format.    
Wrapper around [treelib](https://github.com/caesar0301/treelib) with a few additional features geared towards easier data modelling for analytics engineers.    

# Abstract:
* Tree structures are often used to represent hierarchical data. However, they are not always easy to work with. This script converts a tree structure from a yaml file to a tabular format.    
* The script can also be used to generate unique ids for each node in the tree.
* It reads from a `yaml` file and writes to a `csv` file or updated `yml` file with ids.    

# Usage:
The `yaml` file should have the structure described below:    


```yaml
Hierarchy: #Always start the yaml file with this line``
    name: category # This is the name of the dimension used as column for the tabular data
    id_generation: uuid # Use one of those: uuid, name, or error
    # Keep this structure for the nodes
    childs:
        - name: subcategory
          childs:
              - name: subsubcategory
                childs:
                    - name: subsubsubcategory
        - name: subcategory2
          childs:
              - name: subsubcategory2
```

in python write:    

```python
from tree2tabular import TreeBuilder
fn = 'my_tree.yaml'
tree = TreeBuilder.from_yaml(fn)
tree.to_csv('my_tree.csv')

```

output: automatically generated ids and tree in tabular structure:    

|    | DIM_CATEGORY_LVL1   | DIM_CATEGORY_LVL2   | DIM_CATEGORY_LVL3   | TXT_CATEGORY_LVL1   | TXT_CATEGORY_LVL2   | TXT_CATEGORY_LVL3   |
|---:|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|
|  0 | d13358              | 75e8bd              | df14ab              | subcategory         | subsubcategory      | subsubsubcategory   |
|  1 | 193e3e              | 7f9f4f              | 7f9f4f              | subcategory2        | subsubcategory2     | subsubcategory2     |

## Others methods
Re-use as a dataframe:
```python
df = tree.to_dataframe()
```

Export a new yaml file with ids:
```python
tree.to_yaml('my_tree_with_ids.yaml')
```

## Basic usage
### Yaml structure
* Always start with the keyword 'Hierarchy'
* Provide under `Hierarchy` the following parameters: `name`, `id_generation`, `childs`
* Each node has three properties: `name`, `id`, `childs`

### name parameter
* At the top of the hierarchy: is the name of the dimension used as column for the tabular data
    * e.g. `name: category` will generate the columns `DIM_CATEGORY_LVL1`, `DIM_CATEGORY_LVL2`, etc.
* Inside the hierarchy: is the name of the node

### id_generation parameter
* uuid: generate a unique id for each node if no id provided
* name: use the name of the node as id if no id provided
* error: raise an error if no id provided

### Output structure
* The output is a tabular structure with the following columns: `DIM_CATEGORY_LVL1`, `DIM_CATEGORY_LVL2`, etc. and `TXT_CATEGORY_LVL1`, `TXT_CATEGORY_LVL2`, etc.
* The `DIM_` columns contain the ids of the nodes
* The `TXT_` columns contain the names of the nodes
* There is no blank: if a node has no child, the `DIM_` and `TXT_` columns of the lowest level are filled with the id and name of the node

### Example
You can find examples in the `tests` > `demos*` folders.



