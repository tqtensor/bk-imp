# Conclusion

From the 1 million searches conducted, the exists function was invoked 10,898,067 times in the BST and 8,226,499 times in the RBT.

The RBT's superior search performance is due to its self-balancing attribute, which eliminates the potential height imbalance of the tree present in BST. If left unbalanced, a BST can result in significant time complexity variation across operations, where the worst-case scenario occurs when the height equals the number of nodes, giving a search operation time complexity of O(n).

Conversely, an RBT achieves balance via a sequence of color and rotation rules implemented during insertions and deletions, ensuring the tree always maintains a balanced height. This balance guarantees the RBT's search operation time complexity remains constant at O(log n), faster than the BST's worst-case time complexity of O(n).

In summary, the frequency of exists function calls indicates that RBT performs better than BST in searching, thanks to its self-balancing trait that ensures a balanced height, leading to faster search times.
