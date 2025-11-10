# compare_submissions.py
import pandas as pd

s1 = pd.read_csv("submission.csv").rename(columns={"price":"price_v1"})
s2 = pd.read_csv("submission_v2.csv").rename(columns={"price":"price_v2"})
s3 = pd.read_csv("submission_v3.csv").rename(columns={"price":"price_v3"})

df = s1.merge(s2, on="sample_id").merge(s3, on="sample_id")

summary = pd.DataFrame({
    "mean_v1": [df.price_v1.mean()], "mean_v2": [df.price_v2.mean()], "mean_v3": [df.price_v3.mean()],
    "median_v1": [df.price_v1.median()], "median_v2": [df.price_v2.median()], "median_v3": [df.price_v3.median()],
    "std_v1": [df.price_v1.std()], "std_v2": [df.price_v2.std()], "std_v3": [df.price_v3.std()],
})
print("==== distribution summary ====")
print(summary.round(4).to_string(index=False))

# pairwise deltas
df["d_v2_v1"] = df.price_v2 - df.price_v1
df["d_v3_v2"] = df.price_v3 - df.price_v2
df["d_v3_v1"] = df.price_v3 - df.price_v1

print("\n==== avg absolute deltas ====")
print(pd.Series({
    "avg|v2-v1|": df.d_v2_v1.abs().mean(),
    "avg|v3-v2|": df.d_v3_v2.abs().mean(),
    "avg|v3-v1|": df.d_v3_v1.abs().mean(),
}).round(4))

# top movers (sanity checking)
tops = df.assign(abs_move=df.d_v3_v2.abs()).sort_values("abs_move", ascending=False).head(25)
tops[["sample_id","price_v1","price_v2","price_v3","d_v3_v2","d_v3_v1"]].to_csv("sub_top_movers.csv", index=False)
print("\nWrote top movers -> sub_top_movers.csv")
