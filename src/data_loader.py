import pandas as pd
from typing import  Optional

def load_excel(path: str) ->pd.DataFrame:
    """ Load the excel file to dataframe
        does not modify the original columns    """
    df = pd.read_excel(path= "cleaned_flight_scheduling", engine="openpyxl",dtype=object)
    return df