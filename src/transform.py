import nbformat
# from src.code_utils import code_to_cell
from code_utils_one_cell import code_to_cell
from markdown_utils import markdown_to_cell
from sections import remove_section_list

def transform_nb(path_original_nb, path_new_nb, remove_sections = []):
    colab_nb = nbformat.read(path_original_nb, as_version=4)

    section_localizer = {}
    cell_idx = 0
    ipywidget_imported = False

    new_nb = nbformat.v4.new_notebook()
    for cell in colab_nb.cells:
        new_cells = []
        if cell.cell_type == "code":
            code = cell.source
            new_cells, ipywidget_imported = code_to_cell(code, ipywidget_imported, function_name='function')
        elif cell.cell_type == "markdown":
            text = cell.source
            new_text, section_localizer = markdown_to_cell(text, section_localizer, cell_idx)
            new_cells = [nbformat.v4.new_markdown_cell(new_text)]
            
        if new_cells:
            new_nb.cells.extend(new_cells)
            cell_idx += len(new_cells)

    new_nb.cells, section_localizer = remove_section_list(cells=new_nb.cells, 
                                                          section_localizer=section_localizer,
                                                          section_list = remove_sections)
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

    """
    for notebook_name in notebook_list:
        print(notebook_name)
        path_original_nb = os.path.join("../notebooks/", notebook_name)
        path_new_nb = os.path.join("../colabless_notebooks/", notebook_name)
        transform_nb(path_original_nb, path_new_nb, remove_sections = remove_section_dict[notebook_name])
    """

if __name__ == "__main__":
    main()