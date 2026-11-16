/**
 * Author: Seanneol Ebneazer Anan
 * Matric No.: S79146
 * Program: SMSK(SE) - Software Engineering
 * Course: CSF3104 / CSF3101 Data Structure & Algorithm
 * Lab: Lab 4 (Queue)
 * Date: November 2026
 */

public class QueueExperiment {
    public static void main(String[] args) {
        System.out.println("--- STEP 5: Testing initial queue (capacity 10) ---");
        CharQueue myQueue = new CharQueue(10);
        myQueue.enqueue('a');
        myQueue.enqueue('b');
        myQueue.enqueue('c');
        myQueue.enqueue('d');
        myQueue.enqueue('e');
        myQueue.enqueue('f');
        myQueue.enqueue('g');
        myQueue.enqueue('h');
        myQueue.enqueue('i');
        myQueue.enqueue('j');

        System.out.println("First element in queue: " + myQueue.peek());

        System.out.println("\n--- STEP 8: Inserting 'k' into existing queue ---");
        myQueue.enqueue('k');
        System.out.println("First element in queue: " + myQueue.peek());

        System.out.println("\n--- STEP 9: Fixed Queue with Capacity 11 (or 15) ---");
        CharQueue fixedQueue = new CharQueue(15);
        fixedQueue.enqueue('a');
        fixedQueue.enqueue('b');
        fixedQueue.enqueue('c');
        fixedQueue.enqueue('d');
        fixedQueue.enqueue('e');
        fixedQueue.enqueue('f');
        fixedQueue.enqueue('g');
        fixedQueue.enqueue('h');
        fixedQueue.enqueue('i');
        fixedQueue.enqueue('j');
        fixedQueue.enqueue('k'); // Successfully enqueued without error!

        System.out.println("First element in fixed queue: " + fixedQueue.peek());

        System.out.println("\n--- STEP 10: Display all elements in the queue ---");
        fixedQueue.displayQueue();
    }
}
