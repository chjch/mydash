import pandas as pd
import json


DATA_URL = r"./data/building/ov_bldg.geojson"

geojson_data = json.load(open(DATA_URL))

df = pd.json_normalize(geojson_data['features'])
df = df[[clm for clm in df.columns if clm.startswith('properties')]]
df.rename(
    columns=dict(zip(
        df.columns,
        [_[len('properties.'):] for _ in df.columns]
    )),
    inplace=True
)

print(df)

# print(df.columns.values)
# #
# # df = pd.read_json(DATA_URL, orient='split')
# # print(df)