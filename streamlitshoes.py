import streamlit as st
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='dot.env')
NEO4J_URL = os.getenv("NEO4J_URL")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Establish connection to Neo4j
driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


def query_neo4j(cypher_query):
    with driver.session() as session:
        result = session.run(cypher_query)
        return [record.data() for record in result]


def main():
    st.title("Running Shoe Knowledge Graph Assistant")

    # Step 1: Striker Type
    striker_type = st.selectbox(
        "Are you a heel striker or a mid/forefoot striker?",
        ["Heel Striker", "Mid/Forefoot Striker"]
    )

    if striker_type == "Heel Striker":
        st.write("You will benefit from a higher offset shoe.")
    elif striker_type == "Mid/Forefoot Striker":
        st.write("You will benefit from a lower offset shoe.")

    st.markdown("---")

    # Step 2: Pain Guidance
    pain = st.selectbox("Do you have any pain while running?", ["Knees", "Ankles", "None"])

    if pain == "Knees":
        st.write("Try a shoe with a lower offset. Start with decreasing the offset by 2mm.")
        st.markdown(
            "[Learn more about heel-to-toe drop](https://www.zappos.com/c/what-is-heel-to-toe-drop#:~:text=%E2%80"
            "%9CIn%20general%2C%20a%20shoe%20with,stress%20on%20the%20lower%20leg.%22)"
        )
    elif pain == "Ankles":
        st.write("Try a shoe with a higher offset. Start with increasing the offset by 2mm.")
        st.markdown(
            "[Learn more about heel-to-toe drop](https://www.zappos.com/c/what-is-heel-to-toe-drop#:~:text=%E2%80"
            "%9CIn%20general%2C%20a%20shoe%20with,stress%20on%20the%20lower%20leg.%22)"
        )

    st.markdown("---")

    # Step 3: Offset Queries
    offset_query = st.selectbox(
        "Do you want to see shoes with offset of 8mm and higher or 8mm and lower?",
        ["8mm and higher", "8mm and lower"]
    )

    if offset_query == "8mm and higher":
        query = """
            MATCH (s:Shoe)-[:HAS_OFFSET]->(o:Offset), (s)-[:HAS_BRAND]->(b:Brand)
            WHERE toFloat(substring(o.offsetValue, 0, size(o.offsetValue) - 2)) >= 8
            RETURN s.name AS Shoe, o.offsetValue AS Offset, b.brandName AS Brand
        """
        results = query_neo4j(query)
        st.write("Shoes with offset 8mm and higher:")
        st.write(results)

    elif offset_query == "8mm and lower":
        query = """
            MATCH (s:Shoe)-[:HAS_OFFSET]->(o:Offset), (s)-[:HAS_BRAND]->(b:Brand)
            WHERE toFloat(substring(o.offsetValue, 0, size(o.offsetValue) - 2)) <= 8
            RETURN s.name AS Shoe, o.offsetValue AS Offset, b.brandName AS Brand
        """
        results = query_neo4j(query)
        st.write("Shoes with offset 8mm and lower:")
        st.write(results)

    st.markdown("---")

    # Step 4: Brand Details
    brand = st.selectbox("Select a brand to learn more about it:", ["Saucony", "Brooks", "Hoka", "Nike", "On", "Asics",
                                                                    "New Balance"])

    query = f"""
        MATCH (b:Brand {{brandName: '{brand}'}})
        RETURN b.notesBrand AS Notes
    """
    results = query_neo4j(query)
    st.write(f"About {brand}:")
    if results:
        st.write(results[0]['Notes'])
    else:
        st.write("No details found for this brand.")

    st.markdown("---")

    # Step 5: Carbon-Plated Shoes
    if st.checkbox("Show me all carbon-plated shoes"):
        query = """
            MATCH (s:Shoe)-[:HAS_BRAND]->(b:Brand)
            WHERE s.isCarbonPlated = True
            RETURN s.name AS ShoeName, b.brandName AS BrandName
        """
        results = query_neo4j(query)
        st.write("Carbon-plated shoes:")
        st.write(results)


if __name__ == "__main__":
    main()
