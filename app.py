
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from src.database import init_db, get_polls, get_poll, create_poll, vote, get_results, get_total_votes, get_recent_votes, delete_poll
from src.utils import export_poll_csv, export_poll_json, make_vote_token

st.set_page_config(page_title="Real-Time Polling Dashboard", page_icon="📊", layout="wide")
init_db()

st.markdown("""
<style>
.main-header{font-size:2.3rem;font-weight:800;margin-bottom:.2rem}
.subtle{color:#64748b}
.metric-card{padding:18px;border:1px solid #e2e8f0;border-radius:14px;background:#fff}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 Real-Time Polling Dashboard</div>', unsafe_allow_html=True)
st.caption("Create live polls, collect votes, visualize results instantly, and export analytics.")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to", ["Live Polls", "Create Poll", "Analytics", "Admin"])
    st.divider()
    st.caption("Data is stored locally in SQLite.")
    if st.button("🔄 Refresh data", use_container_width=True):
        st.rerun()

if page == "Live Polls":
    polls = get_polls(active_only=True)
    if not polls:
        st.info("No active polls yet. Create one from the Create Poll page.")
    else:
        for p in polls:
            with st.container(border=True):
                st.subheader(p["question"])
                st.caption(f"Poll ID: {p['id']} • Created: {p['created_at']} • {p['total_votes']} votes")
                cols = st.columns(min(len(p["options"]), 4))
                for i, option in enumerate(p["options"]):
                    with cols[i % len(cols)]:
                        if st.button(f"Vote: {option}", key=f"vote_{p['id']}_{i}", use_container_width=True):
                            token = make_vote_token()
                            ok, msg = vote(p["id"], option, token)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                result = get_results(p["id"])
                if result:
                    df = pd.DataFrame(result)
                    fig = px.bar(df, x="option", y="votes", text="votes", title="Current Results")
                    fig.update_layout(height=330, margin=dict(l=20,r=20,t=50,b=20))
                    st.plotly_chart(fig, use_container_width=True)

elif page == "Create Poll":
    st.header("➕ Create a Poll")
    with st.form("create_poll"):
        question = st.text_input("Question", placeholder="Which technology should we learn next?")
        count = st.number_input("Number of options", min_value=2, max_value=10, value=4)
        options = []
        for i in range(int(count)):
            options.append(st.text_input(f"Option {i+1}", key=f"new_option_{i}", placeholder=f"Option {i+1}"))
        submitted = st.form_submit_button("Create Poll", type="primary")
        if submitted:
            clean = [x.strip() for x in options if x.strip()]
            if not question.strip():
                st.error("Question is required.")
            elif len(clean) < 2 or len(set(x.lower() for x in clean)) != len(clean):
                st.error("Enter at least two unique options.")
            else:
                pid = create_poll(question.strip(), clean)
                st.success(f"Poll #{pid} created successfully.")
                st.rerun()

elif page == "Analytics":
    st.header("📈 Analytics")
    polls = get_polls(active_only=False)
    total_polls = len(polls)
    total_votes = get_total_votes()
    active = sum(1 for p in polls if p["active"])
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Polls", total_polls)
    c2.metric("Total Votes", total_votes)
    c3.metric("Active Polls", active)
    if polls:
        selected = st.selectbox("Select poll", [f"{p['id']} — {p['question']}" for p in polls])
        pid = int(selected.split(" — ",1)[0])
        result = get_results(pid)
        df = pd.DataFrame(result)
        if not df.empty:
            df["percentage"] = (df["votes"] / max(df["votes"].sum(),1) * 100).round(1)
            left,right = st.columns(2)
            with left:
                fig = px.pie(df, names="option", values="votes", hole=.45, title="Vote Distribution")
                st.plotly_chart(fig, use_container_width=True)
            with right:
                fig = px.bar(df, x="option", y="percentage", text="percentage", title="Percentage")
                fig.update_traces(texttemplate="%{text}%", textposition="outside")
                st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
            col1,col2 = st.columns(2)
            col1.download_button("⬇️ Export CSV", export_poll_csv(pid), f"poll_{pid}_results.csv", "text/csv", use_container_width=True)
            col2.download_button("⬇️ Export JSON", export_poll_json(pid), f"poll_{pid}_results.json", "application/json", use_container_width=True)
        else:
            st.info("No votes recorded yet.")

elif page == "Admin":
    st.header("🛠️ Admin Panel")
    st.warning("This demo admin panel is local-only. Add authentication before deploying publicly.")
    polls = get_polls(active_only=False)
    if not polls:
        st.info("No polls available.")
    for p in polls:
        with st.container(border=True):
            c1,c2,c3 = st.columns([5,1,1])
            c1.write(f"**#{p['id']} — {p['question']}**")
            c1.caption(f"{p['total_votes']} votes • Active: {p['active']}")
            if c2.button("📥 CSV", key=f"csv_{p['id']}"):
                st.download_button("Download", export_poll_csv(p["id"]), f"poll_{p['id']}.csv", key=f"dlcsv_{p['id']}")
            if c3.button("🗑️ Delete", key=f"del_{p['id']}"):
                delete_poll(p["id"])
                st.success("Poll deleted.")
                st.rerun()
    st.subheader("Recent Votes")
    recent = get_recent_votes(50)
    if recent:
        st.dataframe(pd.DataFrame(recent), use_container_width=True, hide_index=True)
    else:
        st.info("No votes yet.")
