import pandas as pd
import asyncio
from argparse import ArgumentParser

import streamlit as st
import altair as alt

from etoile.subscriber import TrafficSubscriber

def create_layout():
    st.title("Real-Time Traffic Analytics")
    
    st.header("Live Video Stream")
    img_stream = st.empty()

    st.header("Traffic Rate")
    rate_chart = st.empty()

    st.header("Daily Traffic")
    daily_chart = st.empty()
    return img_stream, rate_chart, daily_chart

async def update_video_stream(img, subscriber):
    async for frame in subscriber.frames():
        img.image(frame, channels="BGR")

async def update_rate_chart(chart, subscriber):
    asyncio.create_task(subscriber.updates())
    x, y = ("time", "vehicles per second")
    df = pd.DataFrame(columns=[x, y])
    while True:
        now, rate = subscriber.vehicle_rate()
        df = pd.concat([df, pd.DataFrame([[now, rate]], columns=[x, y])])
        c = alt.Chart(df).mark_line().encode(
            x=x,
            y=y,
        ).properties(
            width=800,
            height=400,
        )
        chart.altair_chart(c, use_container_width=True)
        await asyncio.sleep(5)

async def update_daily_chart(chart, subscriber):
    while True:
        days = await subscriber.daily_counts()
        x,y = ("day", "total vehicles")
        df = pd.DataFrame(days, columns=[x, y])
        c = alt.Chart(df).mark_bar().encode(
            x=x,
            y=y,
        ).properties(
            width=800,
            height=400,
        )
        chart.altair_chart(c, use_container_width=True)
        await asyncio.sleep(60)

async def app(subscriber):
    img, rate, daily = create_layout()
    tasks = []
    tasks.append(asyncio.create_task(update_video_stream(img, subscriber)))
    tasks.append(asyncio.create_task(update_rate_chart(rate, subscriber)))
    tasks.append(asyncio.create_task(update_daily_chart(daily, subscriber)))
    await asyncio.gather(*tasks)

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