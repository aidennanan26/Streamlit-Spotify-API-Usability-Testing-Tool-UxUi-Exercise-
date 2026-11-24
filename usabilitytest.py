import streamlit as st
import pandas as pd
import time
import os

# Create a folder called data in the main project folder
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Define CSV file paths for each part of the usability testing
CONSENT_CSV = os.path.join(DATA_FOLDER, "consent_data.csv")
DEMOGRAPHIC_CSV = os.path.join(DATA_FOLDER, "demographic_data.csv")
TASK_CSV = os.path.join(DATA_FOLDER, "task_data.csv")
EXIT_CSV = os.path.join(DATA_FOLDER, "exit_data.csv")

# ---------------------------------------------------------------------
# PROJECT SETTINGS - fill these in for the product you are testing
# ---------------------------------------------------------------------
PRODUCT_NAME = "Sound Atlas"

# Your 4 tasks. Write realistic scenarios with a specific goal and do not
# use the exact menu/label names the participant has to find (NN/g guidance).
TASKS = {
    "Task 1: Find an artist": "You just heard a song by Bad Bunny and want to look up the artist behind it. "
                              "Find him in the app and make sure you are looking at the right person.",
    "Task 2: Narrow the catalog": "You only care about his full-length records, not the small releases. "
                                  "Show just those, with the newest first, and no more than 10 of them.",
    "Task 3: Check a release": "You are driving with your young cousin and want to play one of his releases. "
                               "Pick one and tell me how many of its songs are safe to play around a child.",
    "Task 4: Find the hometown": "You are curious where in the world he and the other artists you found come from. "
                                 "Find out where he is from.",
}

# Difficulty scale from the sample task-based questions document
DIFFICULTY_LABELS = {
    0: "0 - Completed with zero difficulty",
    1: "1 - Completed with only minor problem(s)",
    2: "2 - Completed, but needed more effort/time/dead-ends than expected",
    3: "3 - Did not complete the task",
}


def save_to_csv(data_dict, csv_file):
    # Convert dict to DataFrame with a single row
    df_new = pd.DataFrame([data_dict])
    if not os.path.isfile(csv_file):
        # If CSV doesn't exist, write with headers
        df_new.to_csv(csv_file, mode='w', header=True, index=False)
    else:
        # Else, we need to append without writing the header!
        df_new.to_csv(csv_file, mode='a', header=False, index=False)


def load_from_csv(csv_file):
    if os.path.isfile(csv_file):
        return pd.read_csv(csv_file)
    else:
        return pd.DataFrame()


def main():
    st.title("Usability Testing Tool")

    # One ID per participant (P1, P2, P3...) so every CSV can be linked
    participant_id = st.text_input("Participant ID (e.g., P1)").strip().upper()

    home, consent, demographics, tasks, exit, report = st.tabs(["Home", "Consent", "Demographics", "Task", "Exit Questionnaire", "Report"])

    with home:
        st.header("Introduction")
        st.write(f"""
        Welcome to the Usability Testing Tool for HCI. Today you will help
        evaluate **{PRODUCT_NAME}**.

        In this app, you will:
        1. Provide consent for data collection.
        2. Fill out a short demographic questionnaire.
        3. Perform a specific task (or tasks).
        4. Answer an exit questionnaire about your experience.
        5. View a summary report (for demonstration purposes).
        """)

        # Facilitator script (customized from the sample script) - read aloud
        with st.expander("Test Facilitator Script (read exactly as written)"):
            st.markdown(f"""
            ### Welcome and Purpose
            Thank you for agreeing to participate in this {PRODUCT_NAME} product evaluation. Today we are asking you to serve as a participant to help evaluate this {PRODUCT_NAME} product and to complete a set of scenarios. Our goal is to see how easy or difficult you find the {PRODUCT_NAME} product to use. We will record your reactions and opinions; so, we may ask you to clarify statements that you make from time to time.

            ### Test Facilitator's Role
            I'm here to record your reactions and comments of the {PRODUCT_NAME} product you'll test today. During this session I will not be able to offer any suggestions or hints. There may be times, however, when I'll ask you to explain why you said or did something.

            ### Test Participant's Role
            I will ask you to complete a set of tasks, to learn if it works well for you. We ask that you "think out loud" as you work through these tasks. Tell us everything you are thinking as you attempt to determine how to complete each step. You also will be asked a series of questions about your experience at the end of this session.

            ### Things to Keep in Mind
            - This is not a test of you; you're testing the {PRODUCT_NAME} product. So don't worry about making mistakes.
            - There is no right or wrong answer. We really just want to know if we designed the product well for you.
            - If you ever feel that you are lost or cannot complete a scenario with the information that you have been given, please let me know. I'll ask you what you might do in a real-world setting and then move you on to the next task.
            - We will be taking notes during this session for further study if needed. Your name will not be associated or reported with data or findings from this evaluation. Please fill out the consent form.
            - Finally, as you use the {PRODUCT_NAME} product, please do so as you would at home or your office.

            **Do you have any questions before we begin?**
            """)

    with consent:
        st.header("Consent Form")

        # TODO: Create your consent form and a variable called consent_given
        # (customized from the sample consent form)
        st.write(f"""
        **{PRODUCT_NAME} - Experiment Consent Form**

        Human-Computer Interaction - Usability Test

        **Purpose:** This study evaluates how easy a product is to use. You are testing the product, not being tested yourself.

        **Procedure:** You will complete a short questionnaire, perform tasks while being observed and timed, and then answer feedback questions.

        **Data collected:** Demographic information, task completion time and success, observer notes, and your feedback. Data is stored locally and is used only for this course project.

        **Voluntary participation:** You may stop at any time without penalty.

        **Confidentiality:** Results are reported in aggregate only.

        I consent to the use of the information collected during the experiment for the interviewer's written report. I understand that my name and personal information will not be released or distributed for commercial use. It will only be used for the purposes of this HCI usability test project.
        """)

        signature = st.text_input("Signature (type your full name)")
        is_adult = st.checkbox("I am at least 18 years old.")
        consent_given = st.checkbox("I have read the above and agree to participate in this usability test.")

        if st.button("Submit Consent"):
            if not participant_id:
                st.warning("Enter a Participant ID at the top of the page first.")
            elif not is_adult:
                st.error("Participants must be at least 18 years old.")
            elif not consent_given or not signature.strip():
                st.warning("You must agree to the consent terms and sign before proceeding.")
            else:
                # Save the consent acceptance time
                data_dict = {
                    "participant_id": participant_id,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "signature": signature.strip(),
                    "consent_given": consent_given
                }
                save_to_csv(data_dict, CONSENT_CSV)
                st.success("Consent submitted successfully.")

    with demographics:
        st.header("Demographic Questionnaire")

        with st.form("demographic_form"):
            #TODO: Create the demographic form
            # (entrance questionnaire + eligibility screening)
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=18, max_value=120, value=18, step=1)
            gender = st.radio("Gender", ["Woman", "Man", "Non-binary", "Prefer not to say"], horizontal=True)
            education = st.selectbox("Highest level of education completed", [
                "Some high school", "High school diploma / GED", "Some college",
                "Associate degree", "Bachelor's degree", "Graduate degree"])
            occupation = st.text_input("Occupation")
            cs_it_major = st.radio("Is your major (or field of work) Computer Science or Information Technology?",
                                   ["No", "Yes"], horizontal=True)
            knows_product = st.radio(f"Have you used or are you familiar with {PRODUCT_NAME}?",
                                     ["No", "Yes"], horizontal=True)
            familiarity = st.radio(
                "How familiar are you with music apps or music-search websites?",
                ["Not at all", "Slightly", "Moderately", "Very", "Expert"],
                horizontal=True
            )
            submitted = st.form_submit_button("Submit Demographics")
            if submitted:
                if not participant_id:
                    st.warning("Enter a Participant ID at the top of the page first.")
                else:
                    # Participants must not be CS/IT majors or already know the product
                    qualified = "No" if (cs_it_major == "Yes" or knows_product == "Yes") else "Yes"
                    data_dict = {
                        "participant_id": participant_id,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "name": name,
                        "age": age,
                        "gender": gender,
                        "education": education,
                        "occupation": occupation,
                        "cs_it_major": cs_it_major,
                        "knows_product": knows_product,
                        "familiarity": familiarity,
                        "qualified": qualified
                    }
                    save_to_csv(data_dict, DEMOGRAPHIC_CSV)
                    if qualified == "Yes":
                        st.success("Demographics submitted successfully. Participant is eligible.")
                    else:
                        st.error("Participant is NOT eligible (CS/IT major or already familiar with the product). "
                                 "Thank them, do not run the tasks, and still offer the reward.")

    with tasks:
        st.header("Task Page")

        st.write("Please select a task and record your experience completing it.")

        # Four tasks are defined in TASKS at the top of the file
        selected_task = st.selectbox("Select Task", list(TASKS.keys()))
        st.write("Task Description (read aloud to the participant):")
        st.info(TASKS[selected_task])
        st.caption("Facilitator: use this wording, do not lead or help, and remind the participant "
                   "to think out loud. We are testing the product, not them.")

        # Track success, completion time, etc.
        start_button = st.button("Start Task Timer")
        if start_button:
            st.session_state["start_time"] = time.time()
            st.session_state.pop("task_duration", None)  # clear any older recorded time

        stop_button = st.button("Stop Task Timer")
        if stop_button and "start_time" in st.session_state:
            duration = time.time() - st.session_state["start_time"]
            st.session_state["task_duration"] = duration
            del st.session_state["start_time"]  # timer is no longer running

        if "start_time" in st.session_state:
            st.info("Timer is running.")
        elif "task_duration" in st.session_state:
            st.success(f"Recorded time: {st.session_state['task_duration']:.1f} seconds")

        success = st.radio("Was the task completed successfully?", ["Yes", "No", "Partial"])
        difficulty_rating = st.radio("Facilitator's difficulty rating", list(DIFFICULTY_LABELS.keys()),
                                     format_func=lambda x: DIFFICULTY_LABELS[x])
        notes = st.text_area("Observer Notes (what the participant did and said, paths taken, dead-ends)")

        if st.button("Save Task Results"):
            demo_check = load_from_csv(DEMOGRAPHIC_CSV)
            disqualified = False
            if not demo_check.empty and "participant_id" in demo_check.columns:
                rows = demo_check[demo_check["participant_id"].astype(str) == participant_id]
                # Use the most recent demographics submission for this participant
                disqualified = (not rows.empty) and rows.iloc[-1]["qualified"] == "No"
            if not participant_id:
                st.warning("Enter a Participant ID at the top of the page first.")
            elif disqualified:
                st.error("This participant was disqualified. Do not record task results.")
            else:
                duration_val = st.session_state.get("task_duration", None)

                data_dict = {
                    "participant_id": participant_id,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "task_name": selected_task,
                    "success": success,
                    "difficulty_rating": difficulty_rating,
                    "duration_seconds": duration_val if duration_val else "",
                    "notes": notes
                }
                save_to_csv(data_dict, TASK_CSV)

                # Reset any stored time in session_state if you'd like
                if "start_time" in st.session_state:
                    del st.session_state["start_time"]
                if "task_duration" in st.session_state:
                    del st.session_state["task_duration"]

                st.success("Task results saved successfully.")

    with exit:
        st.header("Exit Questionnaire")

        with st.form("exit_form"):
            # TODO: likert scale or other way to have an exit questionnaire
            # Likert scales (1-5) plus the open-ended questions from the sample exit questionnaire
            st.caption("Rate from 1 (lowest) to 5 (highest)")
            satisfaction = st.select_slider(
                "Overall, how satisfied were you with the product? (1 = very dissatisfied, 5 = very satisfied)",
                options=[1, 2, 3, 4, 5], value=3)
            difficulty = st.select_slider(
                "How difficult was it to complete the tasks? (1 = very easy, 5 = very difficult)",
                options=[1, 2, 3, 4, 5], value=3)
            navigation_ease = st.select_slider(
                "How easy was it to navigate the product? (1 = very difficult, 5 = very easy)",
                options=[1, 2, 3, 4, 5], value=3)
            terminology_clarity = st.select_slider(
                "How clear were the labels and terminology? (1 = very confusing, 5 = very clear)",
                options=[1, 2, 3, 4, 5], value=3)
            confidence = st.select_slider(
                "How confident did you feel while using the product? (1 = not at all, 5 = extremely)",
                options=[1, 2, 3, 4, 5], value=3)

            q_confusing = st.text_area(f"1. What features of {PRODUCT_NAME} were vague or confusing to you, if any?")
            q_navigation = st.text_area("2. What is your impression about navigating the site/product? Does it seem easy or difficult? What makes it that way?")
            q_missing = st.text_area(f"3. What else should be included in {PRODUCT_NAME}?")
            q_best = st.text_area("4. What did you like best about the site/product?")
            q_least = st.text_area("5. What did you like the least?")
            q_others = st.text_area("6. Do you think some people would have problems using it? What kinds of people? What kinds of problems?")
            open_feedback = st.text_area("7. Would you like to make any other comments?")

            submitted_exit = st.form_submit_button("Submit Exit Questionnaire")
            if submitted_exit:
                if not participant_id:
                    st.warning("Enter a Participant ID at the top of the page first.")
                else:
                    data_dict = {
                        "participant_id": participant_id,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "satisfaction": satisfaction,
                        "difficulty": difficulty,
                        "navigation_ease": navigation_ease,
                        "terminology_clarity": terminology_clarity,
                        "confidence": confidence,
                        "confusing_features": q_confusing,
                        "navigation_impression": q_navigation,
                        "missing_features": q_missing,
                        "liked_best": q_best,
                        "liked_least": q_least,
                        "problems_for_others": q_others,
                        "open_feedback": open_feedback
                    }
                    save_to_csv(data_dict, EXIT_CSV)
                    st.success("Exit questionnaire data saved.")

    with report:
        st.header("Usability Report - Aggregated Results")

        st.write("**Consent Data**")
        consent_df = load_from_csv(CONSENT_CSV)
        if not consent_df.empty:
            # Hide the typed signature so names are not shown in the report
            st.dataframe(consent_df.drop(columns=["signature"], errors="ignore"))
        else:
            st.info("No consent data available yet.")

        st.write("**Demographic Data**")
        demographic_df = load_from_csv(DEMOGRAPHIC_CSV)
        if not demographic_df.empty:
            st.dataframe(demographic_df.drop(columns=["name"], errors="ignore"))
        else:
            st.info("No demographic data available yet.")

        st.write("**Task Performance Data**")
        task_df = load_from_csv(TASK_CSV)
        if not task_df.empty:
            st.dataframe(task_df)
        else:
            st.info("No task data available yet.")

        st.write("**Exit Questionnaire Data**")
        exit_df = load_from_csv(EXIT_CSV)
        if not exit_df.empty:
            st.dataframe(exit_df)
        else:
            st.info("No exit questionnaire data available yet.")

        # Only analyze participants who qualified (not CS/IT, not familiar with product)
        qualified_ids = set()
        if not demographic_df.empty and "qualified" in demographic_df.columns:
            # Use each participant's most recent demographics submission
            latest_demo = demographic_df.drop_duplicates(subset="participant_id", keep="last")
            qualified_ids = set(latest_demo.loc[latest_demo["qualified"] == "Yes",
                                                "participant_id"].astype(str))
            st.subheader("Participants")
            st.write(f"Screened: {len(latest_demo)} | Qualified: {len(qualified_ids)} | "
                     f"Disqualified: {len(latest_demo) - len(qualified_ids)}")
        if not exit_df.empty and "participant_id" in exit_df.columns:
            completed = exit_df["participant_id"].astype(str).isin(qualified_ids).sum()
            st.write(f"Completed sessions (with exit questionnaire): {completed}")
            if completed < 3:
                st.warning("At least 3 completed test sessions are required.")

        # Aggregated task stats per task
        if not task_df.empty and "participant_id" in task_df.columns:
            t = task_df[task_df["participant_id"].astype(str).isin(qualified_ids)].copy()
            if not t.empty:
                st.subheader("Task Performance Summary")
                t["duration_seconds"] = pd.to_numeric(t["duration_seconds"], errors="coerce")
                t["difficulty_rating"] = pd.to_numeric(t["difficulty_rating"], errors="coerce")
                t["completed_pct"] = (t["difficulty_rating"] < 3) * 100
                summary = t.groupby("task_name").agg(
                    participants=("participant_id", "nunique"),
                    completion_rate_pct=("completed_pct", "mean"),
                    avg_time_seconds=("duration_seconds", "mean"),
                    avg_difficulty_0_to_3=("difficulty_rating", "mean"),
                ).round(2)
                st.dataframe(summary)
                st.bar_chart(summary["avg_difficulty_0_to_3"])

                # Same results sliced by demographics
                if not demographic_df.empty:
                    demo = demographic_df.drop_duplicates(subset="participant_id", keep="last").copy()
                    demo["participant_id"] = demo["participant_id"].astype(str)
                    demo["age_group"] = pd.cut(pd.to_numeric(demo["age"], errors="coerce"), bins=[17, 24, 34, 44, 54, 200],
                                               labels=["18-24", "25-34", "35-44", "45-54", "55+"]).astype(str)
                    t["participant_id"] = t["participant_id"].astype(str)
                    merged = t.merge(demo[["participant_id", "age_group", "gender", "education", "familiarity"]],
                                     on="participant_id", how="left")
                    for col in ["age_group", "gender", "education", "familiarity"]:
                        st.write(f"**Task results by {col.replace('_', ' ')}**")
                        st.dataframe(merged.groupby(col).agg(
                            participants=("participant_id", "nunique"),
                            avg_time_seconds=("duration_seconds", "mean"),
                            avg_difficulty_0_to_3=("difficulty_rating", "mean"),
                        ).round(2))

        # Example of aggregated stats (for demonstration only)
        if not exit_df.empty:
            st.subheader("Exit Questionnaire Averages")
            avg_satisfaction = exit_df["satisfaction"].mean()
            avg_difficulty = exit_df["difficulty"].mean()
            st.write(f"**Average Satisfaction**: {avg_satisfaction:.2f}")
            st.write(f"**Average Difficulty**: {avg_difficulty:.2f}")
            for col, label in [("navigation_ease", "Navigation Ease"),
                               ("terminology_clarity", "Terminology Clarity"),
                               ("confidence", "Confidence")]:
                if col in exit_df.columns:
                    st.write(f"**Average {label}**: {exit_df[col].mean():.2f}")

        # Download raw data so it can be opened in Excel for the final report
        st.subheader("Download Raw Data")
        for label, path in [("Consent", CONSENT_CSV), ("Demographics", DEMOGRAPHIC_CSV),
                            ("Tasks", TASK_CSV), ("Exit Questionnaire", EXIT_CSV)]:
            df = load_from_csv(path)
            if not df.empty:
                if label == "Consent":
                    df = df.drop(columns=["signature"], errors="ignore")
                if label == "Demographics":
                    df = df.drop(columns=["name"], errors="ignore")
                st.download_button(f"Download {label} (CSV)", df.to_csv(index=False),
                                   file_name=os.path.basename(path), mime="text/csv", key=f"dl_{label}")


if __name__ == "__main__":
    main()