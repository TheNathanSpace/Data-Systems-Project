from pathlib import Path

from suffix_tree.SuffixTreeNode import SuffixTreeNode
from seek_file import SeekFile


class FileSuffixTree:
    """An on-disk suffix tree for searching substrings of a given text.

    Attributes:
        file_path (Path): The Path to the suffix tree file.
    """

    def __init__(self, file_path: Path | str) -> None:
        if type(file_path) == str:
            file_path = Path(file_path)
        self.file_path = file_path

    def search(self, pattern: str) -> list[tuple[int, int]]:
        """Searches for a pattern in the suffix tree.

        Args:
            pattern (str): The substring to search for.

        Returns:
            List[Tuple[int, int]]: A list of tuples, each containing the start and end indices (inclusive)
            of the pattern in the original text. Returns an empty list if the pattern is not found.
        """
        seek_file = SeekFile(self.file_path)
        root_node = SuffixTreeNode.deserialize_with_offsets(seek_file, 0)

        current_node = root_node
        for char in pattern:
            # Return an empty list if the next character isn't in the tree
            if char not in current_node.children:
                return []

            # Jump to next node's location
            next_offset = current_node.children[char]
            current_node = SuffixTreeNode.deserialize_with_offsets(seek_file, next_offset)

        # Return a list of tuples (start_index, end_index)
        return current_node.indexes
