# Lab 3 – Stack

Course: **CSF3104 – Data Structure & Algorithm**
Faculty of Computer Science and Mathematics (FSKM), Universiti Malaysia Terengganu (UMT)

This folder contains my Java source code for **Lab 3: Stack** (Lab manual version 2, 2026/2027).
The manual copy I worked from is titled *"Lab03-Stack without Task 2"*, so the tasks covered here are **Task 1** and **Task 3**.

---

## 📂 Files

| File | Task | Purpose |
| --- | --- | --- |
| `StackExperiment.java` | Task 1 | `ChrStack` (a simple character stack built on an array) plus the `main` method that reads a name and prints it in reverse. |
| `BinaryToDecimal.java` | Task 3 | Reads a binary number, pushes every bit onto a `ChrStack`, then pops the bits to build the decimal value. |

---

## ▶️ How to run

### NetBeans
1. **File → New Project → Java with Ant → Java Application**, name it `StackExperiment`.
2. Copy the contents of `StackExperiment.java` into the project's `StackExperiment.java`
   (keep `ChrStack` above the `public class StackExperiment`, as the manual describes).
3. Copy `BinaryToDecimal.java` into the same `src` folder / package.
4. Run `StackExperiment.java` (Task 1) or `BinaryToDecimal.java` (Task 3).

### Command line
```bash
cd "Data Structure Lab 3"
javac StackExperiment.java BinaryToDecimal.java
java StackExperiment
java BinaryToDecimal
```

### Sample run – Task 1
```
Please enter your name:
Fakulti Sains Komputer dan Matematik
Your name reverse is:
kitametaM nad retupmoK sniaS itlukaF
Number of characters stored in the stack: 36
```

### Sample run – Task 3
```
=== Binary to Decimal Converter ===
Enter a binary number (0s and 1s only): 1101
Binary      : 1101
Decimal     : 13
Check (API) : 13
```

---

## 🔧 Notes / small fixes made in my implementation

The manual's listing is a printed code sample, so I tidied it up into code that actually compiles and behaves safely. Behaviour stays the same as the manual, but the following were corrected:

| In the manual | In this code |
| --- | --- |
| `char data = stack[top]` in `pop()` (missing `;`) | Semicolon added. |
| `isempty()`, `isfull()` | Renamed to `isEmpty()`, `isFull()` (consistent camelCase, matching the `main` method). |
| `length()` returns `top` | Returns `top + 1`, because `top` is a 0-based index. |
| `push()` / `pop()` have no boundary guard | `push()` throws `IllegalStateException` when full, `pop()` when empty, so the stack can never overflow the array or read outside it. |
| Default constructor repeats 3 assignments | Uses `this(defaultSize)` (the "easier version" the manual suggests). |
| Only the manual's `main` | Added an extra `peek()` helper and printed the number of characters read before the stack is emptied. |

**Windows line endings:** `System.in.read()` also receives `\r`. The loop skips it so the reversed output is not full of stray carriage returns.

**End of input:** the loop also stops when `System.in.read()` returns `-1` (end of stream). The manual's version only compares against `'\n'`, so piping a file that has no final newline would loop forever.

---

## 📝 Lab questions – short answers

**1. What did the program do?**
It read characters from the keyboard one at a time and pushed each one onto the stack until `ENTER` (`\n`) was pressed. It then repeatedly called `pop()` and printed each character, so the name appeared in reverse order, because a stack is Last-In-First-Out.

**2. For the input "Fakulti Sains Komputer dan Matematik", what is inside stack `s` when you type the word "Sains"?**
`top` points at the newest character, so the stack (bottom → top) holds the characters typed so far, including the space before "Sains":

`F a k u l t i   S a i n s`

`top` = index 12 and `length()` = 13.

**3. With the long lyric input, what happens and why?**
Stack `s` was created with size **100**, but the lyric is longer than 100 characters. Because the code checks `if (!s.isFull())` before every `push()`, the first 100 characters are stored and every character after that is silently dropped. Nothing crashes, but the reversed output is only the reverse of the first 100 characters. If the guard were removed, `push()` would write past the end of the array and throw an `ArrayIndexOutOfBoundsException`.

**4. If the stack is meant to store integer data, what must change in `ChrStack`?**
Every place that deals with the element type:
- `private char[] stack;` → `private int[] stack;`
- `char[]` array creation → `new int[size]`
- `void push(char data)` → `void push(int data)`
- `char pop()` → `int pop()`
- `char peek()` → `int peek()`

The size, `top`, constructor and `isEmpty()` / `isFull()` / `length()` logic stay exactly the same.
