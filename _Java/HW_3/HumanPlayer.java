import java.util.Scanner;

public class HumanPlayer extends Player {

    private final Scanner input;


    public HumanPlayer(String name, char mark, Scanner input) {
        super(name, mark);
        this.input = input;
    }

    @Override
    public void makeMove(Board board) {
        int size = board.getSize();
        int maxCell = size * size;

        while (true) {
            System.out.print(getName() + " (" + getMark() + "), введите номер клетки 1-"+ maxCell + ": ");
            String raw = input.nextLine().trim();

            int position;
            try {
                position = Integer.parseInt(raw);
            } catch (NumberFormatException e) {
                System.out.println("Некорректный ввод. Введите целое число от 1 до " + maxCell + ".");
                continue;
            }

            if (position < 1 || position > maxCell) {
                System.out.println("Введите число от 1 до " + maxCell + ".");
                continue;
            }

            int row = (position - 1) / size;
            int col = (position - 1) % size;

            if (board.placeMark(row, col, getMark())) {
                return;
            }
            System.out.println("Эта клетка уже занята. Попробуйте другую.");
        }
    }
}