import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Follower Comparison", layout="wide")

from app import process_json_data, get_text  # adjust import

st.title("📊 Follower Comparison")

st.write("Upload two different follower JSON files to compare who you gained or lost.")


old_file = st.file_uploader("Upload OLD followers.json", type=["json"], key="old_followers")
new_file = st.file_uploader("Upload NEW followers.json", type=["json"], key="new_followers")

if old_file and new_file:
    try:
        old_data = json.load(old_file)
        new_data = json.load(new_file)

        df_old = process_json_data(old_data, "followers")
        df_new = process_json_data(new_data, "followers")

        old_set = set(df_old["username"])
        new_set = set(df_new["username"])

        gained = new_set - old_set
        lost = old_set - new_set
        unchanged = new_set & old_set

        st.subheader("📈 Followers Gained")
        st.write(len(gained))
        st.dataframe(pd.DataFrame({"username": list(gained)}))

        st.subheader("📉 Followers Lost")
        st.write(len(lost))
        st.dataframe(pd.DataFrame({"username": list(lost)}))

        st.subheader("🔁 Unchanged Followers")
        st.write(len(unchanged))
        st.dataframe(pd.DataFrame({"username": list(unchanged)}))

        # -----------------------
        # Growth number
        # -----------------------
        st.subheader("📊 Follower Count Summary")
        st.write(f"Old snapshot: **{len(old_set)}** followers")
        st.write(f"New snapshot: **{len(new_set)}** followers")

        diff = len(new_set) - len(old_set)
        if diff >= 0:
            st.success(f"Net growth: **+{diff}**")
        else:
            st.error(f"Net loss: **{diff}**")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload both JSON files to begin comparison.")
