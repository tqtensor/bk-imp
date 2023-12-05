import dataset_page
import model_page
import optimization_page
import streamlit as st

PAGES = {
    "Dataset": dataset_page,
    "Model": model_page,
    "Optimization": optimization_page,
}


def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    page = PAGES[selection]

    with st.spinner(f"Loading {selection} ..."):
        page.app()


if __name__ == "__main__":
    main()
