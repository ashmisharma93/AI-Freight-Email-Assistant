
import requests
import pandas as pd
import streamlit as st

API_URL = "https://ai-freight-email-assistant.onrender.com/emails"
REVIEW_STATUS_URL = API_URL
REQUEST_TIMEOUT = 30

ALLOWED_REVIEW_STATUSES = [
    "Pending Review",
    "Reviewed",
    "Needs Follow-up",
]

st.set_page_config(
    page_title="Freight Operations Dashboard",
    layout="wide",
)

st.title("Freight Operations Dashboard")
st.caption("AI Freight Operations Assistant")


@st.cache_data(ttl=30, show_spinner=False)
def fetch_emails():
    response = requests.get(
        API_URL,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise ValueError(
            "The API did not return a list of email records."
        )

    return pd.DataFrame(data)


def update_review_status(email_id, review_status):
    url = f"{REVIEW_STATUS_URL}/{email_id}/review-status"

    response = requests.patch(
        url,
        json={"review_status": review_status},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    return response.json()


# Load email records
try:
    with st.spinner("Loading email records..."):
        df = fetch_emails()

except requests.exceptions.Timeout:
    st.error("The API took too long to respond. Please try again.")
    st.stop()

except requests.exceptions.HTTPError as error:
    st.error(
        f"API error while loading emails: "
        f"{error.response.status_code} - "
        f"{error.response.text}"
    )
    st.stop()

except requests.exceptions.RequestException as error:
    st.error(f"Unable to retrieve emails from the API: {error}")
    st.stop()

except ValueError as error:
    st.error(f"Invalid API response: {error}")
    st.stop()


# Ensure expected columns exist
expected_columns = [
    "email_id",
    "thread_id",
    "sender",
    "subject",
    "body",
    "category",
    "needs_human_review",
    "review_status",
]

for column in expected_columns:
    if column not in df.columns:
        df[column] = ""

if df.empty:
    st.info("No email records are available yet.")
    st.stop()

df = df.fillna("")

df["category"] = df["category"].replace("", "other")
df["review_status"] = df["review_status"].replace(
    "",
    "Pending Review",
)


# Sidebar filters
st.sidebar.header("Filters")

categories = sorted(df["category"].unique().tolist())

selected_categories = st.sidebar.multiselect(
    "Email category",
    options=categories,
    default=categories,
)

statuses = sorted(df["review_status"].unique().tolist())

selected_statuses = st.sidebar.multiselect(
    "Review status",
    options=statuses,
    default=statuses,
)

search_text = st.sidebar.text_input(
    "Search by sender or subject"
)

if st.sidebar.button("Refresh data"):
    st.cache_data.clear()
    st.rerun()


# Filter records
filtered_df = df[
    df["category"].isin(selected_categories)
    & df["review_status"].isin(selected_statuses)
].copy()

if search_text.strip():
    query = search_text.strip()

    matches = (
        filtered_df["sender"].str.contains(
            query,
            case=False,
            regex=False,
            na=False,
        )
        | filtered_df["subject"].str.contains(
            query,
            case=False,
            regex=False,
            na=False,
        )
    )

    filtered_df = filtered_df[matches]


# Summary metrics
pending_count = (
    df["review_status"].str.casefold() == "pending review"
).sum()

reviewed_count = (
    df["review_status"].str.casefold() == "reviewed"
).sum()

follow_up_count = (
    df["review_status"].str.casefold() == "needs follow-up"
).sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Emails", len(df))
col2.metric("Pending Review", int(pending_count))
col3.metric("Reviewed", int(reviewed_count))
col4.metric("Needs Follow-up", int(follow_up_count))


# Charts
st.divider()

chart_column, status_column = st.columns([2, 1])

with chart_column:
    st.subheader("Emails by Category")
    category_counts = df["category"].value_counts()
    st.bar_chart(category_counts)

with status_column:
    st.subheader("Review Status")
    status_counts = df["review_status"].value_counts()
    st.bar_chart(status_counts)


# Email table
st.divider()

st.subheader("Freight Emails")

st.caption(
    f"Showing {len(filtered_df)} of {len(df)} emails."
)

display_columns = [
    "sender",
    "subject",
    "category",
    "needs_human_review",
    "review_status",
]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    hide_index=True,
)


# Email details and review-status editor
with st.expander("View email details"):
    if filtered_df.empty:
        st.info("No emails match the selected filters.")

    else:
        email_indices = filtered_df.index.tolist()

        selected_index = st.selectbox(
            "Select an email",
            options=email_indices,
            format_func=lambda index: (
                f"{filtered_df.loc[index, 'subject'] or 'No subject'}"
                f" — "
                f"{filtered_df.loc[index, 'sender'] or 'Unknown sender'}"
            ),
        )

        selected_email = filtered_df.loc[selected_index]

        email_id = selected_email["email_id"]
        current_status = selected_email["review_status"]

        st.write("Sender:", selected_email["sender"])
        st.write("Subject:", selected_email["subject"])
        st.write("Category:", selected_email["category"])
        st.write("Current Review Status:", current_status)
        st.write("Email ID:", email_id)

        # Select the current status by default
        if current_status not in ALLOWED_REVIEW_STATUSES:
            current_status = "Pending Review"

        selected_status = st.selectbox(
            "Update review status",
            options=ALLOWED_REVIEW_STATUSES,
            index=ALLOWED_REVIEW_STATUSES.index(current_status),
            key=f"status_{email_id}",
        )

        if st.button(
            "Save Status",
            key=f"save_{email_id}",
        ):
            try:
                with st.spinner("Saving review status..."):
                    result = update_review_status(
                        email_id,
                        selected_status,
                    )

                if result.get("success"):
                    st.success(
                        f"Review status updated to "
                        f"'{result['review_status']}'."
                    )

                    st.cache_data.clear()
                    st.rerun()

                else:
                    st.error(
                        "The API did not confirm the status update."
                    )

            except requests.exceptions.HTTPError as error:
                st.error(
                    f"API error while updating status: "
                    f"{error.response.status_code} - "
                    f"{error.response.text}"
                )

            except requests.exceptions.Timeout:
                st.error(
                    "The status update timed out. "
                    "Refresh the data to check whether it was saved."
                )

            except requests.exceptions.RequestException as error:
                st.error(
                    f"Unable to update review status: {error}"
                )

        st.text_area(
            "Email Body",
            value=selected_email["body"],
            height=200,
            disabled=True,
        )


st.caption("Data source: deployed FastAPI service")
