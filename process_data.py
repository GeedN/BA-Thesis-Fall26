# process_data.py
# This code implements data cleaning + score calculation
#
# Coding done by Nisa Geed, debugging done with ChatGPT assistance
# Modules used available in standard python installations

import pandas as pd
import numpy as np

filename = "10-Nov-26_19-14.csv"
df = pd.read_csv(r"D:\User\Documents\1_CSAI\Thesis\Data_Exploration\Data\clean_field_data_" + filename)
timefilter = True #set to false to keep all responses
#dict for clean strings to shorten values to an easier standard
cleanStrings = {
    "high school diploma": "hsd",
    "bachelor's degree": "bac",
    "master's degree": "mas",
    "associate's degree": "asd",
    "doctorate": "doc",
    "female": "f",
    "male": "m",
    "non-binary / other": "o",
    "prefer not to say": "p",
    "india" :"in",
    "netherlands" :"nl",}

# lowercase everything + empty strings become NA + string answers are cleaned
for col in df.select_dtypes(include=["object", "string"]).columns:
    df[col] = df[col].apply(
        lambda x: pd.NA if isinstance(x, str) and x.strip() == ""
        else cleanStrings.get(x.lower().strip(), x.lower().strip()) if isinstance(x, str)
        else x
    )

#   filter out responses over 3 MADs from the average time:

# Calculate median and Median Absolute Deviation
time_median = df["total_time"].median()

mad = np.median(
    np.abs(df["total_time"].dropna() - time_median)
)

# Calculate upper cutoff (robust 3-SD equivalent)
upper_limit = time_median + 3 * 1.4826 * mad

# Identify excluded responses
excluded = df[df["total_time"] > upper_limit].copy()

# Filter dataset
df = df[df["total_time"] <= upper_limit].copy()

# Report
print(f"Median completion time: {time_median:.2f}")
print(f"MAD: {mad:.2f}")
print(f"Upper cutoff: {upper_limit:.2f}")
print(f"Excluded: {len(excluded)}")
print(f"Remaining: {len(df)}, dutch: {(df["country"]=="nl").sum()}, indian: {(df["country"]=="in").sum()}")
print(df["country"].value_counts())
print(df["ng_submit_timing"].count())
print(df["fb_submit_timing"].count())

# Filter dataset
if timefilter == True:
    df = df[df["total_time"] <= upper_limit].copy()

# score types: (all scores are summed then divided by max possible score)
# panas - positive and negative affect schedule, positive affect (PA) and negative affect (NA). 
#   "panas_pre_na" 
#   "panas_pre_pa" 
#   "panas_post_na"
#   "panas_post_pa"
# tpshri - trust perception scale HRI - 0-100 so reverse coding = 100 - response
#   "tpshri_pre" -> with reverse-coded items "tpshri_pre_reverse"
#   "tpshri_post" -> with reverse-coded items "tpshri_post_reverse"
# ses - state empathy scale, subscores affective, cognitive, and associative empathy
#   "ses_aff" 
#   "ses_cog"
#   "ses_ass"
#   "ses_"

scoresList = [
    "panas_pre_na",
    "panas_pre_pa" ,
    "panas_post_na",
    "panas_post_pa",
    "tpshri_pre",
    "tpshri_post",
    "ses_aff" ,
    "ses_cog",
    "ses_ass",
    "ses" ]

maxVals = {
    "panas" : 5,
    "tpshri" : 100,
    "ses" : 5 }

def calculate_score(subCols, maxVal, reverseCols=None):
    subCols = subCols.copy()

    #note: panas and ses don't have reverse coded items 
    # but this code would need to minus the minimum value from the column so the base is 0
    # in case of future studies using scales that do not already start with 0
    # you could also add minVal as an argument and calculate maxVal+minVal-reverseCols
    if reverseCols is not None and not reverseCols.empty:
        subCols[reverseCols.columns] = maxVal - reverseCols

    maxScore = subCols.shape[1]*maxVal
    score = subCols.sum(axis=1) / maxScore
    return score

for item in scoresList:
    targetCol = item + "_score"
    subCols = df.loc[:, df.columns.str.startswith(item)]
    reverseCols = subCols.loc[:, subCols.columns.str.contains("_reverse")]
    subCols = subCols.loc[:, ~subCols.columns.str.contains("_reverse")]
    maxVal = maxVals[item.split("_")[0]]
    
    df[targetCol] = calculate_score(subCols, maxVal, reverseCols)

df["panas_na_diff"] = df["panas_post_na_score"] - df["panas_pre_na_score"]
df["panas_pa_diff"] = df["panas_post_pa_score"] - df["panas_pre_pa_score"]
df["tpshri_diff"] = df["tpshri_post_score"] - df["tpshri_pre_score"]

# add a condition column which sorts responses into 
# "ng" for no gestures and "fb" for full body gestures
# and collapses their timing column into one for simplicity in later analysis
ng_present = (df["ng_submit_timing"].notna())
fb_present = (df["fb_submit_timing"].notna())

df["condition"] = np.select([ng_present, fb_present],["ng", "fb"],default=np.nan)

df["submit_timing"] = (df["ng_submit_timing"].combine_first(df["fb_submit_timing"]))

df = df.drop(columns=["ng_submit_timing", "fb_submit_timing"])
if timefilter:
    df.to_csv(r"D:\User\Documents\1_CSAI\Thesis\Data_Exploration\Data\cleaned_filtered_scored_data_"+ filename, index=False)
else:
    df.to_csv(r"D:\User\Documents\1_CSAI\Thesis\Data_Exploration\Data\cleaned_scored_data_"+ filename, index=False)