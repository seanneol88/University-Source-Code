public class LinkListTest {
     public static void main(String[] args) {
        Linklist list = new Linklist();

        // Inserting nodes at the beginning
        list.addFirst(1, 1.01);
        list.printList();

        list.addFirst(2, 2.02);
        list.printList();

        list.addFirst(3, 3.03);
        list.printList();

        list.addFirst(4, 4.04);
        list.printList();

        list.addFirst(5, 5.05);
        list.printList();

        // Deleting nodes from the beginning until empty
        while (!list.isEmpty()) {
            Node deletedLink = list.deleteFirst();
            System.out.print("deleted: ");
            deletedLink.printNode();
            System.out.println("");
        }

        // Print list after all nodes are deleted
        list.printList();
    }
}
