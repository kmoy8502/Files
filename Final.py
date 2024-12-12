"""
Name: Kayla Moy
CS230: Section 2
Data: FastFoodUSA
URL:

Description:
Exploring fast food chains in the NE states based on locational features such as latitude and longitude and zipcodes.
"""
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk

st.markdown('''
<div style='background-color: #F8C8DC; padding: 10px; border-radius: 5px;'>
    <h1>Kayla Moy: CS 230: Fast Food USA</h1>
</div>
''', unsafe_allow_html=True)


try: #[PY1] CODE WITH A TRY/EXCEPT
    df_whole = pd.read_csv('fast_food_usa.csv', index_col='index')
except:
    print('Could not find csv')
state_name_dict = {}
province_zipcode_dict = {}

def clean_data(df_whole):
    new_england_states = ['CT', 'ME', 'MA', 'NH', 'RI', 'VT']
    cleaned_df = df_whole[df_whole['province'].isin(new_england_states)] #[DA1] FILTER BY ONE CONDITION
    cleaned_df = cleaned_df.drop('sourceURLs', axis=1) #[DA2] DROP COLUMN
    cleaned_df = cleaned_df.drop('websites', axis=1)
    cleaned_df = cleaned_df.drop('id', axis=1)
    cleaned_df = cleaned_df.drop('keys', axis=1)
    cleaned_df = cleaned_df.drop('country', axis=1)
    cleaned_df['dateAdded'] = pd.to_datetime(cleaned_df['dateAdded']) #[DA3] MANIPULATE DATA
    return cleaned_df

def create_dicts(cleaned_df):
    #create dictionary of states and restuarants in state
    for index, row in cleaned_df.iterrows(): #[DA4] ITERATE THROUGH ROWS WITH ITERROWS()
        state = row['province']
        name = row['name']

        #create key if not already in dictionary
        if state not in state_name_dict:
            state_name_dict[state] = []

        #add restuarants to list
        state_name_dict[state].append(name)

        #create dictionary of zipcodes per state
        for index, row in cleaned_df.iterrows():
            province = row['province']
            zipcode = row['postalCode']

            # create key if not already in the dictionary
            if province not in province_zipcode_dict:
                province_zipcode_dict[province] = []

            # Add zipcodes to dictionary
            if zipcode not in province_zipcode_dict[province]:
                province_zipcode_dict[province].append(zipcode)
    return state_name_dict, province_zipcode_dict #[PY2] FUNCTION THAT RETURNS TWO VALUES


# Clean the DataFrame
cleaned_df = clean_data(df_whole)
#create dictionaries
state_names, state_zips = create_dicts(cleaned_df)

def intro(cleaned_df):
    cleaned_df = cleaned_df.sort_values('city', ascending = True) #[DA5] SORT DATA IN A ASCENDING ORDER
    df = cleaned_df.head(10)
    st.title('New England Fast Food Restuarants')
    st.subheader('Data examples')
    st.write(df)

def find_earliest_entry(cleaned_df):
    earliest_added_restaurant = cleaned_df.loc[cleaned_df['dateAdded'].idxmin()] #[DA6] FIND MIN SMALLEST VALUE OF COLUMN
    st.subheader("Earliest Added Restaurant from NE:")
    st.write(f"Name: {earliest_added_restaurant['name']}")
    st.write(f"Address: {earliest_added_restaurant['address']}")
    st.write(f"City: {earliest_added_restaurant['city']}")
    st.write(f"Province: {earliest_added_restaurant['province']}")
    st.write(f"Postal Code: {earliest_added_restaurant['postalCode']}")
    st.write(f"Date Added: {earliest_added_restaurant['dateAdded']}")

def create_state_selector(cleaned_df):
    selected_states = st.sidebar.multiselect( #[ST4] CREATION OF SIDEBAR
        'Select States',
        options= sorted(cleaned_df['province'].unique()), #[ST1] CREATION OF MULTISELECT
    )
    return selected_states


def create_bar(state_names, selected_states): #[VIZ1] BAR CHART OF RESTUARANTS PER STATE
    if selected_states:
        state_counts = {state: len(state_names[state]) for state in selected_states} #[PY3] LIST COMPHRENSHION
    else:
        state_counts = {state: len(restaurants) for state, restaurants in state_names.items()} #[PY4] DICTIONARY CODE TO ACCESS ITEMS

    # Create a bar plot using matplotlib see source 1
    plt.figure(figsize=(10, 6))
    plt.bar(state_counts.keys(), state_counts.values(), color='skyblue')
    plt.xlabel('States')
    plt.ylabel('Number of Restaurants')
    plt.title('Number of Fast Food Restaurants in New England States')
    plt.xticks(rotation=45)
    plt.tight_layout()

    #write to streamlit
    st.header('Fast Food Restaurants in New England')
    st.pyplot(plt)

def create_zip_selector(selected_states, cleaned_df):
    if selected_states:
        filtered_df = cleaned_df[cleaned_df['province'].isin(selected_states)]
        unique_zipcodes = filtered_df['postalCode'].unique()
        selected_zip = st.sidebar.selectbox('Select a Zip', options = unique_zipcodes) #[ST2] SELECT BOX

        if selected_zip:
            province_for_zip = filtered_df[filtered_df['postalCode'] == selected_zip]['province'].values[0]
            st.subheader(f"The province for zip code **{selected_zip}** is **{province_for_zip}**.")
        return selected_zip


def create_pie(state_zips): #[VIZ2] PIECHART OF ZIPCODE FREQUENCY BY STATE

    zip_counts = {province: len(zipcodes) for province, zipcodes in state_zips.items()}

    # Create chart see source 2 of disclaimer
    plt.figure(figsize=(8, 8))
    plt.pie(zip_counts.values(), labels=zip_counts.keys(), autopct='%1.1f%%', startangle=140)
    plt.title('Distribution of Unique Zip Codes in New England States')

    #write to streamlit
    st.title('Unique Zip Codes Distribution in New England Fast Food Restaurant Data')
    st.pyplot(plt)


def create_map(cleaned_df): #based on code used in the example of final project posted on sandbox site source 4
    map_df = cleaned_df.filter(['name', 'latitude', 'longitude'])

    zoom_level = st.slider("Select Zoom Level", min_value=1, max_value=20, value=7) #[ST3] USAGE OF SLIDER
    view_state = pdk.ViewState(latitude=map_df['latitude'].mean(),
                               longitude=map_df['longitude'].mean(),
                               zoom = zoom_level)
    #creates scatterplot layer
    layer = pdk.Layer('ScatterplotLayer',
                      data=map_df,
                      get_position = '[longitude, latitude]',
                      get_radius = 1200,
                      get_color = [150, 175, 200],
                      pickable = True)


    tooltip = {'html': 'Name:<br>,<b>{name}</b>',
                'style': {'backgroundColor': 'steelblue', 'color': 'white'}}
    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers = [layer],
                   tooltip = tooltip)

    st.pydeck_chart(map)

def create_map2(selected_states, cleaned_df): #[MAP] INTERACTIVE MAP
    if selected_states:
        # filter based on selected states
        filtered_df = cleaned_df[cleaned_df['province'].isin(selected_states)]

        # Check if there are any locations to display
        if not filtered_df.empty:
            # Create a map view centered around the mean latitude and longitude
            view_state = pdk.ViewState(
                latitude=filtered_df['latitude'].mean(),
                longitude=filtered_df['longitude'].mean(),
                zoom=7,
                pitch=0
            )

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=filtered_df,
                get_position='[longitude, latitude]',
                get_radius=1000,
                get_color=[255, 0, 0],
                pickable=True,
            )
            tooltip = {'html': 'Name:<br>,<b>{name}</b>',
                       'style': {'backgroundColor': 'steelblue', 'color': 'white'}}
            map = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                map_style='mapbox://styles/mapbox/light-v9',
                tooltip = tooltip
            )

            st.pydeck_chart(map)
        else:
            st.write("No restaurants found for the selected states.")

def create_3d_map(cleaned_df): #[VIZ3] Map with elevated structures (from streamlit website)
    chart_data = cleaned_df[['latitude', 'longitude']].dropna()
    st.title("Fast Food Restaurants Visualization")

    # Create a Pydeck chart
    st.pydeck_chart(
        pdk.Deck(
            map_style=None,  # You can set a specific map style here if needed
            initial_view_state=pdk.ViewState(
                latitude=cleaned_df['latitude'].mean(),  # Centering the map on the mean latitude
                longitude=cleaned_df['longitude'].mean(),  # Centering the map on the mean longitude
                zoom=9,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    data=chart_data,
                    get_position="[longitude, latitude]",
                    radius=200,
                    elevation_scale=4,
                    elevation_range=[0, 1000],
                    pickable=True,
                    extruded=True,
                ),
                pdk.Layer(
                    "ScatterplotLayer",
                    data=chart_data,
                    get_position="[longitude, latitude]",
                    get_color="[200, 30, 0, 160]",
                    get_radius=200,
                ),
            ],
        )
    )


intro(cleaned_df)
find_earliest_entry(cleaned_df)
selected_states =create_state_selector(cleaned_df)
create_map(cleaned_df)
create_bar(state_names, selected_states)
create_3d_map(cleaned_df)
create_map2(selected_states, cleaned_df)
create_zip_selector(selected_states, cleaned_df)
create_pie(state_zips)

