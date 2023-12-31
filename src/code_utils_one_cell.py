import re
import nbformat

# Usefull regular expressions 
installation_regex = r'(pip|conda) install'
float_regex = r"[-+]?\d*\.\d+|[-+]?\d+"
ipywidget_style = "{'description_width': 'initial'}"
param_regex = r"(\w+)\s*=\s*([\S\s]+?)\s*#@param\s*(.+)"

assignation_regex =  r'^\s*([a-zA-Z_]\w*(?:\s*,\s*[a-zA-Z_]\w*)*)\s*=\s*.*$'
function_regex = r"^\s*def\s+([a-zA-Z_]\w*)\s*\(.+\)\s*:\s*$"

raw_regex = r"\{type:\"raw\"\}"
comment_after_param_regex = r"(\[[^\]]*\]|\{[^}]*\})(?: [^#]*)?(\[[^\]]*\]|\{[^}]*\})* *#.*"

def param_to_widget(code):
    """
    Extracts components from a line with @param and creates ipywidgets based on the extracted information.
    Parameters:
        code (str): The line of code containing the @param component.

    Returns:
        str: The generated widget code.
        str: The name of the variable associated with the widget.
    """

    # Extract the components from a line with @param component
    match_param = re.search(param_regex, code)
    var_name = match_param.group(1)
    default_value = match_param.group(2)
    post_param = match_param.group(3)
    
    if re.match(comment_after_param_regex, post_param):
        # In case is the strange scenario with comment after @param 
        # And after it will be treated as raw parameter

        if '\'' in default_value or '\"' in default_value: 
            result = f'widget_{var_name} = widgets.Text(value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
        else:
            result = f'widget_{var_name} = widgets.Text(value="{default_value}", style={ipywidget_style}, description="{var_name}:")\n'
    else:
        # Extract the type of the @param
        match_type = re.findall(r"{type:\s*\"(\w+)\".*}", post_param)
        param_type = match_type[0] if match_type else None

        # Extract and check if instead of a type, a list is defined 
        match_list = re.findall(r"(\[.*?\])", post_param)
        if match_list:
            possible_values = match_list[0]

            if re.findall(r"{allow-input:\s*true}", post_param):
                # In case the variable allow-input is found, a Combobox ipywidget is added (allowing new inputs)
                result = f'widget_{var_name} = widgets.Combobox(options={possible_values}, placeholder={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
            else:
                # If not, a Dropdown ipywidget is added

                # In case the default value is not in the given list of possible values the first one will be selected
                # For that we need to extract the list of possible values and then check if it is in there
                if ',' in possible_values:
                    list_possible_values = [item.strip() for item in possible_values.strip('[]').split(',')]
                else:
                    list_possible_values =  [possible_values.strip('[]').strip()]
                default_value = default_value if default_value in list_possible_values else list_possible_values[0]

                if param_type is not None and param_type == "raw":
                    # In case its a raw parameter, a Dropdown ipywidget is added that will be then evaluated with eval()
                    possible_values = [str(i) for i in list_possible_values]
                    
                    if '\'' in default_value or '\"' in default_value: 
                        result = f'widget_{var_name} = widgets.Dropdown(options={possible_values}, value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
                    else:
                        result = f'widget_{var_name} = widgets.Dropdown(options={possible_values}, value="{default_value}", style={ipywidget_style}, description="{var_name}:")\n'
                else:
                    result = f'widget_{var_name} = widgets.Dropdown(options={possible_values}, value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'

        elif param_type is not None:
            # If it is not a list a list of values, it would be one of the following types (adding ipywidgets based on the type)
            if param_type == "slider":
                min, max, step = re.findall(f"\s*min:({float_regex}),\s*max:({float_regex}),\s*step:({float_regex})", post_param)[0]
                try:
                    min, max, step = int(min), int(max), int(step)
                    result = f'widget_{var_name} = widgets.IntSlider(value={default_value}, min={min}, max={max}, step={step}, style={ipywidget_style}, description="{var_name}:")\n'
                except:
                    min, max, step = float(min), float(max), float(step)
                    result = f'widget_{var_name} = widgets.FloatSlider(value={default_value}, min={min}, max={max}, step={step}, style={ipywidget_style}, description="{var_name}:")\n'
            if param_type == "integer":
                result = f'widget_{var_name} = widgets.IntText(value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
            elif param_type == "number":
                if '.' in default_value:
                    result = f'widget_{var_name} = widgets.FloatText(value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
                else:
                    result = f'widget_{var_name} = widgets.IntText(value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
            elif param_type == "boolean":
                result = f'widget_{var_name} = widgets.Checkbox(value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
            elif param_type == "string" or param_type == "raw":
                result = f'widget_{var_name} = widgets.Text(value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
            elif param_type == "date":
                result = ('from datetime import datetime\n'
                        f'widget_{var_name} = widgets.DatePicker(value=datetime.strptime({default_value}, "%Y-%m-%d"),style={ipywidget_style}, description="{var_name}:")\n'
                        )
        else:
            # Even if it has #@param, it does not follow colab param format
            return code, ''
            
    # In case it has colab param format 
    result += f'display(widget_{var_name})'
    return result, var_name

def extract_values_from_variables(variable_list):
    """
    Extracts the selected values from the given list of variables.
    Parameters:
        variable_list (list): A list of variables.
    Returns:
        str: A string containing the extracted values.
    """
    
    result = '# Run this cell to extract the selected values in previuous cell\n'
    for var in variable_list:
        result += f"{var} = widget_{var}.value\n"
    return result

def clear_excesive_empty_lines(data):
    """
    Remove excessive empty lines from the given string.
    Parameters:
    - data (str): The input string.

    Returns:
    - str: The string with excessive empty lines removed.
    """

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
    """
    Check if the given code consists only of comments.
    Parameters:
    - code (str): The code to be checked.
    Returns:
    - is_only_comments (bool): True if the code consists only of comments, False otherwise.
    """
    
    is_only_comments = all(line.strip().startswith('#') or not line.strip() for line in code.split('\n'))
    return is_only_comments

def count_spaces(sentence):
    """
    Count the number of leading spaces in a given sentence.
    Parameters:
        sentence (str): The sentence to count the leading spaces in.
    Returns:
        int: The number of leading spaces in the sentence.
    """
    
    match = re.match(r'^\s*', sentence)
    if match:
        return len(match.group(0))
    else:
        return 0

def code_to_cell(code, ipywidget_imported, function_name):
    """
    Generates a list of code cells for a Jupyter notebook based on the given code.
    Parameters:
    - code (str): The code to be converted into code cells.
    - ipywidget_imported (bool): Indicates whether the `ipywidgets` library has already been imported.
    - function_name (str): The name of the function to be created.
    Returns:
    - new_cells (list): A list of code cells generated from the given code.
    - ipywidget_imported (bool): An updated value indicating whether the `ipywidgets` library has been imported.
    """
 

    # Future lines of code that are based on widgets or not
    widget_code = ''
    non_widget_code = ''
    
    # List of variables and functions that need to be defined as global
    widget_var_list = []
    var_list = []
    func_list = []

    # We are going line by line analyzing them
    lines = code.split('\n')  
    for line in lines:
        if re.search(installation_regex, line):
            # The installation lines are removed
            pass
        elif re.search(param_regex, line):
            # The lines with #@param are replaced with ipywidgets based on the parameters
            new_line, var_name = param_to_widget(line)
            if var_name != "" and var_name not in widget_var_list:
                widget_var_list.append(var_name)
            widget_code += new_line + '\n'

            if re.search(raw_regex, line) or re.match(comment_after_param_regex, re.search(param_regex, line).group(3)):
                # In case the param is raw or it has a comment after @param, the value of the widget needs to evaluated
                non_widget_code += ' ' * count_spaces(line) + f"{var_name} = eval(widget_{var_name}.value)\n"
            else:
                non_widget_code += ' '*count_spaces(line) + f"{var_name} = widget_{var_name}.value\n"
        else:
            # In the other the variable and function names are extracted
            assign_match = re.match(assignation_regex, line)
            if assign_match:
                possible_variables = assign_match.group(1).split(',')
                for var in possible_variables:
                    var_list.append(var)
            
            function_match = re.match(function_regex, line)
            if function_match:
                func_list.append(function_match.group(1))

            # And the line is added as it is
            non_widget_code += line + '\n'

    new_cells = []

    if widget_var_list:
        # In case a param was found, everything will be encapsulated in a function

        # For that all the code needs to be tabbed inside the function
        tabbed_non_widget_code = ""
        for line in non_widget_code.split('\n'):
            tabbed_non_widget_code += " "*4 + line + '\n'

        # Global variables that will be inside the function in order to be accesible in the notebook
        global_widgets_var = "".join([" "*4 + f"global {var}\n" for var in widget_var_list])
        global_var = "".join([" "*4 + f"global {var}\n" for var in var_list])
        global_func = "".join([" "*4 + f"global {var}\n" for var in func_list])

        global_variables = global_widgets_var + '\n' + global_var + '\n' + global_func

        # All the new lines of code are ensambled
        code_cell = "# Run this cell to visualize the parameters and click the button to execute the code\n"
        if not ipywidget_imported:
            # In case the ipywidgets library have not been imported yet
            code_cell += ("import ipywidgets as widgets\n" 
                          "from IPython.display import display, clear_output\n")       
            ipywidget_imported = True

        code_cell += ("clear_output()\n\n" # In orther to renew the ipywidgets
                    ) + widget_code + ( # Add the code with the widgets at the begining of the cell
                    f"\ndef {function_name}(output_widget):\n" # The function that will be called whwn clicking the button
                    "  output_widget.clear_output()\n" # Clear the output that was displayed when calling the function
                    "  with output_widget:\n" # In order to display the output
                    ) + global_variables + '\n' + tabbed_non_widget_code + ( # Add the global variables and the non widget code
                    "    plt.show()\n" # Add plt.show() in case there is any plot in tab_non_widget_code, so that it can be displayed
                    "button = widgets.Button(description='Load and run')\n" # Add the button that calls the function
                    "output = widgets.Output()\n"
                    "display(button, output)\n\n"
                    f"def aux_{function_name}(_):\n" 
                    f"  return {function_name}(output)\n\n"
                    f"button.on_click(aux_{function_name})\n"
                    )
    else:
        # Otherwise, just add the code
        code_cell = "# Run this cell to execute the code\n" +  non_widget_code

    #Create the code cell
    aux_cell = nbformat.v4.new_code_cell(clear_excesive_empty_lines(code_cell))
    # Hides the content in the code cells
    aux_cell.metadata["cellView"] = "form"
    aux_cell.metadata["collapsed"] = True
    aux_cell.metadata["jupyter"] = {"source_hidden": True}
            
    new_cells.append(aux_cell)
    
    return new_cells, ipywidget_imported
