
# Installation

## Requirements

- Python 2.7 plus a few Python libraries:
	- matplotlib
	- numpy
	- pandas
	- xlwr
	- xlrd
	- openpyxl

## Windows

1. [Download](http://conda.pydata.org/miniconda.html) and install miniconda for Python 2.7 
	- Make sure the directory of the conda binary and that of the python interpreter that comes with conda are added to the PATH. The installer will let you do that.
2. Open a command-line window (`cmd`) and install the necessary libraries by typing the following command:

		conda install matplotlib pandas xlrd xlwt openpyxl
	

## Mac OS X

1. Install MacPorts
2. Install the python interpreter (v2.7) that comes with MacPorts and set this interpreter as the default one. Don't forget to install the required python packages as well.

		## Install python + additional packages
		$ sudo port install py27-matplotlib py27-numpy py27-pandas py27-xlrd py27-xlwt py27-openpyxl
		
		## Select MacPorts Python27 interpreter by default
		$ sudo port select --set python python27
		$ sudo port select --set ipython ipython27
		
		
		
		
# Usage

	$ ./delta_s.py 
	Usage: ./delta_s <data_file> <nfield_values> <mass> [output_file]
	
* `data_file`: Input file in CSV or Excel format (.xls or .xlsx)
	- The file must contain a table with three columns: Temp(K), Magnetic Field (in Oe), and Magnetization
	- The rows must be sorted in ascending order by temperature and magnetic field
* `nfield_values`: Number of different values explored for the magnetic field
* `mass`: mass of the experimental sample used
*  `output_file`: (optional field) Path of the file where to dump the results. It can be a CSV or an Excel file. If no output file is given, a default name for the output will be used, by appending the "out" suffix to the name of the input file. So for example, if the name of the input file is "example.xls", the output data will be stored by default in "example_out.xls".


## Example		

	$ ./delta_s.py example.xls 15 0.05 results.xls
