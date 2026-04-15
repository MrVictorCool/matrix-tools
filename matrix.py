from __future__ import annotations
from fractions import Fraction
from enum import Enum, auto

class Matrix:
    rows: int
    cols : int
    data : list[list[Fraction]]

    class DeterminantTypes(Enum):
        COFACTOR = auto()
        GAUSSIAN_ELIMINATION = auto()
    
    #region Constructors
    def __init__(self, data: list[list[Fraction]], line_placement : int = 0) -> None:
        self.data = [list(row) for row in data]
        self.rows = len(data)
        self.cols = len(data[0])
        self._line_placement = line_placement
    
    @property
    def line_placement(self) -> int:
        return self._line_placement

    @line_placement.setter
    def line_placement(self, value) -> None:
        if value in range(1, self.cols):
            self._line_placement = value
            return
        
        self._line_placement = 0

    
    @classmethod
    def zeroes(cls, r : int, c : int) -> Matrix:
        data: list[list[Fraction]] = [[Fraction(0) for _ in range(c)] for _ in range(r)]

        return cls(data)

    @classmethod
    def identity(cls, size):
        data: list[list[Fraction]] = [
            [Fraction(1 if i == j else 0) for i in range(size)] 
            for j in range(size)
        ]

        return cls(data)

    @classmethod
    def from_input(cls, rows: int, cols: int):
        print(f"Enter a {rows}x{cols} matrix (space-separated values):")
        
        new_matrix = cls.zeroes(rows, cols)
        
        for i in range(rows):
            line = input(f"Row {i+1}: ")
            row_values = [Fraction(val) for val in line.split()]
            
            if len(row_values) != cols:
                raise ValueError(f"Expected {cols} values, got {len(row_values)}")
            
            new_matrix.data[i] = row_values
            
        return new_matrix

    #endregion

    #region Attributes
    def __repr__(self) -> str:
        string_matrix : list[list[str]] = [
            [str(self[row][col])for col in range(self.cols)] 
            for row in range(self.rows)
        ]

        max_w = max(len(s) for row in string_matrix for s in row)
        
        if self.line_placement in range(1, self.cols):
            for row in string_matrix:
                row.insert(self.line_placement, "|")

        lines = []
        for row in string_matrix:
            formatted_row = f"|{"  ".join([f"{s:^{max_w}}" for s in row])}|"
            lines.append(formatted_row)

        # for row in string_matrix:
        #     formatted_row = f"|{"  ".join([f"{s:^{max_w}}" for s in row])}|"
        #     lines.append(formatted_row)
            
        return "\n".join(lines)
    
    @property
    def dimensions(self) -> tuple[int,int]:
        return (self.rows, self.cols)
    
    #endregion

    # region Basic interaction
    def set(self, value: Fraction, row: int, col: int) -> None:
        self.data[row][col] = value
    
    def get(self, row: int, col: int) -> Fraction:
        return self.data[row][col]
    
    # endregion

    #region Operators

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value) -> None:
        self.data[key] = value

    def __add__(self, other):
        if not isinstance(other, Matrix) or self.dimensions != other.dimensions:
            raise ValueError("Matrices must be of the same size to perform addition")
        
        result_data : list[list[Fraction]] = [[self[i][j] + other[i][j] for j in range(self.cols)] for i in range(self.rows)]

        return Matrix(result_data, self.line_placement)
    
    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        result_data : list[list[Fraction]] = [[-self[i][j] for i in range(self.cols)] for j in range(self.rows)]

        return Matrix(result_data, self.line_placement)
    
    def __eq__(self, value: object) -> bool:
        return not self != value

    def __ne__(self, value: object) -> bool:
        if not isinstance(value, Matrix):
            return False
        
        other : Matrix = value

        if self.dimensions != other.dimensions:
            return False
        
        for i in range(self.rows):
            for j in range(self.cols):
                if (self[i][j] != other[i][j]):
                    return False
        
        return True

    def __bool__(self):
        return self != Matrix.zeroes(self.rows, self.cols)

    def __mul__(self, other):
        if isinstance(other, (int, float, Fraction)):
            return Matrix.scalar_mult(self, Fraction(other))
        
        if not isinstance(other, Matrix):
            raise ValueError("Can only multiply matrices by other matrices or scalar values.")
        
        if self.cols != other.rows:
            raise ValueError("For matrix multiplication the number of columns of the first matrix must be the number of rows of the second matrix")
        
        result_data : list[list[Fraction]] = [[Matrix.dot_product(self[i], [other[r][j] for r in range(other.rows) ]) for j in range(other.cols)] for i in range(self.rows)]

        return Matrix(result_data, self.line_placement)

    def __rmul__(self, other):
        if isinstance(other, (int, float, Fraction)):
            return self * other
        
        raise ValueError("Can only multiply matrices by other matrices or scalar values.")
    
    def __truediv__(self, other):
        if isinstance(other, (int, float, Fraction)):
            raise ValueError("Only division by scalars is allowed, use inverse for matrices.")
        
        if other == 0:
            raise ValueError("Division by zero.")
        
        return self * other ** -1

    def __matmul__(self, other):
        return self.__mul__(other)
    

    @classmethod
    def dot_product(cls, v1 : list[Fraction], v2 : list[Fraction]) -> Fraction:
        total : Fraction = Fraction(0)
        for a, b in zip(v1, v2):
            total += a * b
        
        return total

    @classmethod
    def scalar_mult(cls, m : Matrix, n : Fraction) -> Matrix:
        result_data : list[list[Fraction]] = [[m[i][j] * n for j in range(m.cols)] for i in range(m.rows)]

        return cls(result_data)

    def row(self, n : int, start1 : bool = False) -> Matrix:
        if start1: n -= 1
        result_data : list[list[Fraction]] = [[self[n][col] for col in range(self.cols)]]

        return Matrix(result_data, self.line_placement)

    def col(self, n : int, start1 : bool = False) -> Matrix:
        if start1: n -= 1
        result_data : list[list[Fraction]] = [[self[row][n]] for row in range(self.rows)]

        return Matrix(result_data, self.line_placement)
    
    def set_row(self, r : int, new_row : Matrix, start1 : bool = False) -> Matrix:
        if start1: r -= 1

        m : Matrix = Matrix(self.data, self.line_placement)

        for c in range(new_row.cols):
            m[r][c] = new_row[0][c]

        return m
    
    def set_col(self, c : int, new_col : Matrix, start1 : bool = False) -> Matrix:
        if start1: c -= 1

        m : Matrix = Matrix(self.data, self.line_placement)

        for r in range(new_col.rows):
            m[r][c] =new_col[r][0]

        return m

    def swap_row(self, a : int, b: int, start1: bool = False) -> Matrix:
        if start1:
            a -= 1
            b -= 1

        if not (a in range(self.rows) and b in range(self.rows)):
            raise ValueError(f"{a} or {b} outside of range size {self.rows} (start at 0).")
        
        m: Matrix = Matrix(self.data, self.line_placement)
        m[a], m[b] = m[b], m[a]

        return m
    
    def swap_col(self, a : int, b: int) -> Matrix:
        if not (a in range(self.rows) and b in range(self.rows)):
            raise ValueError(f"{a} or {b} outside of range size {self.rows} (start at 0).")
        
        m: Matrix = Matrix(self.data, self.line_placement)
        for i in range(self.rows):
            m[i][a], m[i][b] = m[i][b], m[i][a]

        return m

    def add_to_row(self, r: int, add_row : Matrix, start1 : bool = False) -> Matrix:
        if start1: r -= 1

        m : Matrix = Matrix(self.data, self.line_placement)

        for i in range(self.cols):
            m[r][i] += add_row[0][i]

        return m
    
    def scale_row(self, r: int, s: Fraction, start1 : bool = False) -> Matrix:
        if start1: r -= 1

        m : Matrix = Matrix(self.data, self.line_placement)

        for i in range(self.cols):
            m[r][i] *= s

        return m

    def transposed(self) -> Matrix:
        m: Matrix = Matrix.zeroes(self.cols, self.rows)
        for row in range(0, m.rows):
            for col in range(0, m.cols):
                m.set(self.get(col, row), row, col)
        
        return m
    
    def minor(self, r: int, c: int) -> Matrix:
        m : Matrix = Matrix.zeroes(self.rows - 1, self.cols -1)
        for i in range(0 , m.rows):
            for j in range(0, m.cols):
                i_source = i if i < r else i + 1
                j_source = j if j < c else j + 1

                m[i][j] = self[i_source][j_source]
        return m

    def cofactor(self, r : int, c: int, verbose : bool = False) -> Fraction:
        min_m : Matrix = self.minor(r, c)
        if verbose:
            print(f"C({r + 1},{c + 1}) = (-1) ^ {r + 1} + {c + 1} * ")
            print(min_m)
            print(f"{"-" if (r + c) & 1 else ""}(", end = "")
            
        det_m : Fraction = min_m.det(self.DeterminantTypes.COFACTOR, verbose)
        if verbose:
            print(f"\003) = {Fraction(det_m * (-1 if (r + c) & 1 else 1))}", "\n")
        return Fraction(det_m * (-1 if (r + c) & 1 else 1))


    def det(self, type: DeterminantTypes, verbose: bool = False) -> Fraction:
        match type:
            case self.DeterminantTypes.COFACTOR:
                return self.det_cofactor(verbose)
            case self.DeterminantTypes.GAUSSIAN_ELIMINATION:
                return self.det_gauss(verbose)

    def det_cofactor(self, verbose: bool = False) -> Fraction:
        if self.cols != self.rows:
            raise ValueError("Matrix must be square.")
        
        match self.rows:
            case 0:
                return Fraction(0)
            case 1:
                return self[0][0]
            case 2:
                if verbose:
                    print(f"{self[0][0] * self[1][1]} - {self[0][1] * self[1][0]}")
                return Fraction(self[0][0] * self[1][1] - self[0][1] * self[1][0])
            case 3:
                res : Fraction = Fraction(0)
                for i in range(3):
                    res += self[0][i % 3] * self[1][(i + 1) % 3] * self[2][(i + 2) % 3]
                    if verbose:
                        print(self[0][i % 3] * self[1][(i + 1) % 3] * self[2][(i + 2) % 3], end= "" if i == 2 else " + ")

                if verbose: print("-(", end="")
                for i in range(3):
                    res -= self[2][i % 3] * self[1][(i + 1) % 3] * self[0][(i + 2) % 3]
                    if verbose:
                        print(self[2][i % 3] * self[1][(i + 1) % 3] * self[0][(i + 2) % 3], end= "" if i == 2 else " + ")
                if verbose: print(") = ")
            case _:
                res : Fraction = Fraction(0)
                for col in range(self.cols):
                    calc : Fraction = self[0][col] * self.cofactor(0, col, verbose)
                    res += self[0][col] * self.cofactor(0, col)
        
        return res

    def det_gauss(self, verbose: bool = False) -> Fraction:
        m : Matrix = Matrix(self.data, self.line_placement).upper_triangular(verbose, True)
        det_m: Fraction = Fraction(1)
        for i in range(self.rows):
            det_m *= m[i][i]
        #TODO: check this works
        return det_m
    
    def gauss_jordan(self, verbose: bool = False) -> Matrix:
        m : Matrix = Matrix(self.data, self.line_placement)
        m = m.upper_triangular(verbose, False, True)
        m = m.lower_triangular(verbose)
        return m

    def upper_triangular(self, verbose: bool = False, preserve_determinant : bool = False, jordan_pivots: bool = False) -> Matrix:
        m: Matrix = Matrix(self.data, self.line_placement)
        for c in range(m.rows - 1):
            if m[c][c] == 0:
                new_pivot_row: int = -1
                for r in range(1 + c, m.rows):
                    if m[r][c] != 0:
                        new_pivot_row = r
                        break
                
                if new_pivot_row != -1:
                    if verbose: print(f"R{c} <-> R{new_pivot_row}")
                    m = m.swap_row(c, new_pivot_row)
                    print(m)
                    if preserve_determinant:
                        m = m.scale_row(c, -1)
                        if verbose: 
                            print(f"R{c}(-1) to preserve determinant.")
                            print(m, "\n")
                else:
                    raise ValueError("Couldn't do upper_triangular matrix, should mean the determinant is zero.")
            
            if jordan_pivots and m[c][c] != 1:
                if verbose: print(f"F{c + 1}({m[c][c] ** -1})")
                m = m.scale_row(c, Fraction(1, m[c][c]))
                if verbose: print(m, "\n")

            for r in range(1 + c, m.rows):
                if m[r][c] != 0:
                    scalar : Fraction = m[r][c] / m[c][c]
                    m = m.add_to_row(r, m.row(c) * -scalar)
                    if verbose:
                        print(f"R{r + 1} + {-scalar} R{c + 1}")
                        print(m, "\n")
        print(f"Last check {m[m.rows - 1][m.rows - 1]}")
        if jordan_pivots and m[m.rows - 1][m.rows - 1] != 1:
                if verbose: print(f"F{m.rows - 1}({m[m.rows - 1][m.rows - 1] ** -1})")
                m = m.scale_row(m.rows - 1, Fraction(1, m[m.rows - 1][m.rows - 1]))
                if verbose: print(m, "\n")
        
        return m
    
    def lower_triangular(self, verbose: bool = False) -> Matrix:
        m: Matrix = Matrix(self.data, self.line_placement)

        for c in range(m.rows - 1, 0, -1):
            # print(f"Column {c + 1}:")
            for r in range(c - 1, -1, -1):
                # print(f"Row {r + 1}:")
                # print(f"Checking {r + 1}, {c + 1}")
                if m[r][c] != 0:
                    scalar : Fraction = m[r][c] / m[c][c]
                    m = m.add_to_row(r, m.row(c) * -scalar)
                    if verbose:
                        print(f"R{r + 1} + {-scalar} R{c + 1}")
                        print(m, "\n")
        
        return m

    def adj(self, verbose: bool = False) -> Matrix:
        result_data : list[list[Fraction]] = [[self.cofactor(j, i, verbose) for j in range(self.cols)] for i in range(self.rows)]
        return Matrix(result_data, self.line_placement)
    
    def inverse(self, verbose : bool = False) -> Matrix:
        det : Fraction = self.det(self.DeterminantTypes.COFACTOR, verbose)
        if det == 0:
            raise ValueError("Determinant is 0 therefore the matrix has no inverse.")
        
        adj_m = self.adj(verbose)

        if verbose:
            print(f"{adj_m}\003 * {Fraction(1, det)}\n")
        return adj_m * (1 / det)
    #endregion