import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Set the style for seaborn
sns.set_style('darkgrid')

# Main function
def main_graph():
    st.title("Interactive Plot Generator")
    st.write("Generate plots using your own data or sample datasets.")

    # Sidebar for navigation
    st.sidebar.title("Options")
    data_option = st.sidebar.selectbox("Select Data Source", ("Upload CSV", "Use Sample Dataset"))
    
    # Data loading
    if data_option == "Upload CSV":
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.success("Data loaded successfully!")
        else:
            st.warning("Awaiting CSV file upload.")
            return
    else:
        # Sample dataset options
        sample_data = st.sidebar.selectbox("Select Sample Dataset", ("Iris", "Tips", "Wine"))
        if sample_data == "Iris":
            df = sns.load_dataset('iris')
        elif sample_data == "Tips":
            df = sns.load_dataset('tips')
        # elif sample_data == "Wine":
        #     df = sns.load_dataset('wine')
        st.success(f"Loaded {sample_data} dataset.")

    st.subheader("Data Preview")
    st.write(df.head())

    # Plotting options
    st.sidebar.title("Plot Settings")
    plot_type = st.sidebar.selectbox("Select Plot Type", ("Line Plot", "Scatter Plot", "Bar Plot", "Histogram"))

    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    all_columns = df.columns.tolist()

    if plot_type != "Histogram":
        x_axis = st.sidebar.selectbox("X-Axis", options=all_columns)
        y_axis = st.sidebar.selectbox("Y-Axis", options=numeric_columns)
    else:
        x_axis = st.sidebar.selectbox("Select Column", options=numeric_columns)
        y_axis = None

    st.sidebar.subheader("Additional Settings")
    title = st.sidebar.text_input("Plot Title", value=f"My {plot_type}")
    color = st.sidebar.color_picker("Pick a Color", "#69b3a2")

    # Generate plot
    st.subheader("Generated Plot")
    fig, ax = plt.subplots(figsize=(8, 6))

    try:
        if plot_type == "Line Plot":
            sns.lineplot(data=df, x=x_axis, y=y_axis, ax=ax, color=color)
        elif plot_type == "Scatter Plot":
            sns.scatterplot(data=df, x=x_axis, y=y_axis, ax=ax, color=color)
        elif plot_type == "Bar Plot":
            sns.barplot(data=df, x=x_axis, y=y_axis, ax=ax, color=color)
        elif plot_type == "Histogram":
            sns.histplot(data=df, x=x_axis, ax=ax, color=color, bins=30)
        ax.set_title(title)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"An error occurred: {e}")

    # Option to download the plot
    st.sidebar.subheader("Download Plot")
    if st.sidebar.button("Download as PNG"):
        buf = BytesIO()
        fig.savefig(buf, format="png")
        st.sidebar.download_button(
            label="Download Image",
            data=buf.getvalue(),
            file_name="plot.png",
            mime="image/png"
        )

if __name__ == "__main__":
    main_graph()
