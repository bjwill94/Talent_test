# THIS IS AN APPLICATION WHERE THE FULL LIST OF THE PROGRAMS ARE GIVEN IN A SINGLE FILE AND
# FROM THE FILE, THE CLASSES, AND ITEMS ARE DISPLAYED,AND ON SELECTING A PARTICULAR ITEM, THE PARTICIPANTS
# MARKSHEET IS VISIBLE, WHICH ON UPDATING, WE WILL GET AN UPDATED FILE IN WHICH THE FIRST, SECOND ARE NOTED AND CSV CAN BE DOWNLAODED

import streamlit as st
import pandas as pd

# Streamlit app
st.title("Contestant Marks Entry and Results")

# File upload
uploaded_file = st.file_uploader("Upload Excel file with full program list", type=["xlsx"])

if uploaded_file is not None:
    # Read the Excel file into a DataFrame, explicitly setting 'chest no' as string
    df = pd.read_excel(uploaded_file, dtype={'chest no': str})

    # Explode the 'items' column to handle multiple items per contestant
    df['items'] = df['items'].str.split(', ')
    df = df.explode('items')

    # Class selection buttons
    selected_class = st.radio("Select Class:", df['class'].unique())

    # Filter DataFrame based on selected class
    filtered_df = df[df['class'] == selected_class]

    # Item dropdown (dynamically populated based on selected class)
    available_items = filtered_df['items'].unique()
    selected_item = st.selectbox("Select Item:", available_items)

    # Filter further based on selected item
    final_df = filtered_df[filtered_df['items'] == selected_item]

    # Drop duplicates based on 'chest no' after filtering
    final_df = final_df.drop_duplicates(subset=['chest no'])

    # Add columns for mark entry with float data type
    final_df['mark1'] = 0.0
    final_df['mark2'] = 0.0
    final_df['mark3'] = 0.0

    # Make the mark columns editable, displaying only the desired columns
    # edited_df = st.experimental_data_editor(final_df[['chest no', 'name', 'mark1', 'mark2', 'mark3', 'church']])
    edited_df = st.data_editor(final_df[['chest no', 'name', 'mark1', 'mark2', 'mark3', 'church']])


    # Submit button
    if st.button("Submit Marks"):
        # Calculate total marks
        edited_df['total'] = edited_df['mark1'] + edited_df['mark2'] + edited_df['mark3']

        # Round the total and mark columns to two decimal places
        edited_df['total'] = edited_df['total'].round(2)
        edited_df['mark1'] = edited_df['mark1'].round(2)
        edited_df['mark2'] = edited_df['mark2'].round(2)
        edited_df['mark3'] = edited_df['mark3'].round(2)

        # Convert 'chest no' to integer
        edited_df['chest no'] = pd.to_numeric(edited_df['chest no'], errors='coerce').astype('Int64')

        # Sort by total marks in descending order
        edited_df = edited_df.sort_values(by='total', ascending=False)

        # Reset the index of the edited DataFrame
        edited_df = edited_df.reset_index(drop=True)

        # Assign positions dynamically
        edited_df['position'] = ''
        if not edited_df.empty:
            edited_df.loc[0, 'position'] = 'First'
            for i in range(1, len(edited_df)):
                if edited_df.loc[i, 'total'] != edited_df.loc[0, 'total']:
                    edited_df.loc[i, 'position'] = 'Second'
                    break

        # Display the final DataFrame
        st.subheader("Results:")

        # Format the columns to display only two decimal places
        edited_df[['mark1', 'mark2', 'mark3', 'total']] = edited_df[['mark1', 'mark2', 'mark3', 'total']].applymap('{:.2f}'.format)

        st.table(edited_df)

        # Download button for the updated results (CSV format)
        csv = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Download {selected_class}-{selected_item}-winner.csv",
            data=csv,
            file_name=f"{selected_class}-{selected_item}-winner.csv",
            mime='text/csv'
        )
