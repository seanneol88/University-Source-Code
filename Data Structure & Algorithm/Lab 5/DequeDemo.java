import java.util.Deque;
import java.util.ArrayDeque;

/**
 * Author: Seanneol Ebneazer Anan
 * Matric No.: S79146
 * Program: SMSK(SE) - Software Engineering
 * Course: CSF3104 Data Structure & Algorithm
 * Lab: Lab 5 (Task 3 - Deque Demo)
 */
public class DequeDemo {
    public static void main(String[] args) {
        Deque<String> deque = new ArrayDeque<String>();
        deque.offer("Struktur");
        deque.offer("Data");
        deque.add("Dan");
        deque.offerFirst("Algoritma");
        System.out.println("After offerFirst Traversal...");
        for (String s : deque) {
            System.out.println(s);
        }
        //deque.poll();
        //deque.pollFirst(); // it is same as poll()
        deque.pollLast();
        System.out.println("After pollLast() Traversal...");
        for (String s : deque) {
            System.out.println(s);
        }
    }
}
