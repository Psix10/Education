package HW_1.polindrom;

class  Main {
    
    public static boolean polidrom(int number) {
        
        if (number < 0) {
            return false;
        }

        int originalNumber = number;
        int lastDigit;
        int reversedNumber = 0;

        
        while (number > 0) {
            lastDigit = number % 10;
            reversedNumber = (reversedNumber * 10) + lastDigit;
            number = number / 10;
        }
        return originalNumber == reversedNumber;
        

    }
    public static void main(String[] args) {
        int test1 = 121;
        int test2 = -121;
        int test3 = 10;

        System.out.println("Число " + test1 + " палиндром? " + polidrom(test1));
        System.out.println("Число " + test2 + " палиндром? " + polidrom(test2));
        System.out.println("Число " + test3 + " палиндром? " + polidrom(test3));
    }
}