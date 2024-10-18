import streamlit as st
import pandas as pd
import json
from sqlalchemy import create_engine

# Title of the app
st.title("Yelp Database Creation")

# Inform the user about the database setup process
st.write("This application will load Yelp dataset JSON files into a SQLite database.")

# File uploader for JSON files
uploaded_business_file = st.file_uploader("Upload business dataset JSON", type="json")
uploaded_checkin_file = st.file_uploader("Upload check-in dataset JSON", type="json")
uploaded_review_file = st.file_uploader("Upload review dataset JSON", type="json")
uploaded_tip_file = st.file_uploader("Upload tip dataset JSON", type="json")
uploaded_user_file = st.file_uploader("Upload user dataset JSON", type="json")

# Define a function to load the data from JSON to a DataFrame
def load_json_to_dataframe(file):
    data = [json.loads(line) for line in file]
    return pd.DataFrame(data)

# Create SQLite connection
engine = create_engine('sqlite:///yelp.db')

# Define a function to load a DataFrame into a table in the SQLite database
def load_dataframe_to_db(df, table_name):
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    st.write(f"Loaded {df.shape[0]} records into the '{table_name}' table.")

# Load each dataset when files are uploaded
if uploaded_business_file:
    st.write("Loading business data...")
    business_df = load_json_to_dataframe(uploaded_business_file)
    # Drop unnecessary columns (attributes, hours, etc.)
    business_df.drop(['attributes', 'hours'], axis=1, inplace=True)
    load_dataframe_to_db(business_df, 'business')

if uploaded_checkin_file:
    st.write("Loading check-in data...")
    checkin_df = load_json_to_dataframe(uploaded_checkin_file)
    load_dataframe_to_db(checkin_df, 'checkin')

if uploaded_review_file:
    st.write("Loading review data...")
    review_df = load_json_to_dataframe(uploaded_review_file)
    load_dataframe_to_db(review_df, 'review')

if uploaded_tip_file:
    st.write("Loading tip data...")
    tip_df = load_json_to_dataframe(uploaded_tip_file)
    load_dataframe_to_db(tip_df, 'tip')

if uploaded_user_file:
    st.write("Loading user data...")
    user_df = load_json_to_dataframe(uploaded_user_file)
    load_dataframe_to_db(user_df, 'user')

st.write("Database setup complete!")