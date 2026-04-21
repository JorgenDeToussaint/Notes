import polars as pl

data = pl.read_csv(source = r"C:\Users\ae_ea\Desktop\p1_przeksztalcanie_danych.csv", has_header = True, encoding = "UTF-8")

df = pl.DataFrame(data)

print(df.head())

df = df.with_columns(
     pl.col("Opis transakcji")
    .str.extract(r":\s*([\d\s]+)", 1)
    .str.replace_all(r"\s+", "")
    .alias("Numer konta")
)

print(df.head())
