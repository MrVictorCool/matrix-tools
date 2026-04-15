import click
from click_shell import shell

import importlib

from fractions import Fraction
import matrix
from matrix import Matrix

class SessionData:
    def __init__(self) -> None:
        self.matrices : dict[str, Matrix] ={}
        self.current_matrix : Matrix = None
        self.swap_counter : int = -1
        self.scalar_mult_list : list[Fraction]
        

sd : SessionData = SessionData()

@shell(prompt='mcalc > ', context_settings=dict(ignore_unknown_options=True, allow_interspersed_args=True), intro='Matrix Calculator Started.')
def app():
    pass

@app.command()
@click.argument('r', type=int)
@click.argument('c', type=int)
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
@click.option('--line_position', '-l', default = "-1", type = int, help = "Line position for augmented matrix")
@click.option('--empty', '-e', is_flag = True, help = "Fill the matrix with zeroes instead of writing values manually.")
def new(r, c, name, line_position, empty):
    m : Matrix
    if not empty:
        m = Matrix.from_input(r, c)
    else:
        m = Matrix.zeroes(r, c)

    m.line_placement = line_position

    if name != "":
        sd.matrices[name] = m
        click.echo(f"Created {r}x{c} matrix at {name}.")
        return
    
    sd.current_matrix = m
    click.echo(f"Created {r}x{c} matrix.")

@app.command()
@click.argument('name', type = str, default = "")
def show(name) -> None:
    if name != "":
        if name in sd.matrices:
            click.echo(sd.matrices[name])
        else:
            click.echo(f"{name} matrix not found.")
        return
    click.echo(sd.current_matrix)

@app.command()
@click.option('--workspace', '-w', is_flag = True, help = "Conserve workspace matrix")
def wipe(workspace) -> None:
    if workspace:
        sd.matrices.clear
        return
    
    sd.current_matrix = None
    sd.matrices.clear

@app.command()
@click.argument('from_key', type = str)
@click.argument('to_key', type = str, default = "")
def save(from_key, to_key):
    if to_key == "":
        sd.matrices[from_key] = sd.current_matrix
        click.echo(f"Saved workspace matrix as {from_key}")
    else:
        sd.matrices[to_key] = sd.matrices[from_key]
        click.echo(f"Saved {from_key} as {to_key}")


@app.command()
def reload() -> None:
    importlib.reload(matrix)
    if sd.current_matrix is not None:
        sd.current_matrix = Matrix(sd.current_matrix.data)
    for mkey in sd.matrices.keys():
        sd.matrices[mkey] = Matrix(sd.matrices[mkey].data)

@app.command()
@click.argument('n', type = int)
@click.argument('mkey', type=str, default="")
@click.option('--start_at_zero', '-sz', '-s0', "-s", is_flag = True, help = "Makes the row consulted start at zero like it works internally but usually matrices star at index 1.")
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
def row(n, mkey, start_at_zero, name):
    if mkey == "":
        m : Matrix = sd.current_matrix
    else:
        m : Matrix = sd.matrices[mkey]

    result : Matrix = m.row(n, not start_at_zero)
    click.echo(result)

    if name == "":
        sd.current_matrix = result
    else:
        sd.matrices[name] = result
        click.echo(f"Saved at {name}")

@app.command()
@click.argument('r', type = int)
@click.argument('mkey', type=str, default="")
@click.option('--start_at_zero', '-sz', '-s0', "-s", is_flag = True, help = "Makes the row consulted start at zero like it works internally but usually matrices star at index 1.")
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
def replace_row(r, mkey, start_at_zero, name):
    if mkey == "":
        m : Matrix = sd.current_matrix
    else:
        m : Matrix = sd.matrices[mkey]

    new_row : Matrix = Matrix.from_input(1, m.cols)

    result : Matrix = m.set_row(r, new_row, not start_at_zero)

    click.echo(result)

    if name == "":
        sd.current_matrix = result
    else:
        sd.matrices[name] = result
        click.echo(f"Saved at {name}")

app.add_command(replace_row, name = 'rrow')
app.add_command(replace_row, name = 'rr')

@app.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('r1', type = int)
@click.argument('r2', type = int)
@click.argument('s', type = Fraction, default=Fraction(1))
@click.argument('mkey', type=str, default="")
@click.option('--start_at_zero', '-sz', '-s0', "-s", is_flag = True, help = "Makes the row consulted start at zero like it works internally but usually matrices star at index 1.")
@click.option('--save_to_workspace', '-sw', '-w', is_flag = True, help = "Saves only to workspace.")
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
def row_addition(r1, r2, s, mkey, start_at_zero, save_to_workspace, name):
    if mkey == "":
        m : Matrix = sd.current_matrix
    else:
        m : Matrix = sd.matrices[mkey]

    add_row : Matrix = m.row(r2, not start_at_zero) * s

    result : Matrix = m.add_to_row(r1, add_row, not start_at_zero)

    click.echo(result)

    if save_to_workspace:
        sd.current_matrix = result
        return
    if name == "":
        sd.matrices[mkey] = result
        click.echo(f"Updated matrix {name}")
    else:
        sd.matrices[name] = result
        click.echo(f"Saved at {name}")

app.add_command(row_addition, name = 'row_add')
app.add_command(row_addition, name = 'ra')

@app.command()
@click.argument('r1', type = int)
@click.argument('r2', type = int)
@click.argument('mkey', type=str, default="")
@click.option('--start_at_zero', '-sz', '-s0', "-s", is_flag = True, help = "Makes the row consulted start at zero like it works internally but usually matrices star at index 1.")
@click.option('--save_to_workspace', '-sw', '-w', is_flag = True, help = "Saves only to workspace.")
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
def swap_rows(r1, r2, mkey, start_at_zero, save_to_workspace, name):
    if mkey == "":
        m : Matrix = sd.current_matrix
    else:
        m : Matrix = sd.matrices[mkey]

    result : Matrix = m.swap_row(r1, r2, not start_at_zero)

    click.echo(result)

    if save_to_workspace:
        sd.current_matrix = result
        return
    if name == "":
        sd.matrices[mkey] = result
        click.echo(f"Updated matrix {name}")
    else:
        sd.matrices[name] = result
        click.echo(f"Saved at {name}")

app.add_command(swap_rows, name = 'swapr')
app.add_command(swap_rows, name = 'sr')

@app.command()
@click.argument('n', type = int)
@click.argument('mkey', type=str, default="")
@click.option('--start_at_zero', '-sz', '-s0', "-s", is_flag = True, help = "Makes the column consulted start at zero like it works internally but usually matrices star at index 1.")
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
def column(n, mkey, start_at_zero, name):
    if mkey == "":
        m : Matrix = sd.current_matrix
    else:
        m : Matrix = sd.matrices[mkey]

    result : Matrix = m.col(n, not start_at_zero)
    click.echo(result)

    if name == "":
        sd.current_matrix = result
    else:
        sd.matrices[name] = result
        click.echo(f"Saved at {name}")

app.add_command(column, name = 'col')

@app.command()
@click.argument('c', type = int)
@click.argument('mkey', type=str, default="")
@click.option('--start_at_zero', '-sz', '-s0', "-s", is_flag = True, help = "Makes the column consulted start at zero like it works internally but usually matrices star at index 1.")
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
def replace_column(c, mkey, start_at_zero, name):
    if mkey == "":
        m : Matrix = sd.current_matrix
    else:
        m : Matrix = sd.matrices[mkey]

    new_col : Matrix = Matrix.from_input(m.rows, 1)

    result : Matrix = m.set_col(c, new_col, not start_at_zero)

    click.echo(result)

    if name == "":
        sd.current_matrix = result
    else:
        sd.matrices[name] = result
        click.echo(f"Saved at {name}")

app.add_command(replace_column, name = 'replace_col')
app.add_command(replace_column, name = 'rcol')
app.add_command(replace_column, name = 'rc')

@app.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('mkey1', type = str)
@click.argument('mkey2', type = str, default = "")
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
def add(mkey1, mkey2, name):
    if mkey2 == "":
        m2 : Matrix = sd.current_matrix
    else:
        m2 : Matrix = sd.matrices[mkey2]
    
    m1: Matrix = sd.matrices[mkey1]

    result : Matrix = m1 + m2

    click.echo(result)

    if name == "":
        sd.current_matrix = result
    else:
        sd.matrices[name] = result
        click.echo(f"Saved at {name}")

@app.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('mkey1', type = str)
@click.argument('mkey2', type = str, default = "")
@click.argument('scalar', type = Fraction, default = Fraction(1))
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
def addm(mkey1, scalar, mkey2, name):
    if mkey2 == "":
        m2 : Matrix = sd.current_matrix
    else:
        m2 : Matrix = sd.matrices[mkey2]
    
    m1: Matrix = sd.matrices[mkey1]

    result : Matrix = m1 + m2 * scalar

    click.echo(result)

    if name == "":
        sd.current_matrix = result
    else:
        sd.matrices[name] = result
        click.echo(f"Saved at {name}")

@app.command()
@click.argument('mkey1', type = str)
@click.argument('mkey2', type = str, default = "")
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
def sub(mkey1, mkey2, name):
    if mkey2 == "":
        result : Matrix = sd.current_matrix - sd.matrices[mkey1]
    else:
        result : Matrix = sd.matrices[mkey1] - sd.matrices[mkey2]

    click.echo(result)

    if name == "":
        sd.current_matrix = result
    else:
        sd.matrices[name] = result
        click.echo(f"Saved at {name}")

app.add_command(sub, name = 'subtract')

"""Matrix multiplication, if only given one argument it multiplies it to workspace matrix by the right side"""
@app.command()
@click.argument('mkey1', type = str)
@click.argument('mkey2', type = str, default = "")
@click.option('--left', '-l', is_flag = True, help = "It allows to multiply workspace matrix by the left side, or inverts the order when given two matrices.")
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
def mmult(mkey1, mkey2, left, name):
    if mkey2 == "":
        m1 : Matrix = sd.current_matrix
        m2 : Matrix = sd.matrices[mkey1]
    else:
        m1 : Matrix = sd.matrices[mkey1]
        m2 : Matrix = sd.matrices[mkey2]
    

    result : Matrix = m1 * m2 if not left else m2 * m1

    click.echo(result)

    if name == "":
        sd.current_matrix = result
    else:
        sd.matrices[name] = result
        click.echo(f"Saved at {name}")

app.add_command(mmult, 'mm')
app.add_command(mmult, 'matrix_multiplication')

@app.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('a', type=Fraction)
@click.argument('mkey', type=str, default="")
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
def smult(a, mkey, name):
    if mkey == "":
        m2 : Matrix = sd.current_matrix
    else:
        m2 : Matrix = sd.matrices[mkey]

    result : Matrix = m2 * a

    click.echo(result)

    if name == "":
        sd.current_matrix = result
    else:
        sd.matrices[name] = result
        click.echo(f"Saved at {name}")

app.add_command(smult, 'sm')
app.add_command(smult, 'scalar_multiplication')

@app.command()
@click.argument('mkey', type = str, default = "")
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
@click.option('--verbose', '-v', is_flag = True, help = "Verbose I guess.")
def inverse(mkey, name, verbose):
    if mkey == "":
        m : Matrix = sd.current_matrix
    else :
        m : Matrix = sd.matrices[mkey]
    
    result_m : Matrix = m.inverse(verbose)

    click.echo(result_m)

    if name:
        sd.matrices[name] = result_m
    else :
        sd.current_matrix = result_m

@app.command()
@click.argument('mkey', type = str, default = "")
@click.option('--verbose', '-v', is_flag = True, help = "Verbose I guess.")
def det(mkey, verbose):
    if mkey == "":
        m : Matrix = sd.current_matrix
    else :
        m : Matrix = sd.matrices[mkey]

    click.echo(m.det(Matrix.DeterminantTypes.COFACTOR, verbose))

app.add_command(det, 'd')

@app.command()
@click.argument('mkey', type = str, default = "")
@click.option('--verbose', '-v', is_flag = True, help = "Verbose I guess.")
def gauss_det(mkey, verbose):
    if mkey == "":
        m : Matrix = sd.current_matrix
    else :
        m : Matrix = sd.matrices[mkey]

    click.echo(m.det(Matrix.DeterminantTypes.GAUSSIAN_ELIMINATION, verbose))

app.add_command(gauss_det, 'gdet')
app.add_command(gauss_det, 'gd')

@app.command()
@click.argument('mkey', type = str, default = "")
@click.option('--verbose', '-v', is_flag = True, help = "Verbose I guess.")
@click.option('--preserve-determinant', '-pd', '-d', is_flag = True, help = "Self explanatory")
@click.option('--jordan-pivots', '-jp', '-p1', '-j', is_flag = True, help = "Self explanatory")
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
def gaussian_elimination(mkey, verbose, preserve_determinant, jordan_pivots, name):
    if mkey == "":
        m : Matrix = sd.current_matrix
    else :
        m : Matrix = sd.matrices[mkey]

    result_m : Matrix = m.upper_triangular(verbose, preserve_determinant, jordan_pivots)

    click.echo(result_m)

    if name:
        sd.matrices[name] = result_m
    else :
        sd.current_matrix = result_m


app.add_command(gaussian_elimination, 'gelim')
app.add_command(gaussian_elimination, 'ge')

@app.command()
@click.argument('mkey', type = str, default = "")
@click.option('--verbose', '-v', is_flag = True, help = "Verbose I guess.")
@click.option('--name', '-n', default = "", type = str, help = "Chose a name to store the matrix, if it is left blank or this argument is not included it goes to the workspace matrix")
def adj(mkey, verbose, name):

    if mkey == "":
        m : Matrix = sd.current_matrix
    else :
        m : Matrix = sd.matrices[mkey]

    result : Matrix = m.adj(verbose)
    click.echo(result)

    if name:
        sd.matrices[name] = result
    else:
        sd.current_matrix = result

#Run the shell
if __name__ == "__main__":
    app()
    
