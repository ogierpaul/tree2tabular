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

| TXT_CATEGORY_LVL1   | TXT_CATEGORY_LVL2   | TXT_CATEGORY_LVL3   | DIM_CATEGORY_LVL1   | DIM_CATEGORY_LVL2   | DIM_CATEGORY_LVL3   |
|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|
| subcategory         | subsubcategory      | subsubsubcategory   | 7690c4              | 163eed              | 6d0573              |
| subcategory2        | subsubcategory2     | subsubcategory2     | 3860c7              | e7921e              | e7921e              |

## Others methods
### Re-use as a dataframe:
```python
df = tree.to_dataframe()
```

### Export a new yaml file with ids:
```python
tree.to_yaml('my_tree_with_ids.yaml')
```



## Usage requirements:
### Yaml structure
* Always start with the keyword 'Hierarchy'
* Provide under `Hierarchy` the following parameters: `name`, `id_generation`, `childs`
* Each node can have three properties: `name`, `id`, `childs`
    * The `childs` property is a list of nodes, can be null if no child nodes
    * The `id` property is optional, if not provided, it will be generated based on the `id_generation` parameter
    * The `name` property is mandatory

### name parameter
* At the top of the hierarchy: is the name of the dimension used as column for the tabular data
    * e.g. `name: category` will generate the columns `DIM_CATEGORY_LVL1`, `DIM_CATEGORY_LVL2`, etc.
* Inside the hierarchy: is the name of the node

### id_generation parameter
* uuid: generate a unique id for each node if no id provided
* name: use the name of the node as id if no id provided
* error: raise an error if no id provided

### Output structure
#### Creation of column names using the `name` parameter
* The output is a tabular structure with the following columns: `DIM_CATEGORY_LVL1`, `DIM_CATEGORY_LVL2`, etc. and `TXT_CATEGORY_LVL1`, `TXT_CATEGORY_LVL2`, etc.
* The `DIM_` columns contain the ids of the nodes.
* The `TXT_` columns contain the names of the nodes.
  
#### The higher the level, the deeper the node
* The **level 1 corresponds to the top of the hierarchy**, the highest the level, the deeper the node is in the hierarchy
* The **primary key** of the table is the `DIM_` columns with the highest level, and the highest granularity.
* There is no blank: if a node has no child, the `DIM_` and `TXT_` columns of the lowest level are filled with the id and name of the node

### Example
You can find examples in the `tests` > `demos*` folders.



