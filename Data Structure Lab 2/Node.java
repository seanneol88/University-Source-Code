public class Node {
    public Object element;
    public Node next;

    // Default constructor
    public Node() {
        this.element = null;
        this.next = null;
    }

    // Constructor taking an item and storing it in element
    public Node(Object element) {
        this.element = element;
        this.next = null;
    }

    @Override
    public String toString() {
        return element != null ? element.toString() : "null";
    }
}