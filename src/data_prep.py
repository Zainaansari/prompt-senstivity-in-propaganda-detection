import pandas as pd

columns = ["article_id", "technique", "start", "end"]
df = pd.read_csv(
    "./data/raw/datasets-v2/datasets/train-task2-TC.labels",
    sep="\t",
    header=None,
    names=columns,
)

unique_ids = df["article_id"].unique()

text_spans = []


for article_id in unique_ids:

    spans = df.loc[df["article_id"] == article_id, ["start", "end"]]


    with open(
        f"./data/raw/datasets-v2/datasets/train-articles/article{article_id}.txt", "r",encoding="utf-8"
    ) as article:

        text = article.read()

        for index, start, end in spans.itertuples(name=None):

            text_span = text[start:end]

            text_spans.append(text_span)

if(len(text_spans) == len(df)):
    df["text_spans"] = text_spans
            

print(df.head())

df.to_csv("./data/processed/processed_data.csv", index=False)


