from suffix_tree.FileSuffixTree import FileSuffixTree
from suffix_tree.MemorySuffixTree import MemorySuffixTree

if __name__ == "__main__":
    input_name = "short"
    search_string = "GCAA"

    # Construct suffix tree
    input_file = f"data/target_sequences/{input_name}.txt"
    suffix_tree = MemorySuffixTree.from_file(input_file)

    # Output visualization and save tree to disk
    suffix_tree.export_to_dot(f"data/visualizations/{input_name}.dot")
    suffix_tree.serialize_to_bytes(f"data/trees/{input_name}.dat")

    # Search disk tree for string
    file_tree = FileSuffixTree(f"data/trees/{input_name}.dat")
    results = file_tree.search(search_string)
    print(f"\"{search_string}\": {results}")
