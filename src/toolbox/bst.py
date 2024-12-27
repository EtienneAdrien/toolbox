from typing import Self


class BPlusTreeError(Exception):
    pass


class BPlusTreeNodeNotFoundError(BPlusTreeError):
    pass


class BPlusTreeNodeDuplicateError(BPlusTreeError):
    pass


class BPlusTreeNode:
    def __init__(
        self,
        is_leaf=False,
        keys: list | None = None,
        parent: Self | None = None,
        left: Self | None = None,
        right: Self | None = None,
    ):
        self.is_leaf = is_leaf
        self.keys = keys or []
        self.children = []
        self.parent = parent
        self.left = left
        self.right = right

    # def __repr__(self):
    #     return (
    #         f"BPlusTreeNode(is_leaf={self.is_leaf}, keys={self.keys}, left={self.left.keys}, right={self.right.keys})"
    #     )


class BPlusTree:
    def __init__(self, degree: int):
        self.root = BPlusTreeNode(is_leaf=True)
        self.degree = degree
        self.minimum_occupancy = self.degree // 2

    def __str__(self):
        return self.print_tree()

    def __repr__(self):
        return self.print_tree()

    def _search(
        self,
        key: int,
        raise_on_duplicate: bool,
        raise_on_not_found: bool,
    ) -> tuple[BPlusTreeNode | None, int | None]:
        node = self.root
        pos_in_parent = None

        while not node.is_leaf:
            parent = node

            for index, node_key in enumerate(node.keys):
                if key < node_key:
                    node = node.children[index]
                    node.parent = parent
                    pos_in_parent = index
                    break
            else:
                node = node.children[-1]
                node.parent = parent
                pos_in_parent = len(parent.children) + 1

        is_in_node = key in node.keys

        if raise_on_duplicate and is_in_node:
            raise BPlusTreeNodeDuplicateError(f"Key {key} is already in the tree and {raise_on_duplicate=}")

        if raise_on_not_found and not is_in_node:
            raise BPlusTreeNodeNotFoundError(f"Key {key} is not in the tree and {raise_on_not_found=}")

        return node, pos_in_parent

    def search(self, key: int):
        try:
            return self._search(key=key, raise_on_duplicate=False, raise_on_not_found=True)[0]
        except BPlusTreeNodeNotFoundError:
            return None

    def _find_where_to_insert(self, key: int):
        return self._search(key=key, raise_on_duplicate=True, raise_on_not_found=False)

    def _find_where_to_delete(self, key: int):
        return self._search(key=key, raise_on_duplicate=False, raise_on_not_found=True)

    def _is_node_free(self, node: BPlusTreeNode):
        return len(node.keys) < self.degree

    def _handle_overflow(self, node: BPlusTreeNode, pos: int | None = None):
        if self._is_node_free(node=node):
            return

        ## Split the node in two
        # Get the middle key
        middle_key = len(node.keys) // 2
        # Split the keys in two
        left_keys, right_keys = node.keys[:middle_key], node.keys[middle_key:]
        # Assign the left keys to the current node
        node.keys = left_keys
        # If the node is not a leaf, remove the middle key from the right keys
        # if not node.is_leaf:
        #     right_keys = right_keys[1:]
        # Create a new node and assign the right keys
        new_node = BPlusTreeNode(is_leaf=node.is_leaf, keys=right_keys, parent=node.parent, left=node)
        node.right = new_node

        ## Create parent if needed
        if node.parent is None:
            parent = BPlusTreeNode(is_leaf=False)
            parent.children = [node, new_node]
            node.parent = parent
            self.root = parent
        else:
            parent = node.parent
            parent.children.insert(pos + 1, new_node)

        # Add the middle key to the parent
        parent.keys.append(new_node.keys[0])
        parent.keys.sort()

        if not node.is_leaf:
            new_node.keys = new_node.keys[1:]

            # Split children from the current node
            left_children, right_children = node.children[: middle_key + 1], node.children[middle_key + 1 :]
            # Assign the left children to the current node
            node.children = left_children
            # Create a new node and assign the right children
            new_node.children = right_children

        self._handle_overflow(node=parent, pos=pos)

    def insert(self, key: int):
        if self.root.is_leaf:
            node = self.root
            pos = None

        else:
            node, pos = self._find_where_to_insert(key=key)

        node.keys.append(key)
        node.keys.sort()

        self._handle_overflow(node=node, pos=pos)

    def _handle_redistribution(
        self,
        left_node: BPlusTreeNode,
        right_node: BPlusTreeNode,
        node: BPlusTreeNode,
        key: int,
    ):
        original_first_right_keys = right_node.keys[0]

        node.keys.remove(key)

        keys = [*left_node.keys, *right_node.keys]

        middle_key = len(keys) // 2
        left_keys, right_keys = keys[:middle_key], keys[middle_key:]

        left_node.keys = left_keys
        right_node.keys = right_keys

        parent_key_index = left_node.parent.keys.index(original_first_right_keys)
        left_node.parent.keys[parent_key_index] = right_keys[0]

    def _handle_rebalancing(self, key: int, node: BPlusTreeNode):
        left_node = None
        right_node = None

        if len(node.left.keys) > self.minimum_occupancy:
            left_node = node.left
            right_node = node
        elif len(node.right.keys) > self.minimum_occupancy:
            left_node = node
            right_node = node.right

        self._handle_redistribution(
            left_node=left_node,
            right_node=right_node,
            node=node,
            key=key,
        )

    def delete(self, key: int):
        # Find on which node delete the key
        node, pos = self._find_where_to_delete(key=key)

        # End of the simplest case
        if len(node.keys) > self.minimum_occupancy:
            # Delete the key from the leaf node
            node.keys.remove(key)
            return

        # Handle rebalancing
        self._handle_rebalancing(key=key, node=node)

    def print_tree(self, node: BPlusTreeNode | None = None, level: int = 0):
        if node is None:
            node = self.root

        print(" " * (level * 4) + f"Keys: {node.keys}, IsLeaf: {node.is_leaf}")
        if not node.is_leaf:
            for child in node.children:
                self.print_tree(child, level + 1)


if __name__ == "__main__":
    tree = BPlusTree(degree=3)

    for i in [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31]:
        tree.insert(i)

    tree.print_tree()
