import numpy as np
import pandas as pd


def main():
    df = pd.read_csv("data/dirty_cafe_sales.csv", dtype=str, keep_default_na=False)
    c_df = clean(df)
    c_df.to_csv("data/clean_cafe_sales.csv", index=False)
    print(f"Start: {len(df)} --> After: {len(c_df)}")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    

    clean_df = df.copy()
    clean_df = clean_df.replace(["ERROR", "UNKNOWN", " ", "", None, "error", "unknown"], np.nan)


    # columns

    clean_df.columns = clean_df.columns.str.strip().str.replace(" ", "_").str.lower()

    # format
    
    num_columns = ["quantity", "price_per_unit", "total_spent"]

    for columns in num_columns:
        clean_df[columns] = pd.to_numeric(clean_df[columns], errors="coerce")

    # transaction

    clean_df = clean_df[clean_df["transaction_id"].astype(str).str.startswith("TXN_", na=False)]
    clean_df = clean_df.drop_duplicates(subset=["transaction_id"])
    clean_df = clean_df.reset_index(drop=True)
    

    # price per unit

    clean_df["price_per_unit"] = clean_df["price_per_unit"].fillna(clean_df["total_spent"] / clean_df["quantity"])
    


    # total spent
    
    clean_df["total_spent"] = clean_df["total_spent"].fillna(clean_df["quantity"] * clean_df["price_per_unit"])
    

    # quantity
    
    clean_df["quantity"] = clean_df["quantity"].fillna(clean_df["total_spent"] / clean_df["price_per_unit"])

    
    # item

    clean_df["item"] = clean_df["item"].str.title().str.strip()

    p_to_items = (clean_df.dropna(subset=["item", "price_per_unit"]).groupby("price_per_unit")["item"].unique())
    
    unique_p_map = {}

    for price, items in p_to_items.items():
        if len(items) == 1:
            unique_p_map[price] = items[0]

    clean_df["item"] = clean_df["item"].fillna(clean_df["price_per_unit"].map(unique_p_map))
    clean_df["item"] = clean_df["item"].fillna("Unknown")


    # drop useless data
    
    clean_df = clean_df.dropna(subset=["quantity", "price_per_unit", "total_spent"]).reset_index(drop=True)
 

    # payment method

    clean_df["payment_method"] = clean_df["payment_method"].str.title().str.strip()
    clean_df["payment_method"] = clean_df["payment_method"].fillna("Unknown")
    

    # location
    
    clean_df["location"] = clean_df["location"].str.title().str.strip()
    clean_df["location"] = clean_df["location"].fillna("Unknown")

    # transaction_date

    clean_df["transaction_date"] = pd.to_datetime(clean_df["transaction_date"], errors="coerce")


    return clean_df



if __name__ == "__main__":
    main()