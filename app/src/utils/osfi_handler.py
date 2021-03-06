import pandas as pd


class OsfiHandler:
    def __init__(self):
        self.data = pd.read_csv("/data/cleaned/data_osfi.csv")

    def get_structure_data(self, code_structure, year=None):
        if year:
            return self.data.loc[(self.data.id == code_structure) & (self.data["Année"] == year), :]
        else:
            return self.data.loc[(self.data.id == code_structure)]


oh = OsfiHandler()
