/**
 * Author: Seanneol Ebneazer Anan
 * Matric No.: S79146
 * Program: SMSK(SE) - Software Engineering
 * Course: CSF3104 Data Structure & Algorithm
 * Lab: Lab 5 (Task 2 - Test Class)
 */
public class LinkedListQExperiment {
    public static void main(String[] args) {
        LinkedListQueue queue = new LinkedListQueue();

        // Inserting inputs: 2, 1, 0, 3, 0
        queue.insert(2);
        queue.insert(1);
        queue.insert(0);
        queue.insert(3);
        queue.insert(0);

        System.out.println("-- Displaying Queue data--");
        queue.displayList();

        System.out.println("Item peeked- " + queue.peek());

        System.out.println("-- Removing Queue elements--");
        System.out.println("Item removed- " + queue.remove());
        System.out.println("Item removed- " + queue.remove());
    }
}
