import java.util.ArrayList;
import java.util.List;

public class Board {

    private final char[][] grid;
    private final int size;
    private final char empty;

    private Board(int size, char empty) {
        this.size = size;
        this.empty = empty;
        this.grid = new char[size][size];
        for (int row = 0; row < size; row++) {
            for (int col = 0; col < size; col++) {
                grid[row][col] = empty;
            }
        }
    }

    public static class BoardBuilder {
        private int size = 3;
        private char empty = ' ';

        public BoardBuilder size(int s) {
            if (s < 3) throw new IllegalArgumentException("Минимальный размер поля — 3");
            this.size = s;
            return this;
        }

        public BoardBuilder emptyCell(char c) {
            this.empty = c;
            return this;
        }

        public Board build() {
            return new Board(size, empty);
        }
    }

    public int getSize()   { return size; }
    public char getEmpty() { return empty; }
    public char getCell(int row, int col) { return grid[row][col]; }

    public void displayBoard() {
        System.out.println();
        for (int row = 0; row < size; row++) {
            StringBuilder sb = new StringBuilder(" ");
            for (int col = 0; col < size; col++) {
                char value = grid[row][col];
                if (value == empty) {
                    sb.append(row * size + col + 1);
                } else {
                    sb.append(value);
                }
                if (col < size - 1) sb.append(" | ");
            }
            System.out.println(sb);
            if (row < size - 1) {
                StringBuilder sep = new StringBuilder(" ");
                for (int col = 0; col < size; col++) {
                    sep.append("---");
                    if (col < size - 1) sep.append("+");
                }
                System.out.println(sep);
            }
        }
        System.out.println();
    }

    public boolean isFull() {
        for (int row = 0; row < size; row++)
            for (int col = 0; col < size; col++)
                if (grid[row][col] == empty) return false;
        return true;
    }

    public char checkWin() {
        if (size != 3) {
            throw new UnsupportedOperationException(
                "checkWin поддерживает только 3×3. Для size=" + size + " нужна обобщённая версия.");
        }
        for (int row = 0; row < 3; row++) {
            if (grid[row][0] != empty
                    && grid[row][0] == grid[row][1]
                    && grid[row][1] == grid[row][2]) return grid[row][0];
        }
        for (int col = 0; col < 3; col++) {
            if (grid[0][col] != empty
                    && grid[0][col] == grid[1][col]
                    && grid[1][col] == grid[2][col]) return grid[0][col];
        }
        if (grid[0][0] != empty && grid[0][0] == grid[1][1] && grid[1][1] == grid[2][2])
            return grid[0][0];
        if (grid[0][2] != empty && grid[0][2] == grid[1][1] && grid[1][1] == grid[2][0])
            return grid[0][2];
        return empty;
    }

    public boolean placeMark(int row, int col, char mark) {
        if (row < 0 || row >= size || col < 0 || col >= size) return false;
        if (grid[row][col] != empty) return false;
        grid[row][col] = mark;
        return true;
    }

    public List<int[]> getEmptyCells() {
        List<int[]> cells = new ArrayList<>();
        for (int row = 0; row < size; row++)
            for (int col = 0; col < size; col++)
                if (grid[row][col] == empty) cells.add(new int[]{row, col});
        return cells;
    }
}