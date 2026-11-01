import java.util.Scanner;

/*
 * ==============================================================
 *  DATA STRUCTURE & ALGORITHM
 *  Lab 3 : Stack  --  TASK 3 (Binary to Decimal Converter)
 * ==============================================================
 *  Name    : Seanneol
 *  Program : SMSK(SE)
 *  Course  : CSF3104
 *  Lab     : 3
 *  Date    : <enter lab date>
 * ==============================================================
 *
 *  How the stack is used:
 *  1. Every bit of the binary number is pushed onto the stack from
 *     left to right (most significant bit first).
 *  2. Because a stack is Last-In-First-Out, popping returns the bits
 *     from right to left, so the first bit popped is the least
 *     significant bit (weight 2^0), the next is 2^1, and so on.
 *  3. Decimal value = sum of (bit * weight) for every popped bit.
 *
 *  Example: 1101
 *      push 1, 1, 0, 1     -> stack (bottom..top) = 1 1 0 1
 *      pop  1  -> 1 * 1  =  1
 *      pop  0  -> 0 * 2  =  0
 *      pop  1  -> 1 * 4  =  4
 *      pop  1  -> 1 * 8  =  8
 *      total = 13
 */

public class BinaryToDecimal {

    public static void main(String[] args) {

        Scanner input = new Scanner(System.in);

        System.out.println("=== Binary to Decimal Converter ===");
        System.out.print("Enter a binary number (0s and 1s only): ");

        if (!input.hasNextLine()) {
            System.out.println("No input received.");
            return;
        }

        String binary = input.nextLine().trim();

        // Basic validation before using the stack
        if (binary.isEmpty()) {
            System.out.println("Error: input is empty.");
            return;
        }
        if (binary.length() > 63) {
            System.out.println("Error: please enter at most 63 bits.");
            return;
        }
        for (int i = 0; i < binary.length(); i++) {
            char digit = binary.charAt(i);
            if (digit != '0' && digit != '1') {
                System.out.println("Error: '" + digit + "' is not a binary digit.");
                return;
            }
        }

        // 1. create a stack big enough to hold every bit
        ChrStack s = new ChrStack(binary.length());

        // 2. push every bit, left (MSB) to right (LSB)
        for (int i = 0; i < binary.length(); i++) {
            s.push(binary.charAt(i));
        }

        // 3. pop every bit and add its value using the matching weight
        long decimal = 0;
        long weight = 1;                 // 2^0
        while (!s.isEmpty()) {
            char bit = s.pop();
            if (bit == '1') {
                decimal += weight;
            }
            weight *= 2;                 // move to the next power of two
        }

        System.out.println("Binary      : " + binary);
        System.out.println("Decimal     : " + decimal);
        System.out.println("Check (API) : " + Long.parseLong(binary, 2));

        input.close();
    }
}
