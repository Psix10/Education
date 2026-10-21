

public abstract class Player {
    private final String name;
    private final char mark;

    public Player(String name, char mark) {
        this.name = name;
        this.mark = mark;
    }

    public abstract void makeMove(Board board);

    public char getMark() {
        return mark;
    }

    public String getName() {
        return name;
    }
}