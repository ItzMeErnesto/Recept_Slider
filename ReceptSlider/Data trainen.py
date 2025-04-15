# Stap 1: Model trainen en opslaan als .pkl

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

# Laad je Excel-bestand (pas pad aan indien nodig)
data_path = "samengevoegde_resultaten_met_eigen_data.xlsx"  # pas dit aan naar je pad
sheet_name = "Sheet1"

# Kolommen die we gebruiken (je kunt dit uitbreiden)
columns = [
    'LV-Dex (%)', 'HV-Dex (%)', 'Borax (%)', 'Krijt Slurry (%)', 'MBL (%)',
    'LA1209 (%)', 'Water (%)', 'Struktol (%)', 'Loog (%)', 'Suiker (%)',
    'Viscosity Brookfield', 'pH [-]', 'DS'
]

df = pd.read_excel(data_path, sheet_name=sheet_name, usecols=columns)
df = df.dropna()  # eventueel, om incomplete rijen te verwijderen

# Features en targets
X = df.drop(columns=['Viscosity Brookfield', 'pH [-]', 'DS'])
y = df[['Viscosity Brookfield', 'pH [-]', 'DS']]

# Split en train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# Sla model op
joblib.dump(model, "model_rf.pkl")
print("✅ Model getraind en opgeslagen als model_rf.pkl")
