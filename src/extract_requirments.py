
import nbformat
import re
from yarg import json2package
from yarg.exceptions import HTTPError
import requests
import logging

python310_base_packages = ['appnope', 'asttokens', 'backcall', 'colorama', 'decorator', 'diskcache', 'executing', 
                           'ipython', 'jedi', 'jsonpickle', 'matplotlib-inline', 'nvidia-ml-py', 'packaging', 
                           'parso', 'pexpect', 'pickleshare', 'prompt-toolkit', 'psutil', 'ptyprocess', 'pure-eval', 
                           'Pygments', 'pyvis', 'stack-data', 'termcolor', 'traitlets', 'wcwidth']

def requiremts_from_code(code):

    import_pattern = r'^\s*(import|from)\s+(\w+)'
    imports = re.findall(import_pattern, code, re.MULTILINE)
    imports = [library[-1] for library in imports if library]

    installation_pattern =  r'pip\s+install\s+(-[^\s]+\s+)?["\']?([^<>=\s]+)'
    installations = re.findall(installation_pattern, code, re.MULTILINE)
    installations = [library[-1] for library in installations if library]

    return imports + installations

def fix_requiremts(requiremts):
    fixed_requirements = []
    for r in requiremts:
        if r not in python310_base_packages:
            if r == 'sklearn':
                fixed_requirements.append('scikit-learn')
            elif r == 'skimage':
                fixed_requirements.append('scikit-image')
            elif r == 'PIL':
                fixed_requirements.append('Pillow')
            elif '_' in r:
                fixed_requirements.append(r.replace('_', ''))
            else:
                fixed_requirements.append(r)

    return fixed_requirements

def extract_requirements(path_nb):
    colab_nb = nbformat.read(path_nb, as_version=4)

    requiremts = []
    for cell in colab_nb.cells:
        if cell.cell_type == "code":
            code = cell.source
            cell_requirements = requiremts_from_code(code)
            requiremts += cell_requirements
        elif cell.cell_type == "markdown":
            pass
    
    requiremts = list(set(requiremts))
    requiremts = fix_requiremts(requiremts)
    
    return requiremts
    
def compare_with_freeze(path_nb, requirement_list=[]):

    requirements = requirement_list if requirement_list else extract_requirements(path_nb)

    try: from pip._internal.operations import freeze
    except ImportError: # pip < 10.0
        from pip.operations import freeze

    requirements_with_version = []

    pkgs = freeze.freeze()
    for pkg in pkgs: 
        if '@' in pkg:
            # Means that the library is in a local file
            # library = pkg.split('@')[0]
            continue
        elif '==' in pkg:
            library = pkg.split('==')[0]
            version = pkg.split('==')[1]
        else:
            print(pkg)
            raise Exception("Wrong library name.")
        
        if library in requirements:
            try:
                response = requests.get(
                    "{0}{1}/json".format("https://pypi.python.org/pypi/", library), proxies=None)
                if response.status_code == 200:
                    if hasattr(response.content, 'decode'):
                        data = json2package(response.content.decode())
                    else:
                        data = json2package(response.content)
                elif response.status_code >= 300:
                    raise HTTPError(status_code=response.status_code,
                                    reason=response.reason)
            except HTTPError:
                logging.warning(
                    'Package "%s" does not exist or network problems', item)
                continue

            if version in data._releases.keys() and library!="ipywidgets":  
                actual_version = version
            else:
                actual_version = data.latest_release_id

            requirements_with_version.append(f'{library}=={actual_version}')
    return requirements_with_version


if __name__ == "__main__":

    import os
    import argparse
 
    parser = argparse.ArgumentParser(description="Convert colab notebook to docker notebook",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-p", "--path", help="path of the notebook")
    parser.add_argument("-n", "--name", help="name of the notebook")
    parser.add_argument("-s", "--save", help="path and name to save the requirements.txt")
    args = vars(parser.parse_args())
    
    path_requiremts =  os.path.join(args["save"])
    nb_path = os.path.join(args["path"], args["name"])

    requiremts = compare_with_freeze(nb_path)

    file=open(path_requiremts,'w')
    file.writelines(f'# Requirements for {args["name"]}\n')
    for item in sorted(requiremts):
        file.writelines(item + '\n')
    file.close()
