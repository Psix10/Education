import java.util.List;
import java.util.Random;

public class AIPlayer extends Player {
    private static final Random RANDOM = new Random();

    public AIPlayer(String name, char mark) {
        super(name, mark);
    }

    @Override
    public void makeMove(Board board) {
        List<int[]> empty = board.getEmptyCells();
        int[] cell = empty.get(RANDOM.nextInt(empty.size()));
        board.placeMark(cell[0], cell[1], getMark());
        System.out.println(getName() + " (" + getMark() + ") походил в клетку " + (cell[0] * 3 + cell[1] + 1));
    }
    
}
