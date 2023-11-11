from typing import List, Dict


class BaseNode:
    name: str


class Node(BaseNode):
    children: str


class HierarchyNode(Node):
    parent: BaseNode

    def add_parent(self, parent):
        self.parent = parent


class MultiHeirarchyNode(Node):
    parents: Dict[str, BaseNode]

    def add_parent(self, parent):
        self.parents[parent.__name__] = parent


class RootNode(Node):
    children: BaseNode


class TerminalNode(BaseNode):
    parent: BaseNode
