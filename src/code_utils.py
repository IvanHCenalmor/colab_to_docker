import re
import nbformat

installation_regex = r'(pip|conda) install'
float_regex = r"[-+]?\d*\.\d+|[-+]?\d+"
ipywidget_style = "{'description_width': 'initial'}"
param_regex = r"(\w+)\s*=\s*([\S\s]+?)\s*#@param\s*(.+)"
def param_to_widget(code: str) -> str:
    """
    This function converts colab's form params into interactive widgets. It takes a string as input and returns a string.
    @param code: a string containing the function parameters.
    @return: a string that contains the generated widgets for each parameter that can be used to make the function interactive.
    """
    
    match_param = re.search(param_regex, code)
    var_name = match_param.group(1)
    default_value = match_param.group(2)
    post_param = match_param.group(3)
    
    match_type = re.findall(r"{type:\"(\w+)\".*}", post_param)
    param_type = match_type[0] if match_type else None

    match_list = re.findall(r"(\[.*?\])", post_param)
    if match_list:
        possible_values = match_list[0]

    if match_list:
        if re.findall(r"{allow-input:\s*true}", post_param):
            result = f'aux_{var_name} = widgets.Combobox(options={possible_values}, placeholder={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
        else:
            if ',' in possible_values:
                list_possible_values = [item.strip() for item in possible_values.strip('[]').split(',')]
            else:
                list_possible_values =  [item.strip() for item in possible_values.strip('[]')]
            default_value = default_value if default_value in list_possible_values else list_possible_values[0]
            result = f'aux_{var_name} = widgets.Dropdown(options={possible_values}, value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
    elif param_type is not None:
        if param_type == "slider":
            min, max, step = re.findall(f"\s*min:({float_regex}),\s*max:({float_regex}),\s*step:({float_regex})", post_param)[0]
            try:
                min, max, step = int(min), int(max), int(step)
                result = f'aux_{var_name} = widgets.IntSlider(value={default_value}, min={min}, max={max}, step={step}, style={ipywidget_style}, description="{var_name}:")\n'
            except:
                min, max, step = float(min), float(max), float(step)
                result = f'aux_{var_name} = widgets.FloatSlider(value={default_value}, min={min}, max={max}, step={step}, style={ipywidget_style}, description="{var_name}:")\n'
        if param_type == "integer":
            result = f'aux_{var_name} = widgets.IntText(value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
        elif param_type == "number":
            result = f'aux_{var_name} = widgets.FloatText(value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
        elif param_type == "boolean":
            result = f'aux_{var_name} = widgets.Checkbox(value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
        elif param_type == "string" or param_type == "raw":
            result = f'aux_{var_name} = widgets.Text(value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
        elif param_type == "date":
            result = ('from datetime import datetime\n'
                      f'aux_{var_name} = widgets.DatePicker(value=datetime.strptime({default_value}, "%Y-%m-%d"),style={ipywidget_style}, description="{var_name}:")\n'
                      )
    else:
        # Even if it has #@param, it does not follow colab param format
        return code, ''
            
    # In case it has colab param format 
    result += f'display(aux_{var_name})'
    return result, var_name

def extract_values_from_variables(variable_list):
    resutl = '# Run this cell to extract the selected values in previuous cell\n'
    for var in variable_list:
        resutl += f"{var} = aux_{var}.value\n"
    return resutl

def clear_excesive_empty_lines(data: str) -> str:
    # Split the string into a list of lines
    lines = data.splitlines()

    # Remove consecutive empty lines
    new_lines = []
    for i, line in enumerate(lines):
        if i == 0 or line.strip() or lines[i-1].strip():
            new_lines.append(line)

    # Join the lines back into a string
    new_string = "\n".join(new_lines)

    return new_string

def is_only_comments(code):
    is_only_comments = all(line.strip().startswith('#') or not line.strip() for line in code.split('\n'))
    return is_only_comments

def code_to_cell(code, ipywidget_imported):

    lines = code.split('\n')    

    widget_code = ''
    non_widget_code = '# Run this cell to execute the code\n'
    widget_var_list = []

    for line in lines:
        # Check if the line is an installation line
        if re.search(installation_regex, line):
            pass
        elif re.search(param_regex, line):
            new_line, var_name = param_to_widget(line)
            if var_name != "" and var_name not in widget_var_list:
                widget_var_list.append(var_name)
            widget_code += new_line + '\n'
        else:
            non_widget_code += line + '\n'

    new_cells = []

    if widget_var_list:
        if not ipywidget_imported:
            widget_code = ("# Run this cell to visualize the parameters\n"
                           "import ipywidgets as widgets\n"
                           "from IPython.display import display, clear_output\n"
                           "clear_output()\n\n"
                           ) + widget_code
            ipywidget_imported = True
        else:
            widget_code = "# Run this cell to visualize the parameters\nclear_output()\n\n" + widget_code

        aux_cell = nbformat.v4.new_code_cell(widget_code)
        # Hides the content in the code cells
        aux_cell.metadata["cellView"] = "form"
        aux_cell.metadata["collapsed"] = True
        aux_cell.metadata["jupyter"] = {"source_hidden": True}
        new_cells.append(aux_cell)

        widget_variables_code = extract_values_from_variables(widget_var_list)
        aux_cell = nbformat.v4.new_code_cell(widget_variables_code)
        # Hides the content in the code cells
        aux_cell.metadata["cellView"] = "form"
        aux_cell.metadata["collapsed"] = True
        aux_cell.metadata["jupyter"] = {"source_hidden": True}
        new_cells.append(aux_cell)

    if not is_only_comments(non_widget_code):
        #Create the code cell
        aux_cell = nbformat.v4.new_code_cell(clear_excesive_empty_lines(non_widget_code))
        # Hides the content in the code cells
        aux_cell.metadata["cellView"] = "form"
        aux_cell.metadata["collapsed"] = True
        aux_cell.metadata["jupyter"] = {"source_hidden": True}
                
        new_cells.append(aux_cell)
    
    return new_cells, ipywidget_imported