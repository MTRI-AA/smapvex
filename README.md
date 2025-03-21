# SMAPVEX22
MTRI's Smapvex Code to calculate Biomass

## Table of contents
1. [Installation](#lininstall)
2. [Inputs](#inputs)
	1. [Equation XLSX](#eqxlsx)
	2. [Site_XLSX](#sxlsx)
	3. [Format_XLSX](#fxlsx)
3. [Running](#run)
3. [Output](#out)

## Linux Installation <a name="lininstall"></a>
Clone the repository to a location of your choosing:

    git@vm-gitlab.mtri.org:biomass/smapvex.git

And create the virtual environment:

    python3 -m venv ~/SMAP --system-site-packages
    source ~/SMAP/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r /location/of/SMAP/requirements.txt

## Inputs <a name="inputs"></a>
### Equation XLSX <a name="eqxlsx"></a>
Holds Trees/Small_Trees/Shrubs equations to calculate biomass

changing the equation path 
    
    in ./config/default.config
    {
        "equation_path" : "path/to/equations.xlsx"
    }
### Site XLSX <a name="sxlsx"></a>
Tree and shrub data recorded at sites

Changing the site path 
    
    in ./config/default.config
    {
        "equation_path" : "path/to/site.xlsx"
    }
### Format Output XLSX <a name="fxlsx"></a>
An Excel file that defines excel files, sheets, and the respective data to be outputted 

changing the excel that formats the output  

    in ./config/default.config
    {
        "equation_path" : ""path/to/format/output.xlsx""
    }

## Running Biomass Script<a name="run"></a>
The following script will run through the Site data, processing through the trees and shrubs calculating relevant data

    python ./biomass.py --config ./config/default.config
    
## Output<a name="out"></a>
The Biomass code will output the calculations

Locations to output the data

    File - The xlsx filename to output the data too
    sheet - The sheet name to output the data too
    
Columns of Data that can be outputted

    Site
    Number Plots Shrubs
    Number Plots Trees
    Tree Plot Area (m^2)
    Tree Total Plot Area (m^2)
    Tree Count Total
    Tree Count Live
    Tree Count Dead
    Tree Density all Plots (trees/m^2)
    Avg Tree Diameter (cm)
    Avg Tree Height (m)
    Avg Canopy Depth (m)
    Tree Distribution
    Tree Species Average Diameter
    Basal Area Plot (m^2/ha)
    Tree Biomass Live plot
    Tree Biomass Dead plot
    Total Tree Biomass Live AB (kg/m^2)
    Total Tree Biomass Dead AB (kg/m^2)
    Total Tree Biomass Live ST (kg/m^2)
    Total Tree Biomass Dead ST (kg/m^2)
    Total Tree Biomass Live BR (kg/m^2)
    Total Tree Biomass Dead BR (kg/m^2)
    Total Tree Biomass Live FL (kg/m^2)
    Total Tree Biomass Dead FL (kg/m^2)
    Tree Species Average Height
    Tree Species Biomass Live AB
    Tree Species Biomass Dead AB
    Shrub Plot Area (m^2)
    Shrub Total Plot Area (m^2)
    Shrub Count Total
    Shrub Count Live
    Shrub Count Dead
    Shrub Density (stems/m^2)
    Average Shrub Diameter (cm)
    Average Shrub Height (m)
    Shrub Distribution
    Shrub Species Average Diameter
    Shrub Biomass Live plot
    Shrub Biomass Dead plot
    Total Shrub Biomass Live AB (kg/m^2)
    Total Shrub Biomass Dead AB (kg/m^2)
    Total Shrub Biomass Live ST (kg/m^2)
    Total Shrub Biomass Dead ST (kg/m^2)
    Total Shrub Biomass Live BR (kg/m^2)
    Total Shrub Biomass Dead BR (kg/m^2)
    Total Shrub Biomass Live FL (kg/m^2)
    Total Shrub Biomass Dead FL (kg/m^2)
    Shrub Species Biomass Live AB
    Shrub Species Biomass Dead AB
    Total Biomass Live AB (kg/m^2)
    Total Biomass Dead AB (kg/m^2)
    Total Biomass Live ST (kg/m^2)
    Total Biomass Dead ST (kg/m^2)
    Total Biomass Live BR (kg/m^2)
    Total Biomass Dead BR (kg/m^2)
    Total Biomass Live FL (kg/m^2)
    Total Biomass Dead FL (kg/m^2)
    Total Biomass AB (kg/m^2)
    Total Biomass ST (kg/m^2)
    Total Biomass BR (kg/m^2)
    Total Biomass FL (kg/m^2)

