public class Game {
    private final Board board;
    private final Player player1;
    private final Player player2;
    private Player currentPlayer;

    public Game(Player player1, Player player2, Board board) {
        this.player1 = player1;
        this.player2 = player2;
        this.board = board;
        this.currentPlayer = player1;
    }

    public void startGame() {
        System.out.println("=== Игра «Крестики-нолики» ===");
        System.out.println("Игроки ходят по очереди, вводя номер клетки от 1 до 9.");
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
        if (winner != ' ') {
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
