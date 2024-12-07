from pathlib import Path

from suffix_tree.SuffixTreeNode import SuffixTreeNode
from seek_file import SeekFile


class MemorySuffixTree:
    """An in-memory suffix tree for storing and searching substrings of a given text. Has functionality to
    serialize/deserialize to disk and output to a DOT graph file.

    Attributes:
        root (SuffixTreeNode): The root node of the suffix tree.
        text (str): The original text for which the suffix tree is constructed.
    """

    def __init__(self, text: str = None) -> None:
        """Initializes the suffix tree with the given text.

        Args:
            text (str): The text to construct the suffix tree from.
        """
        self.root: SuffixTreeNode
        self.text: str
        if text:
            self.root = SuffixTreeNode()
            self.text = text
            self.build_suffix_tree()
        else:
            self.root = None
            self.text = None

    def build_suffix_tree(self) -> None:
        """Constructs the suffix tree by inserting all suffixes of the text."""
        for i in range(len(self.text)):
            self.insert_suffix(self.text[i:], i)

    def insert_suffix(self, suffix: str, index: int) -> None:
        """Inserts a suffix into the suffix tree.

        Args:
            suffix (str): The suffix to insert.
            index (int): The starting index of the suffix in the original text.
        """
        current_node = self.root
        depth = index
        # current_node.indexes.append((index, index + len(suffix) - 1))  # Store the index of the suffix
        for char in suffix:
            if char not in current_node.children:
                current_node.children[char] = SuffixTreeNode()
            current_node = current_node.children[char]
            current_node.indexes.append((index, depth))  # Store the index at each node
            depth += 1

    def search(self, pattern: str) -> list[tuple[int, int]]:
        """Searches for a pattern in the suffix tree.

        Args:
            pattern (str): The substring to search for.

        Returns:
            List[Tuple[int, int]]: A list of tuples, each containing the start and end indices (inclusive)
            of the pattern in the original text. Returns an empty list if the pattern is not found.
        """
        current_node = self.root
        for char in pattern:
            if char not in current_node.children:
                return []  # Return an empty list if not found
            current_node = current_node.children[char]

        # Return a list of tuples (start_index, end_index)
        return current_node.indexes

    def display(self, node: SuffixTreeNode = None, prefix: str = '') -> None:
        """Displays all suffixes stored in the suffix tree.

        Args:
            node (SuffixTreeNode, optional): The current node to display. Defaults to the root node.
            prefix (str, optional): The current prefix being built. Defaults to an empty string.
        """
        if node is None:
            node = self.root
        for char, child in node.children.items():
            new_prefix = prefix + char
            if child.indexes:  # Display only if there are indexes
                print(new_prefix)
            self.display(child, new_prefix)

    def export_to_dot(self, filename: str) -> None:
        """Exports the suffix tree to a .dot file for visualization.

        Args:
            filename (str): The name of the file to which the .dot representation will be written.
        """
        with open(filename, 'w') as f:
            f.write("digraph SuffixTree {\n")
            f.write("    node [shape=circle];\n")  # Set node shape to circle
            f.write("    start;\n")
            self._export_node_to_dot(self.root, f, None, "")
            f.write("}\n")

    def _export_node_to_dot(self, node: SuffixTreeNode, f, parent_label: str, transition: str) -> None:
        """Helper method to recursively export nodes to .dot format.

        Args:
            node (SuffixTreeNode): The current node to export.
            f: The file object to write to.
            parent_label (str): The name of the parent node.
            transition (str): The transition label from the parent node to this node.
        """
        if parent_label is None:
            current_label = "start"
        else:
            current_label = str(node.indexes)
            f.write(f'    "{parent_label}" -> "{current_label}" [label="{transition}"];\n')  # Create edge from parent
        for child_transition, child in node.children.items():
            self._export_node_to_dot(child, f, current_label, child_transition)

    def serialize_to_bytes(self, file: Path | str):
        """Serialize this suffix tree to a binary file."""
        file = SeekFile(file)
        file.delete()
        file.open()
        self.root.serialize(file, 0)
        file.close()

    @classmethod
    def deserialize(cls, file: SeekFile):
        root = SuffixTreeNode.deserialize_whole_tree(file, 0)
        text = root.find_longest_child_string()
        tree = MemorySuffixTree()
        tree.root = root
        tree.text = text
        return tree

    @classmethod
    def from_file(cls, file: Path | str):
        if type(file) == str:
            file = Path(file)
        return MemorySuffixTree(file.read_text())
