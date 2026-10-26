public class MyLinkedList {
    public Node head;
    public Node tail;
    public int size;

    // Default constructor
    public MyLinkedList() {
        this.head = null;
        this.tail = null;
        this.size = 0;
    }

    // Returns true if list is empty
    public boolean isEmpty() {
        return head == null;
    }

    // Returns current number of elements
    public int size() {
        return size;
    }

    // addFirst(Node e): Inserts a node at the beginning of the list
    public void addFirst(Node e) {
        if (e == null) return;
        if (isEmpty()) {
            head = tail = e;
            e.next = null;
        } else {
            e.next = head;
            head = e;
        }
        size++;
    }

    // addLast(Node e): Inserts a node at the end of the list
    public void addLast(Node e) {
        if (e == null) return;
        if (isEmpty()) {
            head = tail = e;
            e.next = null;
        } else {
            tail.next = e;
            tail = e;
            e.next = null;
        }
        size++;
    }

    // add(int index, Node e): Inserts a node at the specified position
    public void add(int index, Node e) {
        if (e == null) return;
        if (index <= 0) {
            addFirst(e);
        } else if (index >= size) {
            addLast(e);
        } else {
            Node current = head;
            for (int i = 0; i < index - 1; i++) {
                current = current.next;
            }
            e.next = current.next;
            current.next = e;
            size++;
        }
    }

    // removeFirst(): Deletes a node from the beginning of the list
    public Node removeFirst() {
        if (isEmpty()) {
            return null;
        }
        Node temp = head;
        head = head.next;
        size--;
        if (head == null) {
            tail = null;
        }
        temp.next = null;
        return temp;
    }

    // removeLast(): Deletes a node from the end of the list
    public Node removeLast() {
        if (isEmpty()) {
            return null;
        }
        if (head == tail) {
            Node temp = head;
            head = tail = null;
            size = 0;
            return temp;
        }
        Node current = head;
        while (current.next != tail) {
            current = current.next;
        }
        Node temp = tail;
        tail = current;
        tail.next = null;
        size--;
        return temp;
    }

    // printList(): Prints all elements in the list
    public void printList() {
        Node current = head;
        System.out.print("[");
        while (current != null) {
            System.out.print(current.element);
            if (current.next != null) {
                System.out.print(", ");
            }
            current = current.next;
        }
        System.out.println("]");
    }

    // reverse(): Reverses the singly linked list in-place
    public void reverse() {
        Node prev = null;
        Node current = head;
        Node next = null;
        tail = head; // Original head becomes new tail
        while (current != null) {
            next = current.next;
            current.next = prev;
            prev = current;
            current = next;
        }
        head = prev; // Original tail becomes new head
    }
}
