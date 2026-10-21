public class Game {
    private static Game instance;
    private Board board;
    private Player player1, player2, currentPlayer;

    private Game() {}

    public static Game getInstance() {
        if(instance == null) {
            instance = new Game();
        }
        return instance;
    }

    public void init(Board board, Player player1, Player player2) {
        if (this.board != null) {
            throw new IllegalStateException("Игра уже инициализирована");
        }
        this.board = board;
        this.player1 = player1;
        this.player2 = player2;
        this.currentPlayer = player1;
    }

    public void startGame() {
        System.out.println("=== Игра «Крестики-нолики» ===");
        System.out.println("Игроки ходят по очереди, вводя номер клетки от 1 до "
        + (board.getSize() * board.getSize()) + ".");
        System.out.println("Побеждает тот, кто соберёт три своих знака в ряд.");

        while (true) { 
            board.displayBoard();
            System.out.println("Ход игрока: " 
                + currentPlayer.getName() + " (" + currentPlayer.getMark() + ")");

            currentPlayer.makeMove(board);
            
            if (checkForWinOrDraw()) {
                board.displayBoard();
                return;
            }
            switchPlayer();
        }
    }

    public void switchPlayer() {
        currentPlayer = (currentPlayer == player1) ? player2 : player1;
    }

    public boolean checkForWinOrDraw() {
        char winner = board.checkWin();
        if (winner != board.getEmpty()) {
            String winnerName = (winner == player1.getMark()) ? player1.getName() : player2.getName();
            System.out.println("Победил " + winnerName + " (" + winner + ")!");
            return true;
        }
        if (board.isFull()) {
            System.out.println("Ничья! Игровое поле заполнено.");
            return true;
        }
        return false;
    }
    
}
