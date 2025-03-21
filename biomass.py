import pandas as pd
import math, sys, os
import argparse
import numpy as np
import json
import biomass_io as b_io
from calculations import biomass, axB, basal_area
import copy
import re

equation_dict = None
final_dict = {}

def process_sites(full_df):
    global final_dict
    group_sites_plots = full_df.groupby('SITE').apply(lambda x: x['PLOT'].unique())
    group_tree_plots = full_df.groupby('SITE').apply(lambda x: x[x['LIFE_FORM'] == 'tree']['PLOT'].unique())
    group_shrub_plots = full_df.groupby('SITE').apply(lambda x: x[x['LIFE_FORM'] == 'shrub']['PLOT'].unique())
    for site in group_sites_plots.index:
        if site == "fake" or site == "notasite" or site == "_none":
            continue
        print(f"processing site: {site}")
        final_dict.setdefault(site, {})
        final_dict[site]["_Number Plots Shrubs_"] = len(group_shrub_plots[site])
        final_dict[site]["_Number Plots Trees_"] = len(group_tree_plots[site])
        process_site(full_df.loc[(full_df['SITE'] == site)], site, group_sites_plots[site])

def process_site(plot_pd, site, plot_array):
    global final_dict
    for plot in plot_array:
        individual_plot_pd = plot_pd.loc[(plot_pd['PLOT'] == plot)]
        process_plot(individual_plot_pd, site, plot)

    tree_pd = plot_pd[plot_pd['LIFE_FORM'] == 'tree']
    process_trees_in_site(tree_pd, site)
    shrub_pd = plot_pd[plot_pd['LIFE_FORM'] == 'shrub']
    process_shrubs_in_site(shrub_pd, site)
    final_adjustments(site)

def final_adjustments(site):
    temp_dict = copy.deepcopy(final_dict)
    for key in temp_dict[site].keys():
        if 'Weighted' in key and not 'Area' in key:
            weighted_sum = final_dict[site][key]
            total_area = final_dict[site].get(re.sub(r' \$.*?\$', '', key)+" Area", 0)
            biomass = weighted_sum / total_area if total_area > 0 else 0
            key = key.replace('$','')
            final_dict[site][key.replace('Weighted ', '')] = biomass
            final_dict[site].setdefault(key.replace('Weighted ', '').replace('Shrub ', '').replace('Tree ', ''), 0)
            final_dict[site][key.replace('Weighted ', '').replace('Shrub ', '').replace('Tree ', '')] += biomass
            final_dict[site].setdefault(key.replace('Weighted ', '').replace('Shrub ', '').replace('Tree ', '').replace('Live ','').replace('Dead ',''), 0)
            final_dict[site][key.replace('Weighted ', '').replace('Shrub ', '').replace('Tree ', '').replace('Live ','').replace('Dead ','')] += biomass


def process_trees_in_site(tree_pd, site):
    final_dict[site]['_Tree Count Total_'] = len(tree_pd)
    final_dict[site]['_Tree Count Live_'] = len(tree_pd[tree_pd['STATUS'] == 'living'])
    final_dict[site]['_Tree Count Dead_'] = len(tree_pd[tree_pd['STATUS'] == 'dead'])
    final_dict[site]['_Avg Tree Diameter (cm)_'] = tree_pd["DIAMETER"].mean()
    final_dict[site]['_Avg Tree Height (m)_'] = tree_pd["HEIGHT"].mean()
    final_dict[site]['_Avg Canopy Depth (m)_'] = (tree_pd["HEIGHT"] - tree_pd['HEIGHT_TO_LOWEST_BRANCH']).mean()
    final_dict[site]['_Tree Density all Plots (trees/m^2)_'] = final_dict[site]['_Tree Count Total_'] / final_dict[site][f"_Tree Total Plot Area (m^2)_"]

    for tree_species in tree_pd['SPECIES'].unique():
        final_dict[site][f'_Tree Distribution_ {tree_species}'] = len(tree_pd[tree_pd['SPECIES'] == tree_species]) / final_dict[site]['_Tree Count Total_']
        final_dict[site][f'_Tree Species Average Diameter_ {tree_species} (cm)'] = tree_pd[tree_pd['SPECIES'] == tree_species]["DIAMETER"].mean()
        final_dict[site][f'_Tree Species Average Height_ {tree_species} (m)'] = tree_pd[tree_pd['SPECIES'] == tree_species]["HEIGHT"].mean()

def process_shrubs_in_site(shrub_pd, site):
    final_dict[site]['_Shrub Count Total_'] = len(shrub_pd)
    final_dict[site]['_Shrub Count Live_'] = len(shrub_pd[shrub_pd['STATUS'] == 'living'])
    final_dict[site]['_Shrub Count Dead_'] = len(shrub_pd[shrub_pd['STATUS'] == 'dead'])
    final_dict[site]['_Shrub Density (stems/m^2)_'] = len(shrub_pd) / final_dict[site][f"_Shrub Total Plot Area (m^2)_"]
    final_dict[site]['_Average Shrub Diameter (cm)_'] = shrub_pd["DIAMETER"].mean()
    final_dict[site]['_Average Shrub Height (m)_'] = shrub_pd["HEIGHT"].mean()

    for shrub_species in shrub_pd['SPECIES'].unique():
        final_dict[site][f'_Shrub Distribution_ {shrub_species}' ]= len(shrub_pd[shrub_pd['SPECIES'] == shrub_species]) / final_dict[site]['_Shrub Count Total_']
        final_dict[site][f'_Shrub Species Average Diameter_ {shrub_species}'] = shrub_pd[shrub_pd['SPECIES'] == shrub_species]["DIAMETER"].mean()


def process_plot(plot_pd, site, plot_id):
    global final_dict
    process_trees_in_plot(plot_pd.loc[plot_pd['LIFE_FORM']=='tree'], site, plot_id)
    process_shrubs_in_plot(plot_pd.loc[plot_pd['LIFE_FORM'] == 'shrub'], site, plot_id)
    # plot level variables
def flatten_series(series):
    return pd.Series(series)

def add_biomass(site, plant_type, status, plot_id, df, area):
    df = df.apply(flatten_series)

    df.drop(columns=[0], inplace=True, errors='ignore')
    # if site == "mb525" and plant_type.lower() == "shrub" and status.lower() == "live":  # and plot_id == "3c":
    #     print(df)
    final_dict[site].setdefault(f"_Total {plant_type} Biomass {status} Weighted (kg/m^2)_ Area", 0)
    final_dict[site][f"_Total {plant_type} Biomass {status} Weighted (kg/m^2)_ Area"] += area
    if df.empty:
        return
    for species in df['SPECIES'].unique():
        if species == 0 or pd.isnull(species):
            continue
        final_dict[site][f"_{plant_type} Species Biomass {status} AB_ {species} (kg/m^2) Plot {plot_id}"] = df[df['SPECIES'] == species]['AB'].sum() / area

    for biomass in df.columns.tolist():
        biomass = biomass.upper()
        if biomass.lower() == "species":
            continue
        biomass_sum = df[biomass].sum() if not df.empty else 0
        final_dict[site][f"_{plant_type} Biomass {status} plot_ {biomass} (kg/m^2) {plot_id}"] = biomass_sum/area
        if biomass == 'AB' or biomass == 'ST' or biomass == 'BR' or biomass == 'FL':
            final_dict[site].setdefault(f"_Total {plant_type} Biomass {status} Weighted ${biomass}$ (kg/m^2)_", 0)
            #final_dict[site].setdefault(f"_Total Biomass {status}Weighted {biomass} (kg/m^2)_", 0)
            #final_dict[site].setdefault(f"_Total BiomassWeighted {biomass} (kg/m^2)_", 0)

            #final_dict[site].setdefault(f"_Total Biomass {status}Weighted {biomass} (kg/m^2)_ Area", 0)
            #final_dict[site].setdefault(f"_Total BiomassWeighted {biomass} (kg/m^2)_ Area", 0)

            final_dict[site][f"_Total {plant_type} Biomass {status} Weighted ${biomass}$ (kg/m^2)_"] += biomass_sum
            #final_dict[site][f"_Total Biomass {status}Weighted {biomass} (kg/m^2)_"] += biomass_sum
            #final_dict[site][f"_Total BiomassWeighted {biomass} (kg/m^2)_"] += biomass_sum


            #final_dict[site][f"_Total {plant_type} Biomass {status} Weighted (kg/m^2)_ Area"] += area
            #final_dict[site][f"_Total Biomass {status}Weighted {biomass} (kg/m^2)_ Area"] += area
            #final_dict[site][f"_Total BiomassWeighted {biomass} (kg/m^2)_ Area"] += area

def process_trees_in_plot(tree_pd, site, plot_id):
    global final_dict
    final_dict[site][f"_Tree Plot Area (m^2)_ {plot_id}"] = tree_pd.PLOT_SIZE.loc[~tree_pd.PLOT_SIZE.isnull()].iloc[0]
    area = np.prod(np.array(final_dict[site][f"_Tree Plot Area (m^2)_ {plot_id}"].split('x'), dtype=np.uint8))

    final_dict[site][f"_Tree Total Plot Area (m^2)_"] = final_dict[site].get(f"_Tree Total Plot Area (m^2)_", 0) + area

    final_dict[site][f"_Basal Area Plot (m^2/ha)_ {plot_id}"] = tree_pd.apply(basal_area, args=(area,), axis=1).sum() if not tree_pd.empty else 0

    live_tree_df = living_trees.apply(biomass, args=(equation_dict,), axis=1, result_type='expand') if not (living_trees := tree_pd[tree_pd["STATUS"]=='living']).empty else pd.DataFrame()
    dead_tree_df = dead_trees.apply(biomass, args=(equation_dict,), axis=1, result_type='expand') if not (dead_trees := tree_pd[tree_pd["STATUS"] == 'dead']).empty else pd.DataFrame()
    add_biomass(site, "Tree", "Live", plot_id, live_tree_df, area)
    add_biomass(site, "Tree", "Dead", plot_id, dead_tree_df, area)

def process_shrubs_in_plot(shrub_pd, site, plot_id):
    global final_dict
    final_dict[site][f"_Shrub Plot Area (m^2)_ {plot_id}"] = shrub_pd.PLOT_SIZE.loc[~shrub_pd.PLOT_SIZE.isnull()].iloc[0] if not shrub_pd['PLOT_SIZE'].isnull().all() else final_dict[site][f"_Tree Plot Area (m^2)_ {plot_id}"]
    area = np.prod(np.array(final_dict[site][f"_Shrub Plot Area (m^2)_ {plot_id}"].split('x'), dtype=np.uint8))
    final_dict[site][f"_Shrub Total Plot Area (m^2)_"] = final_dict[site].get(f"_Shrub Total Plot Area (m^2)_", 0) + area

    if area > 0:
        live_shrub_df = living_shrubs.apply(biomass, args=(equation_dict,), axis=1, result_type='expand') if not (living_shrubs := shrub_pd[shrub_pd['STATUS'] == 'living']).empty else pd.DataFrame()
        dead_shrub_df = dead_shrubs.apply(biomass, args=(equation_dict,), axis=1, result_type='expand') if not (dead_shrubs := shrub_pd[shrub_pd['STATUS'] == 'dead']).empty else pd.DataFrame()
        add_biomass(site, "Shrub", "Live", plot_id, live_shrub_df, area)
        add_biomass(site, "Shrub", "Dead", plot_id, dead_shrub_df, area)

if __name__ == "__main__":
    config = b_io.parse_config()
    print(f'Running Biomass on: {config["site_xlsx"]}')
    equation_dict = b_io.read_excel(config["equation_xlsx"],"Species_Name")
    process_sites(b_io.read_excel(config["site_xlsx"]))
    b_io.format_output(final_dict, b_io.read_excel(config["output_format"], transpose=True))