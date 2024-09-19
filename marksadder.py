import streamlit as st
import pandas as pd

st.title("TALENT Test tracker")

# Input for Program's Name
program_name = st.text_input("Enter the program's name:")

# File Upload Section
uploaded_file1 = st.file_uploader("Upload the first Excel file (marks)", type=["xlsx"])
uploaded_file2 = st.file_uploader("Upload the second Excel file (names & church)", type=["xlsx"])

if uploaded_file1 and uploaded_file2:
    # Read Excel Files with explicit data type for 'chest no'
    df_marks = pd.read_excel(uploaded_file1, dtype={'chest no': str})
    df_names = pd.read_excel(uploaded_file2, dtype={'chest number': str})




    # Data Processing (Calculate Total & Rank)
    df_marks['total'] = (df_marks['mark1'] + df_marks['mark2'] + df_marks['mark3']).round(2)
    df_marks = df_marks.sort_values(by='total', ascending=False)
    top_two = df_marks.head(2)

    # Data Merging (to get names and church)
    merged_df = pd.merge(df_marks, df_names, left_on='chest no', right_on='chest number')

    # Update the first DataFrame (df_marks)
    df_marks['position'] = ''  # Initialize the 'position' column
    df_marks.loc[df_marks['chest no'] == top_two.iloc[0]['chest no'], 'position'] = 'First'
    df_marks.loc[df_marks['chest no'] == top_two.iloc[1]['chest no'], 'position'] = 'Second'
    df_marks['name'] = merged_df['name']
    df_marks['church'] = merged_df['church']

    # Display Results
    st.subheader(f"Marksheet for {program_name}")
    st.table(df_marks)

    # Download Button for the updated first sheet
    st.download_button(
        label=f"Download {program_name} marksheet",
        data=df_marks.to_csv(index=False).encode('utf-8'),
        file_name=f'updated_marksheet_{program_name.replace(" ", "_")}.csv',  # Use program_name in the filename
        mime='text/csv',
    )