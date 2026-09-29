

public class Main {
    public static void main(String[] args) {
        Player player1 = new HumanPlayer("Игрок 1", 'X');
        Player player2 = new HumanPlayer("Игрок 2", 'O');

        Board board = new Board();
        Game game = new Game(player1, player2, board);
        game.startGame();
    }
}
