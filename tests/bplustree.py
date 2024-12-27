from csv import excel

import pytest

from toolbox.bst import BPlusTree, BPlusTreeNode


def b_plus_tree_node(is_leaf, keys, children):
    node = BPlusTreeNode(is_leaf=is_leaf)

    node.keys = keys
    node.children = children

    return node


@pytest.mark.parametrize(
    "key, expected",
    [
        (0, None),  # in root
        (1, [1, 2, 3]),  # duplicate
        (2, [1, 2, 3]),  # duplicate
        (3, [1, 2, 3]),  # duplicate
        (4, None),  # in root
    ],
)
def test_search_root_is_leaf(key, expected):
    tree = BPlusTree(degree=4)
    tree.root.keys = [1, 2, 3]
    tree.root.children = []

    node = tree.search(key)

    if expected is None:
        assert node is None
    else:
        assert node.keys == expected


@pytest.mark.parametrize(
    "key, expected",
    [
        (0, None),  # add in first leaf
        (1, [1, 2]),  # already in first leaf
        (1.5, None),  # in first leaf
        (3, [3, 4]),  # in second leaf
        (3.5, None),  # in second leaf
        (5, [5, 6]),  # in third leaf
        (7, None),  # out of bounds
    ],
)
def test_search_one_root_three_leaves(key, expected):
    """
    Given a tree with one root and three leaves:
    [3, 5]
    [1, 2] [3, 4] [5, 6]
    """
    tree = BPlusTree(degree=4)
    tree.root.is_leaf = False

    first_leaf = BPlusTreeNode(is_leaf=True)
    first_leaf.keys = [1, 2]

    second_leaf = BPlusTreeNode(is_leaf=True)
    second_leaf.keys = [3, 4]

    third_leaf = BPlusTreeNode(is_leaf=True)
    third_leaf.keys = [5, 6]

    tree.root.keys = [3, 5]
    tree.root.children = [first_leaf, second_leaf, third_leaf]

    res = tree.search(key)
    if expected is None:
        assert res is None
    else:
        assert res.keys == expected


@pytest.mark.parametrize(
    "key, expected",
    [
        (0, None),  # out of bounds
        (1, [1]),  # in first leaf
        (1.5, None),
        (2, [2]),  # in first leaf
        (3, [3]),  # in second leaf
        (3.5, None),
        (4, [4, 5]),  # in third leaf
        (5, [4, 5]),  # in third leaf
        (6, None),  # out of bounds
    ],
)
def test_search_one_root_two_internal_and_five_leaves(key, expected):
    """
    [3]
    [2] [4]
    [1] [2] [3] [4, 5]
    :return:
    """
    tree = BPlusTree(degree=3)
    tree.root.is_leaf = False

    leaves = [
        b_plus_tree_node(is_leaf=True, keys=[1], children=[]),
        b_plus_tree_node(is_leaf=True, keys=[2], children=[]),
        b_plus_tree_node(is_leaf=True, keys=[3], children=[]),
        b_plus_tree_node(is_leaf=True, keys=[4, 5], children=[]),
    ]

    internals = [
        b_plus_tree_node(is_leaf=False, keys=[2], children=[leaves[0], leaves[1]]),
        b_plus_tree_node(is_leaf=False, keys=[4], children=[leaves[2], leaves[3]]),
    ]

    root = b_plus_tree_node(is_leaf=False, keys=[3], children=internals)
    tree.root = root

    res = tree.search(key)
    if expected is None:
        assert res is None
    else:
        assert res.keys == expected


def test_insert_root_leaf_no_overflow():
    tree = BPlusTree(degree=3)
    tree.root.is_leaf = True

    tree.insert(1)
    tree.insert(2)

    assert tree.root.keys == [1, 2]


def test_insert_root_leaf_overflow():
    """
    from:
    [1, 2, 3]

    to:
    [2]
    [1] [2, 3]

    then from:
    [2]
    [1] [2, 3, 4]

    to:
    [2, 3]
    [1] [2] [3, 4]

    then from:
    [2, 3]
    [1] [2] [3, 4, 5]

    to:
    [3]
    [2] [4]
    [1] [2] [3] [4, 5]
    """
    tree = BPlusTree(degree=3)

    for i in range(1, 6):
        tree.insert(i)

    assert tree.root.keys == [3]
    assert tree.root.children[0].keys == [2]
    assert tree.root.children[1].keys == [4]
    assert tree.root.children[0].children[0].keys == [1]
    assert tree.root.children[0].children[1].keys == [2]
    assert tree.root.children[1].children[0].keys == [3]
    assert tree.root.children[1].children[1].keys == [4, 5]


def test_delete_redistribute_same_parent_right_has_more_keys():
    tree = BPlusTree(degree=4)

    for i in [1, 4, 7, 10, 13, 16, 18, 19, 25, 28, 29]:
        tree.insert(i)

    assert tree.root.children[1].keys == [28]
    assert tree.root.children[1].children[0].keys == [18, 25]
    assert tree.root.children[1].children[1].keys == [28, 29]


def test_delete_redistribute_same_parent_left_has_more_keys():
    tree = BPlusTree(degree=4)

    for i in [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31]:
        tree.insert(i)

    tree.delete(28)
    tree.insert(20)

    # Make sure the tree is correct
    assert tree.root.children[1].children[0].keys == [19, 20, 22]
    assert tree.root.children[1].children[1].keys == [25, 31]

    tree.delete(25)

    assert tree.root.children[1].keys == [22]
    assert tree.root.children[1].children[0].keys == [19, 20]
    assert tree.root.children[1].children[1].keys == [22, 31]
