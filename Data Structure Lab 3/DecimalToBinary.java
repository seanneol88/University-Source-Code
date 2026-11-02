import java.util.Scanner;
import java.util.InputMismatchException;

public class DecimalToBinary {
     public static void main(String[] args) {
        // a. Declare stack s of size 25
        IntStack s = new IntStack(25);

        // b. Declare decNumber
        int decNumber = 0;

        // c. Scanner object
        Scanner scanInput = new Scanner(System.in);

        // d. Read integer with try-catch
        System.out.print("Enter a decimal number: ");
        try {
            decNumber = scanInput.nextInt();
        } catch (InputMismatchException e) {
            System.out.println("Error: Invalid input! Please enter an integer value only.");
            return;
        }

        // e. Boolean stop flag
        boolean stop = false;

        // Base cases for 0 and 1
        if (decNumber == 0 || decNumber == 1) {
            if (!s.isFull()) s.push(decNumber);
            stop = true;
        }

        // f. Radix division loop
        while (!stop) {
            // i. Push remainder of decNumber % 2
            if (!s.isFull()) {
                s.push(decNumber % 2);
            }

            // ii. Integer division quotient
            decNumber = decNumber / 2;

            // iii. Stop condition when decNumber is 0 or 1
            if (decNumber == 0 || decNumber == 1) {
                if (!s.isFull()) {
                    s.push(decNumber);
                }
                stop = true;
            }
        }

        // 6 & 7. Pop binary digits
        System.out.print("Binary representation: ");
        while (!s.isEmpty()) {
            System.out.print(s.pop() + " ");
        }
        System.out.println();
    }
}
