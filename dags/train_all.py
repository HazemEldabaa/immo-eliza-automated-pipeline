import joblib
import pandas as pd
import xgboost as xgb
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from version_utils import read_counter


def train(input):

    data_version = read_counter("/opt/airflow/src/counter_data.txt")
    data = pd.read_csv(f"/opt/airflow/src/final_cleaned_v{data_version}.csv")
    # Define features to use
    num_features = [
        "nbr_frontages",
        "nbr_bedrooms",
        "latitude",
        "longitude",
        "total_area_sqm",
        "surface_land_sqm",
        "terrace_sqm",
        "garden_sqm",
        "nb_epc",
        "construction_year",
    ]
    fl_features = ["fl_terrace", "fl_garden", "fl_swimming_pool"]
    cat_features = [
        "province",
        "heating_type",
        "locality",
        "subproperty_type",
        "region",
        "state_building",
        "property_type",
    ]

    # Split the data into features and target
    X = data[num_features + fl_features + cat_features]
    y = data["price"]

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=69
    )

    # Impute missing values using SimpleImputer
    imputer = SimpleImputer(strategy="mean")
    # imputer.fit(X_train[num_features])
    X_train[num_features] = imputer.fit_transform(X_train[num_features])
    X_test[num_features] = imputer.transform(X_test[num_features])

    # Convert categorical columns with one-hot encoding using OneHotEncoder
    # enc = OneHotEncoder()
    # enc.fit(X_train[cat_features])
    # X_train_cat = enc.transform(X_train[cat_features]).toarray()
    # X_test_cat = enc.transform(X_test[cat_features]).toarray()
    ordinal_encoder = OrdinalEncoder(
        handle_unknown="use_encoded_value", unknown_value=-1
    )

    # Fit the OrdinalEncoder on the categorical features of the training data
    X_train_encoded = X_train.copy()
    X_train_encoded[cat_features] = ordinal_encoder.fit_transform(X_train[cat_features])
    # Transform the categorical features of the test data using the same encoder
    X_test_encoded = X_test.copy()
    X_test_encoded[cat_features] = ordinal_encoder.transform(X_test[cat_features])

    print(f"Features: \n {X_train.columns.tolist()}")

    # apply best parameters

    best_params = {
        "subsample": 0.8,
        "n_estimators": 150,
        "max_depth": 7,
        "learning_rate": 0.1,
        "lambda": 1,
        "gamma": 5,
        "colsample_bytree": 0.6,
        "alpha": 0,
    }

    # Train the model with the best parameters

    model = xgb.XGBRegressor(objective="reg:squarederror", **best_params)

    model.fit(X_train_encoded, y_train)

    train_score = r2_score(y_train, model.predict(X_train_encoded))
    test_score = r2_score(y_test, model.predict(X_test_encoded))
    print(f"Train R² score: {train_score}")
    print(f"Test R² score: {test_score}")

    # Save the model
    artifacts = {
        "features": {
            "num_features": num_features,
            "fl_features": fl_features,
            "cat_features": cat_features,
        },
        "imputer": imputer,
        "enc": ordinal_encoder,
        "model": model,
    }
    joblib.dump(artifacts, f"/opt/airflow/myrepo/src/artifacts_airflow_v{input}.joblib")
    print(f"Model saved as artifacts_airflow_v{input}.joblib")
