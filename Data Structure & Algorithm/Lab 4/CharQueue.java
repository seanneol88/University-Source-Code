/**
 * Author: Seanneol Ebneazer Anan
 * Matric No.: S79146
 * Program: SMSK(SE) - Software Engineering
 * Course: CSF3104 / CSF3101 Data Structure & Algorithm
 * Lab: Lab 4 (Task 1 - Linear Queue Implementation using Array)
 */

public class CharQueue {
    char q[];
    int front, rear, size;

    // Constructor of class CharQueue
    public CharQueue(int m) {
        size = m;
        q = new char[size];
        front = rear = -1;
    }

    // Place item at the back of the queue
    void enqueue(char n) {
        if (isFull()) {
            System.out.println("Queue is full");
        } else {
            if (front == -1) {
                front = rear = 0;
            } else {
                rear++;
            }
            q[rear] = n;
        }
    }

    /* Retrieves the element at the front of the queue
       and removes it from the queue. */
    char dequeue() {
        if (isEmpty()) {
            System.out.println("queue is empty");
            return (char) 250;
        } else {
            char x = q[front];
            front++;
            return x;
        }
    }

    /* Retrieves the element at the front of the queue without removing
       it from the queue. */
    char peek() {
        return q[front];
    }

    boolean isEmpty() {
        return (front == -1 || front > rear);
    }

    boolean isFull() {
        return (rear == size - 1);
    }

    // Step 10: Method to display all elements in the queue
    public void displayQueue() {
        if (isEmpty()) {
            System.out.println("Queue is empty");
        } else {
            System.out.print("Elements in queue: ");
            for (int i = front; i <= rear; i++) {
                System.out.print(q[i] + " ");
            }
            System.out.println();
        }
    }
}
