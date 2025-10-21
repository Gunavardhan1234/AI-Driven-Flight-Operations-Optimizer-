#here are the codes 
#which process the raw data and converts to understandable data 

import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder,StandardScaler

file_path = "cleaned_flight_scheduling.xlsx"
data_6_9 = pd.read_excel(file_path,sheet_name='6AM - 9AM')