import pandas as pd
import numpy as np
from version_utils import read_counter

province_to_region = {
    "West Flanders": "Flanders",
    "East Flanders": "Flanders",
    "Antwerp": "Flanders",
    "Brussels": "Brussels",
    "Walloon Brabant": "Wallonia",
    "Limburg": "Flanders",
    "Liege": "Wallonia",
    "Luxembourg": "Wallonia",
    "Namur": "Wallonia",
    "Hainaut": "Wallonia",
    "Flemish Brabant": "Flanders",
}
energy_class_bxl = {
    "A++": (-20, 0),
    "A+": (0, 15),
    "A": (16, 30),
    "A-": (31, 45),
    "B+": (46, 62),
    "B": (63, 78),
    "B-": (79, 95),
    "C+": (96, 113),
    "C": (114, 132),
    "C-": (133, 150),
    "D+": (151, 170),
    "D": (171, 190),
    "D-": (191, 210),
    "E+": (211, 232),
    "E": (233, 253),
    "E-": (254, 275),
    "F": (276, 345),
    "G": (346, 800),
}
energy_class_fld = {
    "A+": (-20, 0),
    "A": (0, 100),
    "B": (100, 200),
    "C": (200, 300),
    "D": (300, 400),
    "E": (400, 500),
    "F": (500, 900),
}
energy_class_wal = {
    "A++": (-20, 0),
    "A+": (0, 45),
    "A": (45, 85),
    "B": (85, 170),
    "C": (170, 255),
    "D": (255, 340),
    "E": (340, 425),
    "F": (425, 510),
    "G": (510, 900),
}


def extract_epc(value):
    if isinstance(value, str) and "_" in value:
        parts = value.split("_")
        return parts[-1]
    else:
        return value


def clean_data(input):
    def print_shape(func):
        def wrapper(*args, **kwargs):
            print(f"Before: {args[0].shape}")
            func(*args, **kwargs)
            print(f"After: {args[0].shape}")

        return wrapper

    @print_shape
    def drop_duplicates(df):
        return df.drop_duplicates(inplace=True)

    df = pd.read_csv(input)
    # drop unnecessary columns
    df.drop(columns=["Unnamed: 0", "link"], inplace=True)
    df["epc"] = df["epc"].apply(extract_epc)
    df["epc"].value_counts().to_frame()
    # remove duplicates
    drop_duplicates(
        df
    )  # helper function with decorator around df.drop_duplicates(inplace=True)
    df["region"] = df["province"].map(province_to_region)
    # remove properties with no known property_type
    df = df[df["property_type"].notna()]

    # remove properties with no known price or a too low price
    df = df[(df["price"] > 75000) & (df["price"].notna())]

    # rename a couple of columns
    df.rename(
        columns={
            "floodZoneType": "fl_floodzone",
            "primaryEnergyConsumptionPerSqm": "primary_energy_consumption_sqm",
            "total_area_m2": "total_area_sqm",
            "furnished": "fl_furnished",
            "open_fire": "fl_open_fire",
            "terrace": "fl_terrace",
            "garden": "fl_garden",
            "surface_land": "surface_land_sqm",
            "swimming_pool": "fl_swimming_pool",
            "Double_Glazing": "fl_double_glazing",
            "Number_of_frontages": "nbr_frontages",
            "bedroom_count": "nbr_bedrooms",
        },
        inplace=True,
    )

    # set all columns to lower case
    df.columns = df.columns.str.lower()

    # replace nan with "MISSING" for object columns
    for col in df.select_dtypes(include="object").columns:
        df[col].fillna("MISSING", inplace=True)

    # replace 0 with nan for cadastral_income
    df["cadastral_income"] = np.where(
        df["cadastral_income"] == 0, np.nan, df["cadastral_income"]
    )

    # replace impossible construction year values with nan
    df["construction_year"] = np.where(
        (df["construction_year"] < 1750) | (df["construction_year"] > 2024),
        np.nan,
        df["construction_year"],
    )

    def random_value_for_energy_class(row):
        primary_energy_column = row.get("primary_energy_consumption_sqm")
        epc_column = row.get("epc")
        region = row.get("region")

        if pd.isna(primary_energy_column) and epc_column == "MISSING":
            return np.nan
        elif pd.notna(primary_energy_column):
            return primary_energy_column
        elif region == "Brussels-Capital":
            lower_bound, upper_bound = energy_class_bxl.get(epc_column, (0, 0))
            return np.random.uniform(lower_bound, upper_bound)
        elif row["region"] == "Wallonia":
            lower_bound, upper_bound = energy_class_wal.get(row["epc"], (0, 0))
            return np.random.uniform(lower_bound, upper_bound)
        elif row["region"] == "Flanders":
            lower_bound, upper_bound = energy_class_fld.get(row["epc"], (0, 0))
            return np.random.uniform(lower_bound, upper_bound)
        else:
            return np.nan

    df["nb_epc"] = df.apply(random_value_for_energy_class, axis=1)

    # reorder columns
    cols = [
        "id",
        "price",
        "property_type",
        "subproperty_type",
        "region",
        "province",
        "locality",
        "zip_code",
        "latitude",
        "longitude",
        "construction_year",
        "total_area_sqm",
        "surface_land_sqm",
        "nbr_frontages",
        "nbr_bedrooms",
        "nb_epc",
        "equipped_kitchen",
        "fl_furnished",
        "fl_open_fire",
        "fl_terrace",
        "terrace_sqm",
        "fl_garden",
        "garden_sqm",
        "fl_swimming_pool",
        "fl_floodzone",
        "state_building",
        "primary_energy_consumption_sqm",
        "epc",
        "heating_type",
        "fl_double_glazing",
        "cadastral_income",
    ]
    df = df[cols]
    version_number = read_counter("/opt/airflow/src/counter_data.txt")
    # save cleaned data
    df.to_csv(f"/opt/airflow/src/final_cleaned_v{version_number}.csv", index=False)
