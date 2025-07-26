import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

# Dashboard page
st.set_page_config(page_title="Airbnb Analysis",layout="wide")
st.title("🏠 Airbnb Analysis Dashboard")
options = ["","United States", "Turkey", "Canada", "Spain", "Australia", "Brazil", "Hong Kong", "Portugal", "China"]
selected_option = st.selectbox("Select Country:", options)
col1, col2 = st.columns(2)  
col3, col4, col5 = st.columns(3)

# Data Function to retrieve dataframe from MongoDB Collection
def data():
    mycluster = MongoClient("mongodb+srv://deepakparashar1:pTtdcktq2bwPe8cY@cluster0.qbrup3w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    mydb = mycluster["sample_airbnb"]
    mycol = mydb["listingsAndReviews"]

    listingsAndReviews = []
    for x in mycol.find():
        listingsAndReviews.append(x)
    df= pd.DataFrame(listingsAndReviews)
    df['price'] = df['price'].astype(str).astype(float).astype(int)

    country = []
    latitude = []
    longitude = []
    review_scores = []
    for i in range(len(df)):
        try:
            country.append(df['address'][i]['country'])
            latitude.append(df['address'][i]['location']['coordinates'][1])
            longitude.append(df['address'][i]['location']['coordinates'][0])
            review_scores.append(df['review_scores'][i]['review_scores_rating'])
        except:
            review_scores.append(0)
    df['country']= country
    df['latitude']= latitude
    df['longitude']= longitude
    df['review_scores']= review_scores
    df= df[['name','country','latitude','longitude','price','room_type','last_review','number_of_reviews']]
    return df

# Create Map based on user seection
def create_map():
    df = data()
    df = df[df['country']==selected_option][['name','country','latitude','longitude','price']]
    top_by_price = df.sort_values(by='price',ascending=False).head(5)
    latitude_maxprice = top_by_price.loc[top_by_price['price'].idxmax(), 'latitude']
    longitude_maxprice = top_by_price.loc[top_by_price['price'].idxmax(), 'longitude']
    m = folium.Map(location=[latitude_maxprice, longitude_maxprice], tiles="OpenStreetMap", zoom_start=6)
    for _, row in top_by_price.iterrows():
        location=[row['latitude'], row['longitude']]
        popup = f"${row['price']}"
        tooltip_html = f"""
        <b>Name:</b> {row['name']}<br>
        <b>Price:</b> ${row['price']}<br>
        """
        folium.CircleMarker(
            location=location,
            radius=5,               # Size of the circle in pixels
            color='blue',            # Border color
            fill=True,
            fill_color='red',        # Fill color
            fill_opacity=0.6,
            popup=popup,
            tooltip=tooltip_html
            ).add_to(m)
    return m

# Function to display charts on dashboard
def main():
    with col1:
        st.markdown("<p style='font-size:14px; margin-bottom:0px; text-align:center;'>Top 5 listings by price</p>", unsafe_allow_html=True)
        map = create_map()
        st_folium(map, use_container_width=False, width=800, height=350,returned_objects=[])

    with col2:
        df = data()
        df = df[df['country']==selected_option][['name','country','price']]
        plt.figure(figsize=(14, 9))
        sns.histplot(df['price'], bins=50, kde=True)
        plt.title('Distribution of Listing Prices', fontsize=16)
        plt.xlabel('Price ($)', fontsize=14)
        plt.ylabel('Frequency', fontsize=14)
        st.pyplot(plt)

    with col3:
        df = data()
        df = df[df['country']==selected_option][['room_type','country','price']]
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.countplot(x='room_type', data=df , color='hotpink')    
        ax.set_title('Room Type Distribution', fontsize=20)
        ax.set_xlabel('Room Type', fontsize=14)
        ax.set_ylabel('Count', fontsize=14)
        st.pyplot(fig)

    with col4:
        df = data()
        df = df[df['country']==selected_option][['last_review','country','price','number_of_reviews']]
        reviews_over_time = df.groupby(df['last_review'].dt.to_period('M')).size()
        plt.figure(figsize=(6, 5))
        reviews_over_time.plot(kind='line',color='red')
        plt.title('Popularity of Airbnb Over Time', fontsize=12)
        plt.xlabel('Year', fontsize=10)
        plt.ylabel('Number of Reviews', fontsize=10)
        st.pyplot(plt)

    with col5:
        df = data()
        country_df = df.groupby('country',as_index=False)['price'].mean().round(2).sort_values(by='price',ascending=False)
        fig= px.scatter(data_frame=country_df,
                x='country',y='price',
                color='country',
                size='price',
                opacity=1,
                size_max=25,
                title='Avg Listing Price in each Country')
        fig.update_layout(title_font=dict(size=14), title_x=0.3, title_y=1, xaxis_title="Country", yaxis_title="Price", 
                          margin=dict(l=10, r=10, t=10, b=10), autosize=False, showlegend=False,
                          width=200, height=350)
        fig.update_xaxes(tickangle=320, showticklabels=True, showgrid=False,showline=True, linewidth=1, linecolor='black', automargin=True, 
                         mirror=True)
        fig.update_yaxes(showticklabels=True, showgrid=False, showline=True, linewidth=1, linecolor='black', mirror=True, automargin=True)
        config = {"displayModeBar": False}  # Hides the entire toolbar
        st.plotly_chart(fig, use_container_width=True, config=config)
        
        return col1, col2, col3, col4, col5

# Check user-input to display charts on dashboard
if selected_option != "":
    main()

