import pandas as pd

class ExcelDataFetcher:
    def __init__(self, file_path, sheet_name):
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.data = None

    def fetch_data(self):
        self.data = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
        return self.data
    


