import java.io.IOException;

/*
 * ==============================================================
 *  DATA STRUCTURE & ALGORITHM
 *  Lab 3 : Stack  --  TASK 1 (Apply and test a simple stack)
 * ==============================================================
 *  Name    : Seanneol
 *  Program : SMSK(SE)
 *  Course  : CSF3104
 *  Lab     : 3
 *  Date    : <enter lab date>
 * ==============================================================
 */

/** Java implementation of stack of type char */
class ChrStack {

    // 1. declare default stack size
    private static final int defaultSize = 10;

    // 2. Declare variable for stack
    private int size;      // Size of stack
    private int top;       // Index for top Object
    private char[] stack;  // Array holding character data

    /** Constructors */

    // 3. Constructor to create stack using default size
    ChrStack() {
        this(defaultSize);            // easier version:
                                      // replace all 3 lines with this(defaultSize);
    }

    // 4. Constructor to create stack using supplied size
    ChrStack(int size) {
        if (size <= 0) {
            throw new IllegalArgumentException("Stack size must be greater than 0");
        }
        this.size = size;
        this.top = -1;
        this.stack = new char[size];
    }

    // 5. Push method: used to insert data into the top of the stack
    void push(char data) {
        if (isFull()) {
            throw new IllegalStateException("Stack is full - cannot push '" + data + "'");
        }
        top++;                // go to upper position
        stack[top] = data;    // put data in that position
    }

    // 6. Pop method: get and remove the top element/data in the stack
    char pop() {
        if (isEmpty()) {
            throw new IllegalStateException("Stack is empty - nothing to pop");
        }
        char data = stack[top];   // get data at current position
        top--;                    // go down one step
        return data;              // and return the data
    }

    // 6b. Peek method: look at the top element without removing it
    char peek() {
        if (isEmpty()) {
            throw new IllegalStateException("Stack is empty - nothing to peek");
        }
        return stack[top];
    }

    // 7. isEmpty method: used to check if the stack is empty.
    //    Usually used before calls to pop method. Returns true or false
    boolean isEmpty() {
        return (top == -1);       // returns true if stack is empty
    }

    // 8. isFull method: used to check if the stack is full.
    //    Usually used before calls to push. Returns true or false
    boolean isFull() {
        return (top == size - 1); // returns true if stack is full
    }

    // 9. length method: to get the current number of elements in the stack
    int length() {
        return top + 1;           // top is a 0-based index, so count is top + 1
    }

} // end of class ChrStack


public class StackExperiment {

    public static void main(String[] args) throws IOException {

        // 1. declare a stack s using the ChrStack class with size 100
        ChrStack s = new ChrStack(100);         // 100 chars

        // 2. Declare a character ch to store character input
        char ch;

        // 3. Give an instruction to user
        System.out.println("Please enter your name:");

        // 4. Get input and store into stack using push method
        //    until user press ENTER (\n)
        int read;                      // raw value returned by System.in.read()
        while ((read = System.in.read()) != -1) {   // -1 means end of input
            ch = (char) read;
            if (ch == '\n') {          // ENTER pressed -> stop reading
                break;
            }
            if (ch == '\r') {          // ignore the CR of a Windows line ending
                continue;
            }
            if (!s.isFull()) {         // check stack is not full
                s.push(ch);            // put data into stack
            }
        }

        // 5. Tell users their name will be printed in reverse
        int totalChars = s.length();    // count first, the stack is emptied below
        System.out.println("Your name reverse is:");
        while (!s.isEmpty()) {          // check stack is not empty
            System.out.print(s.pop());  // get data from stack using pop method
        }
        System.out.println();
        System.out.println("Number of characters stored in the stack: " + totalChars);
    }
}
