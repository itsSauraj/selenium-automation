import pandas as pd

class ExcelHandler:
    @staticmethod
    def read_headers(filepath: str):
        df = pd.read_excel(filepath, nrows=1)
        return list(df.columns)
