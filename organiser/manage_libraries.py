import pandas as pd
import os


class LibrariesManager:

    sample_sheet_to_panel = {
        "SeqCapH": "HyperCap",
        "EG": "EliGene",
        "TSO500": "TruSight"
        }

    def __init__(self, libraries_path, sample_sheet_path, path_to_run, predictive_number):
        all_files = [os.path.join(libraries_path, file) for file in os.listdir(libraries_path)
                     if not os.path.isdir(file) and file.endswith(".csv")]
        latest_file = max(all_files, key=os.path.getmtime)
        self.libraries_path = latest_file
        self.sample_sheet_path = sample_sheet_path
        self.predictive_number = predictive_number
        self.parameters_path = os.path.join(path_to_run, "Samples", predictive_number,
                                            "Analysis", f"{predictive_number}_Parameters.txt")

    def get_data_from_libraries(self):
        df = pd.read_csv(self.libraries_path, delimiter=";", encoding="CP1250")
        df.dropna(inplace=True, subset=["Panel"])
        df.replace(to_replace="NEPRAVDA", value=False, inplace=True)
        df.replace(to_replace="PRAVDA", value=True, inplace=True)
        df["Panel"] = df["Panel"].str.lower()
        df["Text in parameters"] = df["Text in parameters"].str.lower()

        possible_params = df["Text in parameters"].tolist()
        library_name_in_parameter_file = self._look_for_lib_in_parameters(possible_params)
        if library_name_in_parameter_file is None:
            samplesheet_df = pd.read_csv(self.sample_sheet_path, delimiter=",",
                                         names=["[Header]", "Unnamed: 1", "Unnamed: 2", "Unnamed: 3", "Unnamed: 4",
                                                "Unnamed: 5", "Unnamed: 6", "Unnamed: 7", "Unnamed: 8", "Unnamed: 9"])
            experiment = samplesheet_df[samplesheet_df["[Header]"] == "Experiment Name"]["Unnamed: 1"].values[0]
            experiment_name, experiment_date = experiment.split("_")

            reference_date = self._fix_reference_date(experiment_date)

            if experiment_name in self.sample_sheet_to_panel.keys():
                experiment_name = self.sample_sheet_to_panel[experiment_name]

            possible_names = [row["Panel"].lower() for _, row in df.iterrows()
                              if experiment_name.lower() in row["Panel"] and
                              self._date_in_date_range(row["Availability Date Range"], reference_date)]
            if len(possible_names) == 1:
                return self._create_dict_with_library_info(df, possible_names[0])
            elif len(possible_names) > 1:
                return self._create_dict_with_library_info(df, experiment_name.lower(), look_for_manual=True)
            else:
                return None
        else:
            return self._create_dict_with_library_info(df, [],
                                                       panel_name_from_parameter_file=library_name_in_parameter_file)

    def _look_for_lib_in_parameters(self, possible_parameters):
        with open(self.parameters_path, "r") as f:
            text = f.readlines()
        for parameter in possible_parameters:
            if parameter in text[-1].lower():
                return parameter
        return None
        
    def _fix_reference_date(self, date):
        year, month, day = date[:2], date[2:4], date[4:]
        return f"20{year}-{month}-{day}"

    def _date_in_date_range(self, dates, reference_date):
        if isinstance(dates, str) and "-" in dates:
            start, end = dates.split("-")
            start = pd.to_datetime(start, dayfirst=True)
            end = pd.to_datetime(end, dayfirst=True)
            return pd.to_datetime(reference_date) in pd.date_range(start, end)
        else:
            return False

    def _create_dict_with_library_info(self, dataframe, panel_value, look_for_manual=False,
                                       panel_name_from_parameter_file=None):
        if panel_name_from_parameter_file:
            for _, row in dataframe.iterrows():
                if row["Text in parameters"] in panel_name_from_parameter_file.lower():
                    return {
                                    "input_amount": row["Input Amount"],
                                    "library_prep_kit": row["code in the molgenis catalogue"],
                                    "pca_free": row["PCR Free"],
                                    "target_enrichment_kid": row["Target Enrichment Kit"],
                                    "umi_present": row["UMIs Present"],
                                    "intended_insert_size": int(row["Intended Insert Size"]),
                                    "intended_read_length": int(row["Intended Read Length"]),
                                    "genes": row["Genes (*all coding regions covered)"]
                                }
        else:
            for _, row in dataframe.iterrows():
                if look_for_manual and panel_value in row["Panel"] and row["Text in parameters"] == "manual":
                    return {
                                "input_amount": row["Input Amount"],
                                "library_prep_kit": row["code in the molgenis catalogue"],
                                "pca_free": row["PCR Free"],
                                "target_enrichment_kid": row["Target Enrichment Kit"],
                                "umi_present": row["UMIs Present"],
                                "intended_insert_size": int(row["Intended Insert Size"]),
                                "intended_read_length": int(row["Intended Read Length"]),
                                "genes": row["Genes (*all coding regions covered)"]
                            }
                if not look_for_manual and panel_value in row["Panel"]:
                    return {
                                "input_amount": row["Input Amount"],
                                "library_prep_kit": row["code in the molgenis catalogue"],
                                "pca_free": row["PCR Free"],
                                "target_enrichment_kid": row["Target Enrichment Kit"],
                                "umi_present": row["UMIs Present"],
                                "intended_insert_size": int(row["Intended Insert Size"]),
                                "intended_read_length": int(row["Intended Read Length"]),
                                "genes": row["Genes (*all coding regions covered)"]
                            }
            return None
