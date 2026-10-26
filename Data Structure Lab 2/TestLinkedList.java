public class TestLinkedList {
    public static void main(String[] args) {
        MyLinkedList list = new MyLinkedList();

        // 1. Add a, b, c, d, e using addFirst(), then print.
        System.out.println("1. Add a, b, c, d, e using addFirst():");
        list.addFirst(new Node("a"));
        list.addFirst(new Node("b"));
        list.addFirst(new Node("c"));
        list.addFirst(new Node("d"));
        list.addFirst(new Node("e"));
        System.out.print("List: ");
        list.printList();

        // 2. Delete the last value, then print.
        System.out.println("\n2. Delete the last value (removeLast):");
        Node removedLast = list.removeLast();
        System.out.println("Removed: " + (removedLast != null ? removedLast.element : "null"));
        System.out.print("List: ");
        list.printList();

        // 3. Add 'f' at the second position, then print.
        // In 0-indexed list: index 0 = 1st pos, index 1 = 2nd pos
        System.out.println("\n3. Add 'f' at the second position (index 1):");
        list.add(1, new Node("f"));
        System.out.print("List: ");
        list.printList();

        // 4. Add 'g' at the end, then print.
        System.out.println("\n4. Add 'g' at the end (addLast):");
        list.addLast(new Node("g"));
        System.out.print("List: ");
        list.printList();

        // 5. Delete the first element, then print.
        System.out.println("\n5. Delete the first element (removeFirst):");
        Node removedFirst = list.removeFirst();
        System.out.println("Removed: " + (removedFirst != null ? removedFirst.element : "null"));
        System.out.print("List: ");
        list.printList();

        // 6. Reverse the list, then print.
        System.out.println("\n6. Reverse the list:");
        list.reverse();
        System.out.print("List: ");
        list.printList();
    }
}