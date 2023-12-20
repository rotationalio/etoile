import json
import pandas as pd
import asyncio
from argparse import ArgumentParser

import streamlit as st
import altair as alt

from etoile.subscriber import TrafficSubscriber

async def app(subscriber):
    st.title("Traffic Analytics")

    # Query historical data
    days = await subscriber.daily_counts()
    print(days)
    df = pd.DataFrame(days, columns=["day", "vehicles_per_day"])
    daily_bar = alt.Chart(df).mark_bar().encode(
        x="day",
        y="vehicles_per_day",
    ).properties(
        width=800,
        height=400,
    )
    daily_row = st.empty()
    daily_row.altair_chart(daily_bar, use_container_width=True)

    # Real-time updates
    rate_row = st.empty()
    df = pd.DataFrame(columns=["ts", "vehicles_per_minute"])
    async for now, rate in subscriber.updates():
        df = pd.concat([df, pd.DataFrame([[now, rate]], columns=["ts", "vehicles_per_minute"])])
        c = alt.Chart(df).mark_line().encode(
            x="ts",
            y="vehicles_per_minute",
        ).properties(
            width=800,
            height=400,
        )
        rate_row.altair_chart(c, use_container_width=True)

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Demo app that subscribes to real-time traffic updates and displays a real-time dashboard."
    )
    parser.add_argument(
        "-t",
        "--topic",
        default="figure-updates-json",
        help="Ensign topic to subscribe to",
    )
    parser.add_argument(
        "-c",
        "--cred-path",
        default="",
        help="Path to Ensign credentials",
        required=True,
    )

    subscriber = TrafficSubscriber(**vars(parser.parse_args()))
    asyncio.run(app(subscriber))