package HW_1.treeNode;

public class main {
    
    public static int depthTree (TreeNode treeNode) {
        if (treeNode == null) {
            return 0;
        }

        int leftDepth = depthTree(treeNode.left);
        int rightDepth = depthTree(treeNode.right);

        if (leftDepth > rightDepth) {
            return leftDepth + 1;
        } else {
            return rightDepth + 1;
        }
    }

    public static void main(String[] args) {

        TreeNode tree = new TreeNode(1);
        TreeNode current = tree;

        for (int i = 2; i <= 5; i++) {
            current.left = new TreeNode(i);
            current = current.left;
        }
        
        
        tree.right = new TreeNode(99);

        tree.left.left.right = new TreeNode(30);

        tree.left.left.right.left = new TreeNode(300);

        int maxDepth = depthTree(tree);

        System.out.println("Максимальная глубина сложного дерева: " + maxDepth); 
    }
}
