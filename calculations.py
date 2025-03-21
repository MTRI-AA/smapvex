import math, sys, os
import numpy as np
import pandas as pd

def axB(a, x, b, cf=1.0, eqn = ""):
    if a == "" or b == "" or eqn == "":
        return 0
    if not isinstance(cf, (int, float)):
        cf = 1.0
    eqn = eqn.lower().replace("_", "")
    if eqn == "biomass=a*(dia^b)*c":  # Most species use this standard equation
        return (a * x ** b) * cf
    elif eqn == "biomass=(e^(a+b*ln(dia)))/1000" or eqn == "biomass=e^(a+b*ln(dia))/1000":
        return math.exp(a + b * (math.log(x))) / 1000
    elif eqn == "biomass=(e^(a+c*(ln(dia^b))))/1000":
        return math.exp(a + cf * (math.log(x ** b))) / 1000
    elif eqn == "biomass=e^(a+b*(ln(dia^c))/1000":
        return math.exp(a + b * (math.log(x ** cf))) / 1000
    elif eqn == "biomass=10^(a+b*(log10(dia)))*c":
        return 10**(a + b * (math.log10(x))) * cf
    elif eqn == "biomass=10^(a+b*(log10(dia))*c)":
        return 10**(a + b * math.log10(x) * cf)
    elif eqn == "biomass=(a+b*(dia/2.54)+c*((dia/2.54)^2))*0.4536":
        return (a + b * (x / 2.54) + cf * ((x / 2.54)**2)) * 0.4536
    elif eqn == "biomass=10^(a+b*(log10((dia/2.54)^c)))/1000" or eqn == "biomass=(10^(a+b*(log10((dia/2.54)^c))))/1000":
        return (10**(a + b * (math.log10((cf/2.54)**cf)))) / 1000
    elif eqn == "biomass=a*((dia/2.54)^b)*c*0.4536":
        return a * ((x / 2.54) ** b) * cf * 0.4536
    elif eqn == "biomass=(a+b*(dia/2.54)+c*((dia/2.54)^2))*0.4356":
        return (a + b * (x/2.54) + cf * ((x/2.54)**2)) * 0.4356
    elif eqn == "biomass=(10^(a+b*log10(dia*10))/1000":
        return (10**(a + b * math.log10(x*10))) / 1000
    elif eqn == "biomass=(e^(a+c*(ln((dia/2.54)^b))))/1000":
        return (math.exp(a + cf * (math.log((x / 2.54) ** b)))) / 1000
    elif eqn == "biomass=a*(((dia/2.54)^2)^b)*c*0.4536":
        return a * ((x / 2.54) ** 2) ** b * cf * 0.4536
    else:
        if "biomass" in eqn:
            print(f"Equation: {eqn} is unknown")
        else:
            return 0



def basal_area(row, area):
    if row['SPECIES'] != "picea mariana":
        diameter = 0.5 * row['DIAMETER']
    else:
        diameter = 0.5 * (0.8422 * row['DIAMETER'] - 0.2459)
    return axB(3.14159, diameter, 2, eqn="biomass=a*(dia^b)*c") / area

def strip_spaces_and_handle_nan(lst):
    if pd.notna(lst):
        return [word.replace("_", " ").strip().replace(" ","_") for word in lst.split(",")]
    else:
        return ['']

def biomass(row, equation_dict):
    equation_dict_copy = equation_dict.copy()
    equation_dict_copy['SCIENTIFIC_NAME'] = equation_dict_copy['SCIENTIFIC_NAME'].apply(strip_spaces_and_handle_nan)
    equation_dict_copy['SCIENTIFIC_NAME'] = equation_dict_copy['SCIENTIFIC_NAME'].apply(lambda lst: [word.strip() for word in lst])
    equation_dict_copy['SPECIES_NAME'] = equation_dict_copy['SPECIES_NAME'].apply(strip_spaces_and_handle_nan)
    equation_dict_copy['SPECIES_NAME'] = equation_dict_copy['SPECIES_NAME'].apply(lambda lst: [word.strip() for word in lst])
    equation_dict_copy['OTHER_NAMES'] = equation_dict_copy['OTHER_NAMES'].apply(strip_spaces_and_handle_nan)
    equation_dict_copy['OTHER_NAMES'] = equation_dict_copy['OTHER_NAMES'].apply(lambda lst: [word.strip() for word in lst])
    species = row["SPECIES"].replace(" ", "_")
    matching_rows = equation_dict_copy[['SCIENTIFIC_NAME', 'SPECIES_NAME', 'OTHER_NAMES']].apply(
        lambda row: any(species in col for col in row), axis=1
    )
    equation = equation_dict_copy[matching_rows]
    if equation.empty:
        print(f'No Equation for {row["SPECIES"]}')
        return 0
    else:
        equation = equation.iloc[0]
        for key, value in equation.items():
            if isinstance(value, float) and np.isnan(value):
                equation[key] = ""

        AB = axB(equation['AB_A'], row['DIAMETER'], equation['AB_B'], cf=equation['AB_C'], eqn=equation["EQUATION_AB"])
        FL = axB(equation['FL_A'], row['DIAMETER'], equation['FL_B'], cf=equation['FL_C'], eqn=equation["EQUATION_FL"])
        ST = axB(equation['ST_A'], row['DIAMETER'], equation['ST_B'], cf=equation['ST_C'], eqn=equation["EQUATION_ST"])
        SW = axB(equation['SW_A'], row['DIAMETER'], equation['SW_B'], cf=equation['SW_C'], eqn=equation["EQUATION_SW"])
        SB = axB(equation['SB_A'], row['DIAMETER'], equation['SB_B'], cf=equation['SB_C'], eqn=equation["EQUATION_SB"])
        ST_BR = axB(equation['ST_BR_A'], row['DIAMETER'],equation['ST_BR_B'], cf=equation['ST_BR_C'], eqn=equation["EQUATION_ST_BR"])
        BR = axB(equation['BR_A'], row['DIAMETER'], equation['BR_B'],cf=equation['BR_C'], eqn=equation["EQUATION_BR"])

        if equation["EQUATION_ST"].lower() == "sw+sb":
            ST = SW + SB

        if equation["EQUATION_AB"].lower() == "fl+st+br":
            AB = FL + BR + ST

        if equation["EQUATION_BR"].lower() == "st_br-st":
            BR = ST_BR - ST


        #BR2 = axB(equation['BR2_A'], row['DIAMETER'], equation['BR2_B'], cf=equation['BR2_C'], eqn=equation["EQUATION_BR"])
        return pd.Series([AB, FL, ST, SW, SB, ST_BR, BR, species], index=["AB", "FL", "ST", "SW", "SB", "ST_BR", "BR", "SPECIES"])