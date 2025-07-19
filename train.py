# train.py
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, accuracy_score
from xgboost import XGBClassifier
import json
import os
import base64  # moved to top

def main():
    # Load and clean data
    df = sns.load_dataset("penguins").dropna()

    # One-hot encode categorical variables
    df = pd.get_dummies(df, columns=["sex", "island"], drop_first=False)

    # Encode target
    le = LabelEncoder()
    df["species"] = le.fit_transform(df["species"])
    label_mapping = {str(k): int(v) for k, v in zip(le.classes_, le.transform(le.classes_))}


    # Features and labels
    X = df.drop("species", axis=1)
    y = df["species"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # Train model
    model = XGBClassifier(max_depth=3, n_estimators=100, use_label_encoder=False, eval_metric="logloss")
    model.fit(X_train, y_train)

    # Evaluate
    for name, X_, y_ in [("Train", X_train, y_train), ("Test", X_test, y_test)]:
        y_pred = model.predict(X_)
        print(f"{name} Accuracy: {accuracy_score(y_, y_pred):.2f}, F1 Score: {f1_score(y_, y_pred, average='weighted'):.2f}")

    # Save model as base64 string
    model_binary = model.get_booster().save_raw()
    model_base64 = base64.b64encode(model_binary).decode("utf-8")

    # Save model and encoding info
    model_output = {
        "model": model_base64,
        "columns": list(X.columns),
        "label_mapping": label_mapping
    }

    os.makedirs("app/data", exist_ok=True)
    with open("app/data/model.json", "w") as f:
        json.dump(model_output, f)

if __name__ == "__main__":
    main()
