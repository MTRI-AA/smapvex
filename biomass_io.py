import sys, os, json
import pandas as pd
import argparse
def read_excel(excel_file_path, index_name = None, transpose = False):
    """
        Read data from an Excel or CSV file and convert it into a nested dictionary.

        Parameters:
        excel_file_path (str): The path to the Excel or CSV file to be read.
        index_name (str): The name of the column that will serve as the keys for each row in the resulting dictionary.
    """
    if '.xlsx' in excel_file_path:
        output = pd.read_excel(excel_file_path, engine='openpyxl')
    elif '.xls' in excel_file_path:
        output = pd.read_excel(excel_file_path)
    elif '.csv' in excel_file_path:
        output = pd.read_csv(excel_file_path)
    else:
        sys.exit("Error: Equation input is not one of the supported types .'xlsx' , '.xls' or a '.csv' file")

    if transpose:
        output.reset_index(drop=True, inplace=True)
        output = output.T
        output.columns = output.iloc[0]
        output = output[1:]
        output.reset_index(drop=True, inplace=True)
    output.columns = output.columns.str.rstrip()
    output = output.applymap(lambda x: x.rstrip().lower().replace(" ", "_") if isinstance(x, str) else x)
    output.columns = output.columns.str.rstrip().str.upper().str.replace(" ", "_")

    # if not index_name is None:
    #     output = output.set_index(index_name).to_dict('index')
    return output

def output_excel(dfs, save_path, sheets = ["Sheet1"]):
    writer = pd.ExcelWriter(save_path, engine='openpyxl')
    for df, sheet in zip(dfs, sheets):
        if '.xlsx' in save_path:
            df.columns = df.columns.str.replace('_','')
            df.to_excel(writer, header=True, index_label="site", sheet_name=sheet)
        else:
            print(f"Invalid save path : {save_path}\nOutput file must be .xlsx")
        # elif '.csv' in save_path:
        #     df.to_csv(save_path, header=True, index_label="site")
    writer.close()

def format_output(final_dict, format_excel):
    full_df = pd.DataFrame.from_dict(data=final_dict, orient='index')
    full_column_list = list(full_df.head())
    print(format_excel)
    group_output_files = format_excel.groupby('FILE').apply(lambda x: x['SHEET'].unique())
    print(format_excel)
    for file, sheets in group_output_files.items():
        sheet_dfs = []
        for sheet in sheets:
            desired_column_list = format_excel.loc[(format_excel['FILE'] == file) & (format_excel['SHEET'] == sheet)].apply(lambda row: row[row == 'x'].index.tolist(), axis=1).iloc[0]
            out_column_indexes = []
            for name in desired_column_list:
                matching_columns = [s for s in full_column_list if f"_{name.replace('_', ' ').lower()}_" in s.lower()]
                matching_columns_sorted = sorted(matching_columns)
                columns_indices = [full_column_list.index(s) for s in matching_columns_sorted]
                out_column_indexes.extend(columns_indices)
            sheet_dfs.append(full_df.iloc[:,out_column_indexes])
        output_excel(sheet_dfs, file, sheets)

def excel_path(path):
    if os.path.isfile(path) and (".csv" in path) or (".xls" in path) or (".xlsx" in path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"FILE:{path} is not a valid excel file")

def config_path(path):
    if os.path.isfile(path) and (".config" in path) or (".json" in path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"FILE:{path} is not a valid config file")

def parse_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--equation', type=excel_path)
    parser.add_argument('--site', type=excel_path)
    parser.add_argument('--output', type=excel_path)
    parser.add_argument('--config', type=config_path)
    args = parser.parse_args()

    default_config = {
        "equation_xlsx": "./Equations/Species_data_dictionary_9Final_ajc_adjusttreeequations_inpinkandround2orangeR3.xlsx",
        # "site_xlsx": "Sites/TreeInventory_dataentry_LBCcheckMB_forpythoncode_FINAL_r1.xlsx",
        "site_xlsx": "Sites/TreeInventory_dataentry_LBCcheckMA_FINALforpythoncode_sort_nowhitebirch_5Jan24.xlsx",
        "output_format": "Output_Formats/format_output_T.xlsx"
    }
    # replace default with args config
    if args.config:
        with open(args.config, 'r') as config_file:
            new_config = json.load(config_file)
            default_config["equation_xlsx"] = new_config.pop("equation_xlsx", default_config["equation_xlsx"])
            default_config["site_xlsx"] = new_config.pop("site_xlsx", default_config["site_xlsx"])
            default_config["output_format"] = new_config.pop("output_format", default_config["output_format"])
        config_file.close()

    # replace default with args
    if args.equation:
        default_config["equation_xlsx"] = args.equation
    if args.site:
        default_config["site_xlsx"] = args.input
    if args.output:
        default_config["output_format"] = args.output

    return default_config