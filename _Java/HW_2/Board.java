import java.util.ArrayList;
import java.util.List;

public class Board {
    
    private final char[][] grid = new char[3][3];
    
    

    public Board() {
        for (int row = 0; row < 3; row++) {
            for(int col = 0; col < 3; col++) {
                grid[row][col] = ' ';
            }
        }
    }

    public void displayBoard() {
        System.out.println();
        for (int row = 0; row < 3; row++) {
            StringBuilder sb = new StringBuilder(" ");
            for (int col = 0; col < 3; col++) {
                char value = grid[row][col];
                if (value == ' ') {
                    sb.append(row * 3 + col + 1);
                } else {
                    sb.append(value);
                }
                if (col < 2) {
                    sb.append(" | ");
                }
            }
            System.out.println(sb);
            if (row < 2) {
                System.out.println("---+---+---");
            }
        }
        System.out.println(" ");
    }

    public boolean isFull() {
        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 3; col++) {
                if (grid[row][col] == ' '){
                    return false;
                }
            }
        }
        return  true;
    }

    public char checkWin() {
        for (int row = 0; row < 3; row++) {
            if (grid[row][0] != ' '
                    && grid[row][0] == grid[row][1]
                    && grid[row][1] == grid[row][2]) {
                return grid[row][0];
            }
        }
        for (int col = 0; col < 3; col++) {
            if (grid[0][col] != ' '
                    && grid[0][col] == grid[1][col]
                    && grid[1][col] == grid[2][col]) {
                return grid[0][col];
            }
        }
        
        if (grid[0][0] != ' '
                && grid[0][0] == grid[1][1]
                && grid[1][1] == grid[2][2]) {
            return grid[0][0];
        }
        if (grid[0][2] != ' '
                && grid[0][2] == grid[1][1]
                && grid[1][1] == grid[2][0]) {
            return grid[0][2];
        }
        return ' ';
    }


    public boolean placeMark(int row, int col, char mark) {
        if (row < 0 || row > 2 || col < 0 || col > 2) {
            return false;
        }
        if (grid[row][col] != ' ') {
            return false;
        }
        grid[row][col] = mark;
        return true;
    }

    public List<int[]> getEmptyCells() {
        List<int[]> cells = new ArrayList<>();
        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 3; col++) {
                if (grid[row][col] == ' ') {
                    cells.add(new int[]{row, col});
                }
            }
        }
        return cells;
    }

}