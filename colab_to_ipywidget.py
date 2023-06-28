
import re

float_regex = r"[-+]?\d*\.\d+|[-+]?\d+"
ipywidget_style = "{'description_width': 'initial'}"

def params_to_widgets(code: str) -> str:
    """
    This function converts colab's form params into interactive widgets. It takes a string as input and returns a string.
    @param code: a string containing the function parameters.
    @return: a string that contains the generated widgets for each parameter that can be used to make the function interactive.
    """
    param_regex = r"(\w+)\s*=\s*([\S\s]+?)\s*#@param\s*(.+)"
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
            result = f'{var_name} = widgets.Combobox(options={possible_values}, placeholder={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
        else:
            if ',' in possible_values:
                list_possible_values = [item.strip() for item in possible_values.strip('[]').split(',')]
            else:
                list_possible_values =  [item.strip() for item in possible_values.strip('[]')]
            default_value = default_value if default_value in list_possible_values else list_possible_values[0]
            result = f'{var_name} = widgets.Dropdown(options={possible_values}, value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
    elif param_type is not None:
        if param_type == "slider":
            min, max, step = re.findall(f"\s*min:({float_regex}),\s*max:({float_regex}),\s*step:({float_regex})", post_param)[0]
            try:
                min, max, step = int(min), int(max), int(step)
                result = f'{var_name} = widgets.IntSlider(value={default_value}, min={min}, max={max}, step={step}, style={ipywidget_style}, description="{var_name}:")\n'
            except:
                min, max, step = float(min), float(max), float(step)
                result = f'{var_name} = widgets.FloatSlider(value={default_value}, min={min}, max={max}, step={step}, style={ipywidget_style}, description="{var_name}:")\n'
        if param_type == "integer":
            result = f'{var_name} = widgets.IntText(value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
        elif param_type == "number":
            result = f'{var_name} = widgets.FloatText(value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
        elif param_type == "boolean":
            result = f'{var_name} = widgets.Checkbox(value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
        elif param_type == "string" or param_type == "raw":
            result = f'{var_name} = widgets.Text(value={default_value}, style={ipywidget_style}, description="{var_name}:")\n'
        elif param_type == "date":
            result = ('from datetime import datetime\n'
                      f'{var_name} = widgets.DatePicker(value=datetime.strptime({default_value}, "%Y-%m-%d"),style={ipywidget_style}, description="{var_name}:")\n'
                      )
    else:
        # Even if it has #@param, it does not follow colab param format
        return code, ''
            
    # In case it has colab param format 
    result += f'display({var_name})'
    return result, var_name

def extract_values_from_variables(variable_list):
    resutl = ""
    for var in variable_list:
        resutl += f"{var} = {var}.value\n"
    return resutl