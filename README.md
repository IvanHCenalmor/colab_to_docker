A simple library to transform a Google Colab notebook to a 'colabless' version which is able to be run as local jupyter notebook.

# Requirements
Its based in two python libraries: **re** and **nbformat**. As **re** already comes installed with Python as a base library, the only installation that is required is:

'''
pip install nbformat
'''

The versions of the libraries that have been used is:
 - nbformat==5.9.1
 - re==2.2.1

The Python version has been **3.10.11**.

* Other versions may also work, but these have been the ones used during the developement of this library.

# How to use?
As the pip installation is not available yet, you need to clone the repository or download the code to be able to run it:

'''
git clone https://github.com/IvanHCenalmor/colab_to_docker.git
'''

Then, once you have the code the main funcion you need to call is:

'''
python colab_to_docker/src/transform.py -p PATH -n NOTEBOOK_NAME -s SECTIONS_TO_REMOVE
'''

where PATH is the path where the notebook can be found, NOTEBOOK_NAME is the name of the notebook that you want to transform and SECTIONS_TO_REMOVE is a list with the sections that you want to remove from the notebook. This is an example usage:

'''
python colab_to_docker/src/transform.py -p . -n MyNotebook.ipynb -s 1.1. 1.2. 2. 6.3.
'''