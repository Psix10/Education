import java.util.List;
import java.util.Random;

public class AIPlayer extends Player {
    private final Random random;

    public AIPlayer(String name, char mark, Random random) {
        super(name, mark);
        this.random = random;
    }

    @Override
    public void makeMove(Board board) {
        List<int[]> empty = board.getEmptyCells();
        int[] cell = empty.get(random.nextInt(empty.size()));
        board.placeMark(cell[0], cell[1], getMark());
        int humanNumber = cell[0] * board.getSize() + cell[1] + 1;
        System.out.println(getName() + " (" + getMark() + ") походил в клетку " + humanNumber);
    }
    
}
