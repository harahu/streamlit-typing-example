from dataclasses import dataclass

import streamlit as st


@dataclass
class Pastry:
    name: str
    description: str


@dataclass
class Baker:
    name: str
    pastries: list[Pastry]


bakers = [
    Baker(
        name="Eager Bakery",
        pastries=[
            Pastry(
                name="Cinnamon Bun",
                description="The best there is",
            ),
            Pastry(
                name="Magic Muffin",
                description="Putting sparkles back in your day.",
            ),
            Pastry(
                name="Dreamy Donut",
                description="Never drink your coffee without it.",
            ),
        ],
    ),
    Baker(
        name="Lazy Bakin'",
        pastries=[],
    ),
]

baker = st.sidebar.selectbox(
    label="Select a bakery:",
    options=bakers,
    format_func=lambda b: b.name,
)

pastry = st.sidebar.selectbox(
    label=f"Select one of {baker.name}'s pastries:",
    options=baker.pastries,
    format_func=lambda p: p.name,
)
st.write(pastry.name)
st.write(pastry.description)
