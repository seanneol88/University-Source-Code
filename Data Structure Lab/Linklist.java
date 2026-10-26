public class Linklist {
     private Node first;

    // LinkList constructor
    public Linklist() {
        first = null;
    }

    // Returns true if the linked list is empty
    public boolean isEmpty() {
        return first == null;
    }

    // Inserts a new node at the first of the linked list
    public void addFirst(int d1, double d2) {
        Node node = new Node(d1, d2);
        node.next = first;
        first = node;
    }

    // Deletes the node at the first of the linked list
    public Node deleteFirst() {
        Node temp = first;
        first = first.next;
        return temp;
    }

    // Prints the linked list data
    public void printList() {
        Node currentNode = first;
        System.out.print("List: ");
        while (currentNode != null) {
            currentNode.printNode();
            currentNode = currentNode.next;
        }
        System.out.println("");
    }
}
