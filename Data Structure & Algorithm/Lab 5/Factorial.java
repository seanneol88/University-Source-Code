/**
 * Author: Seanneol Ebneazer Anan
 * Matric No.: S79146
 * Program: SMSK(SE) - Software Engineering
 * Course: CSF3104 Data Structure & Algorithm
 * Lab: Lab 5 (Task 1 - Recursion)
 */
public class Factorial {

    /**
     * Computes the factorial of the given (nonnegative) integer
     */
    public static int factorial(int n) throws IllegalArgumentException {
        if (n < 0) {
            throw new IllegalArgumentException(); // argument must be nonnegative
        } else if (n == 0) {
            return 1; // base case
        } else {
            return n * factorial(n - 1); // recursive case
        }
    }

    public static void main(String[] args) {
        int input = 6;
        int result = factorial(input);
        System.out.println("Factorial of " + input + " is: " + result);
    }
}
