/**
 * Author: Seanneol Ebneazer Anan
 * Matric No.: S79146
 * Program: SMSK(SE) - Software Engineering
 * Course: CSF3104 / CSF3101 Data Structure & Algorithm
 * Lab: Lab 4 (Task 3 - Implementation of Circular Queue)
 */

public class CircularQueue {
    private char[] q;
    private int front, rear, size, count;

    public CircularQueue(int m) {
        size = m;
        q = new char[size];
        front = 0;
        rear = -1;
        count = 0;
    }

    public boolean isFull() {
        return count == size;
    }

    public boolean isEmpty() {
        return count == 0;
    }

    public void enqueue(char n) {
        if (isFull()) {
            System.out.println("Circular Queue is full");
        } else {
            rear = (rear + 1) % size;
            q[rear] = n;
            count++;
        }
    }

    public char dequeue() {
        if (isEmpty()) {
            System.out.println("Circular Queue is empty");
            return (char) 250;
        } else {
            char x = q[front];
            front = (front + 1) % size;
            count--;
            return x;
        }
    }

    public char peek() {
        if (isEmpty()) {
            return (char) 250;
        }
        return q[front];
    }

    public void displayQueue() {
        if (isEmpty()) {
            System.out.println("Circular Queue is empty");
        } else {
            System.out.print("Elements in Circular Queue: ");
            for (int i = 0; i < count; i++) {
                int index = (front + i) % size;
                System.out.print(q[index] + " ");
            }
            System.out.println("(Count: " + count + "/" + size + ")");
        }
    }

    public static void main(String[] args) {
        System.out.println("=== TASK 3: TESTING CIRCULAR QUEUE ===");
        CircularQueue cq = new CircularQueue(5);
        cq.enqueue('A');
        cq.enqueue('B');
        cq.enqueue('C');
        cq.enqueue('D');
        cq.enqueue('E');
        cq.displayQueue();

        System.out.println("\nDequeuing 2 elements:");
        System.out.println("Dequeued: " + cq.dequeue());
        System.out.println("Dequeued: " + cq.dequeue());
        cq.displayQueue();

        System.out.println("\nEnqueueing 'F' (Wraps around to freed index 0):");
        cq.enqueue('F');
        cq.displayQueue();

        System.out.println("\nEnqueueing 'G' (Wraps around to freed index 1):");
        cq.enqueue('G');
        cq.displayQueue();
    }
}
