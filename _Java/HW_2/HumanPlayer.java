import java.util.Scanner;

public class HumanPlayer extends Player {

    public HumanPlayer(String name, char mark) {
        super(name, mark);
    }

    @Override
    public void makeMove(Board board) {
        Scanner sc = new Scanner(System.in);

        while (true) {
            System.out.print(getName() + " (" + getMark() + "), введите номер клетки 1-9: ");
            String input = sc.nextLine().trim();

            int position;
            try {
                position = Integer.parseInt(input);
            } catch (NumberFormatException e) {
                System.out.println("Некорректный ввод. Введите целое число от 1 до 9.");
                continue;
            }

            if (position < 1 || position > 9) {
                System.out.println("Введите число от 1 до 9.");
                continue;
            }

            int row = (position - 1) / 3;
            int col = (position - 1) % 3;

            if (board.placeMark(row, col, getMark())) {
                return;
            }
            System.out.println("Эта клетка уже занята. Попробуйте другую.");
        }
    }
}