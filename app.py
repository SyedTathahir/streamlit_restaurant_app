import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import folium
from datetime import datetime
from geopy.geocoders import Nominatim
from matplotlib.colors import LinearSegmentedColormap
from streamlit_folium import folium_static

# Title of the app
st.title("Yelp Restaurant Success Analysis")

# Problem Statement and Research Objectives
st.header("Problem Statement")
st.write("In a competitive market like the restaurant industry, understanding the factors that influence business success is crucial. This project investigates the relationship between user engagement (reviews, tips, check-ins) and business success metrics (review count, ratings) for restaurants.")

st.header("Research Objectives")
st.write("""
1. Quantify the correlation between user engagement (reviews, tips, check-ins) and review count/average star rating.
2. Analyze the impact of sentiment on review count and average star rating.
3. Explore time trends in user engagement for long-term success.
""")

# Database connection setup
conn = sqlite3.connect('yelp.db')
st.header("Database Information")
st.write("The dataset is a subset of Yelp with information about businesses across 8 metropolitan areas in the USA and Canada.")
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
st.write("Available Tables:", tables)

# Load and display business data
st.subheader("Business Data Sample")
business_data = pd.read_sql_query("SELECT * FROM business LIMIT 5", conn)
st.dataframe(business_data)

# Display top restaurants by review count
st.subheader("Top 10 Restaurants by Review Count")
top_restaurants = pd.read_sql_query("""
    SELECT name, SUM(review_count) as review_count, AVG(stars) AS avg_rating
    FROM business
    GROUP BY name
    ORDER BY review_count DESC
    LIMIT 10;
""", conn)
st.dataframe(top_restaurants)

# Visualization of review, tip, and check-in engagement by rating
st.subheader("Average Engagement by Restaurant Rating")
review_count_df = pd.read_sql_query("""
    SELECT total.avg_rating as rating,
           AVG(total.review_count) as avg_review_count,
           AVG(total.checkin_count) as avg_checkin_count,
           AVG(total.tip_count) as avg_tip_count
    FROM (SELECT b.business_id, SUM(b.review_count) AS review_count,
                 AVG(b.stars) AS avg_rating,
                 SUM(LENGTH(cc.date) - LENGTH(REPLACE(cc.date, ',', '')) + 1) AS checkin_count,
                 SUM(tip.tip_count) as tip_count
          FROM business b
          LEFT JOIN checkin cc ON b.business_id = cc.business_id
          LEFT JOIN (select business_id, count(business_id) as tip_count from tip 
                     GROUP BY business_id ORDER BY tip_count) as tip 
                     on b.business_id = tip.business_id
          GROUP BY b.business_id) as total
    GROUP BY total.avg_rating;
""", conn)

colors = ['#FFF1E5', "#F8862C", "#CB754B"]
custom_cmap = LinearSegmentedColormap.from_list("mycmap", colors)
sns.heatmap(review_count_df.corr(), cmap=custom_cmap, annot=True, linewidths=0.5, linecolor='black')
plt.title('AVG Engagement based on Rating\n')
st.pyplot(plt)

# Map visualization using Folium
st.subheader("Top Cities by Success Score")
city_df = pd.read_sql_query("""
    SELECT state, city, latitude, longitude, AVG(stars) AS avg_rating,
           SUM(review_count) as review_count, COUNT(*) as restaurant_count
    FROM business
    GROUP BY state, city
    ORDER BY review_count DESC
    LIMIT 10;
""", conn)

# Function to calculate success score
def calculate_success_metric(df):
    success_score = []
    for index, row in df.iterrows():
        score = row['avg_rating'] * np.log(row['review_count'] + 1)
        success_score.append(score)
    return success_score

city_df['success_score'] = calculate_success_metric(city_df)
m = folium.Map(location=[city_df['latitude'].mean(), city_df['longitude'].mean()], zoom_start=4)

color_scale = folium.LinearColormap(colors=['green', 'yellow', '#E54F29'], vmin=city_df['success_score'].min(), vmax=city_df['success_score'].max())

for index, row in city_df.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color=color_scale(row['success_score']),
        fill=True,
        fill_color=color_scale(row['success_score']),
        fill_opacity=0.7,
        popup=f"Success Score: {row['success_score']}"
    ).add_to(m)

folium_static(m)

# Final Recommendations Section
st.header("Recommendations")
st.write("""
- **Boost User Engagement:** Restaurants should focus on enhancing engagement metrics (reviews, check-ins, tips) to drive overall success.
- **Leverage Elite Users:** Establish relationships with Yelp elite users to increase visibility and credibility.
- **Optimize for Peak Hours:** Based on user engagement data, restaurants should allocate resources efficiently during busy hours (4 PM - 1 AM).
- **Capitalize on Top Cities:** Areas with higher success scores, such as Philadelphia and Tampa, present expansion opportunities.
""")
