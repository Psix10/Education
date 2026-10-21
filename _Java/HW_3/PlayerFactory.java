
import java.util.Random;
import java.util.Scanner;

public class PlayerFactory {
    public static Player createPlayer(String type, String name, char mark, Scanner input, Random random) {
        if ("human".equalsIgnoreCase(type)) return new HumanPlayer(name, mark, input);
        if ("ai".equalsIgnoreCase(type)) return  new AIPlayer(name, mark, random);
        throw new IllegalArgumentException("Неизвестный тип игрока: " + type);
    }

}
