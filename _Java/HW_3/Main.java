import java.util.Random;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {

        Scanner input  = new Scanner(System.in);
        Random  random = new Random();

        Player player1 = PlayerFactory.createPlayer("human", "Player 1", 'X', input, random);
        Player player2 = PlayerFactory.createPlayer("ai", "Bot", 'O', input, random);

        Board board = new Board.BoardBuilder().size(3).build();
        Game game = Game.getInstance();
        game.init(board, player1, player2);
        game.startGame();
    }
}
