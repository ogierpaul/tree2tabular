import pandas as pd
import yaml
import os
import uuid
from treelib import Tree
from collections import OrderedDict
from yaml import SafeDumper


def _ordered_dump(data, stream=None, Dumper=yaml.SafeDumper, **kwds):
    ## FROM: https://stackoverflow.com/questions/10648614/dump-in-pyyaml-as-utf-8
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, allow_unicode=True, **kwds)

def _load_yaml(fn:str) ->dict:
    with open(fn) as f:
        d = yaml.safe_load(f)
    return d

class TreeBuilder(object):
    def __init__(self, d:dict):
        self._generation_possible_values = ['name', 'uuid' ,'error', 'incremental']
        self._identifiers = []
        self.d = d
        if d.get('Hierarchy') is None:
            raise (ValueError('Hierarchy key not found in yaml file'))
        if d['Hierarchy'].get('id_generation') is None:
            raise (ValueError('id_generation key not found in yaml file'))
        if d['Hierarchy'].get('childs') is None:
            raise (ValueError('childs key not found in yaml file'))
        self.id_generation = d['Hierarchy']['id_generation']
        if self.id_generation not in self._generation_possible_values:
            raise (ValueError(
                f"""id_generation {self.id_generation} not supported, must be one of {self._generation_possible_values}"""
            ))
        self._map_identifiers_from_dict(d['Hierarchy']['childs'])
        if self.id_generation == 'incremental':
            self._identifiers = [self._to_integer(x) for x in self._identifiers]
        self.tree = Tree()
        self.tree.create_node('Root', 0)
        self.dim_name = d['Hierarchy']['name']
        self._build()

    def _to_integer(self, x)->int:
        if isinstance(x, int):
            child_id = x
        elif isinstance(x, str) and x.isdigit():
            child_id = int(x)
        else:
            raise (ValueError(f""" with id_generation {self.id_generation} id must be an integer"""))
        return child_id

    def _map_identifiers_from_dict(self, children) ->list:
        for child in children:
            if child.get('id') is not None:
                if child.get('id') == 0:
                    raise KeyError(f"""id 0 is reserved for root node""")
                self._identifiers.append(child.get('id'))
            if child.get('childs') is not None:
                self._map_identifiers_from_dict(child.get('childs'))

    @classmethod
    def from_yaml(cls, fn:str):
        return cls(_load_yaml(fn))

    def _increment_identifier(self):
        if self.id_generation == 'incremental':
            if len(self._identifiers) == 0:
                return 1
            else:
                return max(self._identifiers) + 1

    def _explore_sub_level(self, parent_id:str, childs:dict):
        for c in childs:
            if c.get('name') is None:
                raise (KeyError(f"""No name provided for node id {c.get('id')}: \
                 under parent id {parent_id} and parent name {self.tree.get_node(parent_id).tag}"""))
            if c.get('id') is None:
                if self.id_generation == 'name':
                    child_id = c.get('name')
                elif self.id_generation == 'uuid':
                    child_id = str(uuid.uuid4())[:6]
                elif self.id_generation == 'error':
                    raise (KeyError(f"""No id provided for node name {c.get('name')}"""))
                elif self.id_generation == 'incremental':
                    child_id = self._increment_identifier()
                else:
                    raise (ValueError(f"""id_generation {self.id_generation} not supported, must be one of {self._generation_possible_values}"""))
            else:
                if self.id_generation == 'incremental':
                    child_id = self._to_integer(c.get('id'))
                else:
                    child_id = c.get('id')
            if self.tree.get_node(child_id) is not None:
                new_node_name = c.get('name')
                existing_node_name = self.tree.get_node(child_id).tag
                raise (KeyError(f"""Node identifier {child_id} is not unique, \
                please check your hierarchy for node names {new_node_name} and {existing_node_name}"""))
            self.tree.create_node(c.get('name'), child_id, parent=parent_id)
            self._identifiers.append(child_id)
            if c.get('childs') is not None:
                self._explore_sub_level(child_id, c.get('childs'))

    def _build(self):
        self._explore_sub_level(0, self.d.get('Hierarchy').get('childs'))
        return self.tree

    def to_dataframe(self) ->pd.DataFrame:
        n_levels = self.tree.depth()
        df = pd.DataFrame(self.tree.paths_to_leaves())
        key_columns = [f'DIM_{self.dim_name.upper()}_LVL{i + 1}' for i in range(n_levels)]
        txt_columns = [f'TXT_{self.dim_name.upper()}_LVL{i + 1}' for i in range(n_levels)]
        for i in range(n_levels):
            df[i + 1] = df[i + 1].fillna(df[i])
            df[txt_columns[i]] = df[i + 1].map(lambda x: self.tree.get_node(x).tag)
        if df[n_levels].nunique() != df.shape[0]:
            raise (ValueError(f"""Duplicate values in column {n_levels}"""))
        df.rename(columns=dict(zip(range(1, n_levels + 1), key_columns)), inplace=True)
        df = df[txt_columns + key_columns] # reorder columns and remove first column
        return df

    def to_csv(self, fn:str, overwrite:bool = False, **kwargs):
        df = self.to_dataframe()
        if not overwrite:
            if os.path.exists(fn):
                raise (FileExistsError(f"""File {fn} already exists"""))
        df.to_csv(fn, index=False,**kwargs)
        return None


    def to_ordered_dict(self) -> OrderedDict:
        output = OrderedDict()
        output['Hierarchy'] = OrderedDict()
        output['Hierarchy']['name'] = self.dim_name
        output['Hierarchy']['id_generation'] = self.id_generation
        output['Hierarchy']['childs'] = self._list_children()
        return output

    def to_dict(self) -> dict:
        return dict(self.to_ordered_dict())

    def to_yaml(self, fn:str, overwrite:bool=False):
        if os.path.exists(fn) and not overwrite:
            raise (FileExistsError(f"""File {fn} already exists"""))
        else:
            with open(fn, 'w') as f:
                s = _ordered_dump(self.to_ordered_dict(), f)
        return None

    def _list_children(self, nid=None):
        childs = []
        nid = self.tree.root if (nid is None) else nid
        if self.tree[nid].expanded:
            children = [self.tree[i] for i in self.tree[nid].successors(self.tree._identifier)]
            children.sort(key=lambda x: x.tag)
            for child in children:
                cd = OrderedDict()
                cd['name'] = child.tag
                cd['id'] = child.identifier
                cdc = self._list_children(child.identifier)
                if cdc is not None:
                    cd['childs'] = self._list_children(child.identifier)
                childs.append(cd)
        if len(childs) == 0:
            childs = None
        return childs


    def to_parent_child(self, use_names=False) -> pd.DataFrame:
        y = pd.Series(name='parent_id', dtype='object')
        y.index.name='child_id'
        child_ids = self.tree.nodes.keys()
        # child_ids = [i for i in child_ids if i != 0]
        for child_id in child_ids:
            level = self.tree.level(child_id)
            parent = self.tree.ancestor(child_id, level -1)
            parent_id = parent.identifier
            y.loc[child_id] = parent_id
            if parent_id is None:
                raise (ValueError(f"""Parent id is None for child id {child_id}"""))
            if child_id is None:
                raise (ValueError(f"""Child id is None for parent id {parent_id}"""))
        df = pd.DataFrame(y).reset_index(drop=False)
        if use_names:
            df['parent_name'] = df['parent_id'].map(lambda ix: self.tree[ix].tag)
            df['child_name'] = df['child_id'].map(lambda ix: self.tree[ix].tag)
            df = df[['parent_name', 'child_name']]
        else:
            df = df[['parent_id', 'child_id']]
        return df






