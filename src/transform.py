import nbformat
from code_utils_one_cell import code_to_cell
from markdown_utils import markdown_to_cell
from sections import remove_section_list

import nbformat

def transform_nb(path_original_nb, path_new_nb, remove_sections=[]):
    """
    Transforms a Jupyter notebook by converting code cells and markdown cells
    according to specific rules and removes specified sections.

    Args:
        path_original_nb (str): Path to the original Jupyter notebook file.
        path_new_nb (str): Path to the new transformed Jupyter notebook file.
        remove_sections (list): List of section names to be removed.

    Returns:
        None
    """

    # Read the original notebook
    colab_nb = nbformat.read(path_original_nb, as_version=4)

    # Initialize variables
    section_localizer = {}
    cell_idx = 0
    ipywidget_imported = False

    # Create a new notebook
    new_nb = nbformat.v4.new_notebook()

    # Iterate over each cell in the original notebook
    for cell in colab_nb.cells:
        new_cells = []

        # If the cell is a code cell
        if cell.cell_type == "code":
            code = cell.source
            # Convert code to cells and track if ipywidgets is imported
            new_cells, ipywidget_imported = code_to_cell(code, ipywidget_imported, function_name='function')

        # If the cell is a markdown cell
        elif cell.cell_type == "markdown":
            text = cell.source
            # Convert markdown to a cell
            new_text, section_localizer = markdown_to_cell(text, section_localizer, cell_idx)
            new_cells = [nbformat.v4.new_markdown_cell(new_text)]

        # If new cells are created, add them to the new notebook
        if new_cells:
            new_nb.cells.extend(new_cells)
            cell_idx += len(new_cells)

    # Remove specified sections from the markdown cells in the new notebook
    new_nb.cells, section_localizer = remove_section_list(cells=new_nb.cells,
                                                          section_localizer=section_localizer,
                                                          section_list=remove_sections)

    # Save the new notebook to a file
    nbformat.write(new_nb, path_new_nb)

def main():
    import os
    import argparse
 
    parser = argparse.ArgumentParser(description="Convert colab notebook to docker notebook",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-p", "--path", help="path of the notebook")
    parser.add_argument("-n", "--name", help="name of the notebook")
    parser.add_argument("-s", "--sections", help="list with the sections to temove", nargs='+', default = [])
    args = vars(parser.parse_args())
    
    path_original_nb = os.path.join(args["path"], args["name"])
    path_new_nb = os.path.join(args["path"], "colabless_" + args["name"])
    transform_nb(path_original_nb, path_new_nb, remove_sections = args["sections"])

if __name__ == "__main__":
    main()