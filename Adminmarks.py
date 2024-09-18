import streamlit as st
import pandas as pd
import io

# Streamlit app
st.title("Contestant Marks Entry and Results")

# File upload
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

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
    edited_df = st.experimental_data_editor(final_df[['chest no', 'name', 'mark1', 'mark2', 'mark3', 'church']])

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
        edited_df['chest no'] = pd.to_numeric(edited_df['chest no'], errors='coerce').astype('Int64')  # Handle potential non-numeric values

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
        edited_df[['mark1', 'mark2', 'mark3', 'total']] = edited_df[['mark1', 'mark2', 'mark3', 'total']].applymap(
            '{:.2f}'.format)

        st.table(edited_df)

        # Download button for the updated results
        with io.BytesIO() as buffer:
            edited_df.to_excel(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                label=f"Download {selected_class}-{selected_item}-winner.xlsx",
                data=buffer.read(),
                file_name=f"{selected_class}-{selected_item}-winner.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )