public class Node {
     public int data1;
    public double data2;
    Node next;

    // constructor of the Node
    public Node(int d1, double d2) {
        data1 = d1;
        data2 = d2;
        next = null;
    }

    // Print Node data
    public void printNode() {
        System.out.print("{" + data1 + ", " + data2 + "}");
    }
}
