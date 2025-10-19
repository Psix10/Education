import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int num1 = sc.nextInt();
        int num2 = sc.nextInt();
        try {
            int result = division(num1, num2);
            System.out.println("Результат: " + result);
        }
        catch (ArithmeticException e) {
            System.out.println("Ошибка: Деление на ноль!");
        }
            
    }

    public static int division(int a, int b) {
        return a / b;
    }
}
