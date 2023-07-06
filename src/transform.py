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

    # TODO remove sections and receives a list and ensures that it does it in inverse order so that there is no problem when updating the section numbers
    new_nb.cells, section_localizer = remove_section_list(cells=new_nb.cells, 
                                                          section_localizer=section_localizer,
                                                          section_list = remove_sections)
    nbformat.write(new_nb, path_new_nb)

def main():
    import os
    
    notebook_list = sorted(os.listdir("../notebooks"))
    notebook_list.remove('.ipynb_checkpoints')
    remove_section_dict = {'CARE_2D_ZeroCostDL4Mic.ipynb': ["1.1.", "1.2.", "2.", "6.3."],
                            'CARE_3D_ZeroCostDL4Mic.ipynb': ["1.1.", "1.2.", "2.", "6.2."],
                            'CycleGAN_ZeroCostDL4Mic.ipynb': ["2.", "6.3."],
                            'Deep-STORM_2D_ZeroCostDL4Mic.ipynb': [ "2.", "6.4."],
                            'Noise2Void_2D_ZeroCostDL4Mic.ipynb': ["1.1.", "1.2.", "2.", "6.3."],
                            'Noise2Void_3D_ZeroCostDL4Mic.ipynb': ["1.1.", "1.2.", "2.", "6.2."],
                            'StarDist_2D_ZeroCostDL4Mic.ipynb': ["1.1.", "1.2.", "2.", "6.3."],
                            'StarDist_3D_ZeroCostDL4Mic.ipynb': ["1.1.", "1.2.", "2.", "6.2."],
                            'U-Net_2D_Multilabel_ZeroCostDL4Mic.ipynb': ["1.1.", "1.2.", "2.", "6.2."],
                            'U-Net_2D_ZeroCostDL4Mic.ipynb': ["1.1.", "1.2.", "2.", "6.3."],
                            'U-Net_3D_ZeroCostDL4Mic.ipynb': ["1.1.", "1.2.", "2.", "6.2."],
                            'YOLOv2_ZeroCostDL4Mic.ipynb': ["1.1.", "1.2.", "2.", "6.3."],
                            'fnet_2D_ZeroCostDL4Mic.ipynb': ["1.1.", "1.2.", "2.", "6.3."],
                            'fnet_3D_ZeroCostDL4Mic.ipynb': ["1.1.", "1.2.", "2.", "6.3."],
                            'pix2pix_ZeroCostDL4Mic.ipynb': ["2.", "6.3."],
                           }

    for notebook_name in notebook_list:
        print(notebook_name)
        path_original_nb = os.path.join("../notebooks/", notebook_name)
        path_new_nb = os.path.join("../colabless_notebooks/", notebook_name)
        transform_nb(path_original_nb, path_new_nb, remove_sections = remove_section_dict[notebook_name])

if __name__ == "__main__":
    main()