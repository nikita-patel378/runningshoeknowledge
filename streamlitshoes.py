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
    st.title("Running Shoe Knowledge Assistant")
    st.write(
        "This app provides shoe suggestions for neutral road runners based on a few characteristics. If you need a "
        "stability shoe, scroll down to learn about the brands and there will be atleast one suggestion from each "
        "brand.")

    # Disclaimer
    st.markdown(
        """
        **Disclaimer:** I am not a medical professional. If you are experiencing pain or discomfort while running, 
        please consult with a qualified healthcare provider or medical professional for personalized advice.
        """
    )

    st.subheader("General Running Shoe Guidance")
    # cushioning
    with st.expander("What type of cushioning should you look for?"):
        st.write(
            """If pushing for more distance, max cushioning can be beneficial while training. For race day, 
            you can consider a lighter cushioning shoe. Max cushioning will absorb impact on the ground while less 
            cushioning will be more responsive when running. Hoka’s website mentions this on their cushioning scale."""
        )

    # multiple pairs of running shoes
    with st.expander("Should you have multiple pairs of running shoes?"):
        st.write(
            """
            For half marathons and marathons, having training shoes and having race day shoes can be beneficial. 
            This lessens the risk of your shoes wearing out during your race. 
            You can also consider a carbon-plated shoe for your race day shoe.
            """
        )

    # running during wet weather season
    with st.expander("What shoes should you pick during rainy/wet weather?"):
        st.write(
            """
            Look for shoes that are labeled as GTX or Gore-Tex. These shoes are designed to be water-resistant or waterproof, 
            making them suitable for wet weather conditions.
            """
        )

    st.markdown("---")
    # Step 1: Striker Type
    striker_type = st.selectbox(
        "Are you a heel striker or a mid/forefoot striker?",
        ["", "Heel Striker", "Mid/Forefoot Striker"],  # Add a blank option
        format_func=lambda x: "Select an option" if x == "" else x  # Placeholder text
    )

    if striker_type == "Heel Striker":
        st.write("You will benefit from a higher offset shoe.")
    elif striker_type == "Mid/Forefoot Striker":
        st.write("You will benefit from a lower offset shoe.")

    st.markdown("---")

    # Step 2: Pain Guidance
    pain = st.selectbox(
        "Do you have any pain while running?",
        ["", "Knees", "Ankles", "None"],  # Add a blank option
        format_func=lambda x: "Select an option" if x == "" else x  # Placeholder text
    )

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
        ["", "8mm and higher", "8mm and lower"],  # Add a blank option
        format_func=lambda x: "Select an option" if x == "" else x  # Placeholder text
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
    brand = st.selectbox(
        "Select a brand to learn more about it:",
        ["", "Saucony", "Brooks", "Hoka", "Nike", "On", "Asics", "New Balance"],  # Add a blank option
        format_func=lambda x: "Select a brand" if x == "" else x  # Placeholder text
    )

    if brand:
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


