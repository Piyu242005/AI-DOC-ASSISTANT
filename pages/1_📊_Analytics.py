import plotly.express as px
import streamlit as st

from services.db_manager import DBManager

st.set_page_config(
    page_title="Analytics - NeuraFlow AI",
    page_icon="📊",
    layout="wide",
)

st.title("📈 NeuraFlow Analytics")
st.write("Real-time telemetry and performance metrics for the Enterprise RAG Platform.")

db = DBManager()

# --- Top-Level Metrics ---
st.subheader("System Performance")

col1, col2, col3, col4 = st.columns(4)

total_queries = db.get_total_queries()
col1.metric("🧠 Total Queries", total_queries)

avg_latency = db.get_average_latency()
col2.metric("⚡ Average Latency", f"{avg_latency:.2f}s")

fallback_rate = db.get_fallback_rate()
col3.metric("🔄 Fallback Rate", f"{fallback_rate:.1f}%")

provider_avail = db.get_provider_availability()
col4.metric("📡 Provider Availability", f"{provider_avail:.1f}%")


st.divider()
st.subheader("RAG & Document Intelligence")

col5, col6, col7, col8 = st.columns(4)

docs_indexed = db.get_documents_indexed()
col5.metric("📄 Documents Indexed", docs_indexed)

total_chunks = db.get_total_chunks()
col6.metric("💾 Vector Count (Chunks)", total_chunks)

avg_sim = db.get_average_similarity()
col7.metric("🎯 Avg Similarity Score", f"{avg_sim:.2f}")

# Average RAG Retrieval Time
rag_df = db.get_rag_performance_df()
avg_rag_time = rag_df["rag_time"].mean() if not rag_df.empty else 0.0
col8.metric("🔍 Avg Retrieval Time", f"{avg_rag_time:.2f}s")


st.divider()
st.subheader("Conversation Memory")

col9, col10, col11 = st.columns(3)

memory_hits, memory_tokens, memory_turns = db.get_memory_stats()
col9.metric("🗣️ Memory Hits", memory_hits)
col10.metric("🧩 Avg Context Size", f"{memory_tokens} tokens")
col11.metric("🔁 Avg Chat Length", f"{memory_turns} turns")

st.divider()
st.subheader("Real-Time Streaming Performance")

col12, col13, col14 = st.columns(3)

avg_first_token, avg_tps, stream_success_rate = db.get_streaming_stats()
col12.metric("⚡ Avg First Token Time", f"{avg_first_token}s")
col13.metric("🚀 Avg Tokens / Second", avg_tps)
col14.metric("📊 Stream Success Rate", f"{stream_success_rate}%")

st.divider()

# --- Charts ---
st.subheader("Interactive Analytics")

if total_queries == 0:
    st.info("Not enough data yet. Ask some questions on the main app to see charts!")
else:
    c1, c2 = st.columns(2)

    with c1:
        # Provider Usage
        st.write("**Provider Usage Distribution**")
        df_usage = db.get_provider_usage_df()
        fig_usage = px.bar(
            df_usage,
            x="count",
            y="provider",
            orientation="h",
            color="provider",
            labels={"count": "Number of Queries", "provider": "AI Provider"},
        )
        fig_usage.update_layout(showlegend=False)
        st.plotly_chart(fig_usage, use_container_width=True)

    with c2:
        # Latency Comparison
        st.write("**Latency Comparison by Provider**")
        df_latency = db.get_latency_comparison_df()
        fig_latency = px.bar(
            df_latency,
            x="provider",
            y="avg_latency",
            color="provider",
            labels={"avg_latency": "Average Latency (s)", "provider": "AI Provider"},
        )
        fig_latency.update_layout(showlegend=False)
        st.plotly_chart(fig_latency, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        # Query Volume Over Time
        st.write("**Query Volume Over Time**")
        df_volume = db.get_query_volume_df()
        fig_volume = px.line(
            df_volume,
            x="date",
            y="count",
            markers=True,
            labels={"count": "Queries per Day", "date": "Date"},
        )
        st.plotly_chart(fig_volume, use_container_width=True)

    with c4:
        # RAG Performance
        st.write("**RAG Retrieval Time Distribution**")
        fig_rag = px.histogram(
            rag_df,
            x="rag_time",
            nbins=10,
            labels={"rag_time": "Retrieval Time (seconds)"},
        )
        fig_rag.update_layout(bargap=0.1)
        st.plotly_chart(fig_rag, use_container_width=True)
