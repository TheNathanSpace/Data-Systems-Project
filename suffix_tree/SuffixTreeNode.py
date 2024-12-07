import struct

from seek_file import SeekFile


class SuffixTreeNode:
    """A node in the suffix tree.

    Attributes:
        children (Dict[str, 'SuffixTreeNode']): A dictionary mapping characters to child nodes.
        indexes (List[int]): A list of starting indexes of suffixes that pass through this node.
    """
    HEADER_FORMAT = '<II'
    INDICES_FORMAT = '<II'
    CHILDREN_FORMAT = '<cI'

    HEADER_LEN = struct.calcsize(HEADER_FORMAT)
    INDEX_LEN = struct.calcsize(INDICES_FORMAT)
    CHILD_LEN = struct.calcsize(CHILDREN_FORMAT)

    def __init__(self) -> None:
        self.indexes: list[tuple[int, int]] = []  # To store starting indexes of suffixes
        self.children: dict[str, SuffixTreeNode | int] = {}

    def find_longest_child_string(self) -> str:
        valid = False
        for start, end in self.indexes:
            if start == 0:
                valid = True
        if not valid:
            return ""

        for transition, child in self.children.items():
            for start, end in child.indexes:
                if start == 0:
                    full_string = transition + child.find_longest_child_string()
                    return full_string
        return ""

    def serialize(self, file: SeekFile, offset: int) -> int:
        """Static method to serialize to bytes. Returns next end position."""
        this_length = self.HEADER_LEN + (len(self.indexes) * SuffixTreeNode.INDEX_LEN) + (
                len(self.children) * SuffixTreeNode.CHILD_LEN)
        next_end_position = offset + this_length

        file.seek(offset)

        # Write placeholder for this so we can write its children
        file.write_at_offset(offset, struct.pack(">c", '\0'.encode("utf8")) * this_length)

        # Define the header format:
        # - > = means big-endian
        # - I = unsigned int, representing the number of indices this node matches in the target string
        # - I = unsigned int, representing how many children this node has
        header_bytes = struct.pack(SuffixTreeNode.HEADER_FORMAT, len(self.indexes), len(self.children))

        # Define the indices format:
        # - > = means big-endian
        # - I = unsigned int, representing the matched index start in the target string
        # - I = unsigned int, representing the matched index end in the target string
        indices_bytes = b""
        for start, end in self.indexes:
            indices_bytes += struct.pack(SuffixTreeNode.INDICES_FORMAT, start, end)

        # Define the children format:
        # - > = means big-endian
        # - c = character, representing the transition to its child
        # - I = unsigned int, representing the file offset of its child
        children_bytes = b""
        child: SuffixTreeNode
        for transition, child in self.children.items():
            assert len(transition) == 1
            new_end_position = child.serialize(file, next_end_position)
            children_bytes += struct.pack(SuffixTreeNode.CHILDREN_FORMAT, transition[0].encode("utf8"),
                                          next_end_position)
            next_end_position = new_end_position

        serialized = header_bytes + indices_bytes + children_bytes
        file.write_at_offset(offset, serialized)

        return next_end_position

    @classmethod
    def deserialize_whole_tree(cls, file: SeekFile, start_position: int) -> 'SuffixTreeNode':
        """Static method to deserialize in-memory from file location."""
        output_node = SuffixTreeNode()

        file.seek(start_position)
        header_bytes = file.read(SuffixTreeNode.HEADER_LEN)
        num_indices, num_children = struct.unpack(SuffixTreeNode.HEADER_FORMAT, header_bytes)

        indices_start = start_position + SuffixTreeNode.HEADER_LEN
        indices_len = num_indices * SuffixTreeNode.INDEX_LEN
        file.seek(indices_start)
        indices_bytes = file.read(indices_len)
        for i in range(num_indices):
            index_start = i * SuffixTreeNode.INDEX_LEN
            index_bytes = indices_bytes[index_start:(index_start + SuffixTreeNode.INDEX_LEN)]
            index_tuple = struct.unpack(SuffixTreeNode.INDICES_FORMAT, index_bytes)
            output_node.indexes.append(index_tuple)

        children_start = indices_start + indices_len
        children_len = num_children * SuffixTreeNode.CHILD_LEN
        file.seek(children_start)
        children_bytes = file.read(children_len)
        for i in range(num_children):
            child_start = i * SuffixTreeNode.CHILD_LEN
            child_bytes = children_bytes[child_start:(child_start + SuffixTreeNode.CHILD_LEN)]
            transition_char, target_offset = struct.unpack(SuffixTreeNode.CHILDREN_FORMAT, child_bytes)
            output_node.children[transition_char.decode("utf8")] = SuffixTreeNode.deserialize_whole_tree(file,
                                                                                                         target_offset)

        return output_node

    @classmethod
    def deserialize_with_offsets(cls, file: SeekFile, start_position: int) -> 'SuffixTreeNode':
        """Static method to deserialize with child offsets from file location."""
        output_node = SuffixTreeNode()

        file.seek(start_position)
        header_bytes = file.read(SuffixTreeNode.HEADER_LEN)
        num_indices, num_children = struct.unpack(SuffixTreeNode.HEADER_FORMAT, header_bytes)

        indices_start = start_position + SuffixTreeNode.HEADER_LEN
        indices_len = num_indices * SuffixTreeNode.INDEX_LEN
        file.seek(indices_start)
        indices_bytes = file.read(indices_len)
        for i in range(num_indices):
            index_start = i * SuffixTreeNode.INDEX_LEN
            index_bytes = indices_bytes[index_start:(index_start + SuffixTreeNode.INDEX_LEN)]
            index_tuple = struct.unpack(SuffixTreeNode.INDICES_FORMAT, index_bytes)
            output_node.indexes.append(index_tuple)

        children_start = indices_start + indices_len
        children_len = num_children * SuffixTreeNode.CHILD_LEN
        file.seek(children_start)
        children_bytes = file.read(children_len)
        for i in range(num_children):
            child_start = i * SuffixTreeNode.CHILD_LEN
            child_bytes = children_bytes[child_start:(child_start + SuffixTreeNode.CHILD_LEN)]
            transition_char, target_offset = struct.unpack(SuffixTreeNode.CHILDREN_FORMAT, child_bytes)
            output_node.children[transition_char.decode("utf8")] = target_offset

        return output_node
