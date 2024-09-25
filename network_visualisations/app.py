import streamlit as st
import pandas as pd
import os
from pyvis.network import Network
import random

st.set_page_config(layout="wide")

st.title("Elektronikus Közbeszerzési Rendszer (EKR) hálózati vizualizáció")

# File selector
csv_folder = "data_exports" 
csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]
selected_file = st.selectbox("Select a CSV file", csv_files)

if selected_file:
    # Load the selected CSV file
    data = pd.read_csv(os.path.join(csv_folder, selected_file))
    data = data[['Eljárás EKR azonosító', 'Ajánlatkérő szervezet neve - tisztított', 'Nyertes ajánlattevő neve - tisztított']]
    data.columns = ['EKR azonosító', 'Ajánlatkérő', 'Nyertes']
    data.drop_duplicates(inplace=True)
    # Function to generate a random color
    def random_color():
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))
    # Create a pyvis network
    net = Network(height="800px", width="100%", bgcolor="#FFFFFF", font_color="black")

    # Add nodes
    ajanlatkero_set = set(data['Ajánlatkérő'])
    nyertes_set = set(data['Nyertes'])

    for ajanlatkero in ajanlatkero_set:
        net.add_node(ajanlatkero, label=ajanlatkero, color='#dd4b39', title=f"Ajánlatkérő: {ajanlatkero}")

    for nyertes in nyertes_set:
        net.add_node(nyertes, label=nyertes, color='#162347', title=f"Nyertes: {nyertes}")

    # Add edges
    for idx, row in data.iterrows():
        edge_color = random_color()
        net.add_edge(row['Ajánlatkérő'], row['Nyertes'], title=f"EKR azonosító: {row['EKR azonosító']}", color=edge_color)

    # Set options with original physics settings
    net.set_options("""
    var options = {
    "nodes": {
        "font": {
        "size": 12
        }
    },
    "edges": {
        "color": {
        "inherit": true
        },
        "smooth": false
    },
    "physics": {
        "enabled": true,
        "barnesHut": {
        "theta": 0.5,
        "gravitationalConstant": -2000,
        "centralGravity": 0.3,
        "springLength": 200,
        "springConstant": 0.05,
        "damping": 0.09,
        "avoidOverlap": 0
        },
        "maxVelocity": 50,
        "minVelocity": 0.75,
        "solver": "barnesHut",
        "timestep": 0.5,
        "wind": { "x": 0, "y": 0 }
    },
    "interaction": {
        "dragNodes": true,
        "zoomView": true
    },
    "configure": {
        "enabled": true,
        "filter": "physics"
    }
    }
    """)


    # Save the graph to an HTML file
    net.save_graph("temp_graph.html")

    # Read the saved HTML file
    with open("temp_graph.html", "r", encoding="utf-8") as f:
        graph_html = f.read()

    # Add screenshot functionality
    screenshot_js = """
    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
    <script>
    function takeScreenshot() {
        html2canvas(document.querySelector("#graph-container")).then(canvas => {
            var img = canvas.toDataURL("image/png");
            var link = document.createElement('a');
            link.download = 'graph_screenshot.png';
            link.href = img;
            link.click();
        });
    }
    </script>
    """

    # Modify the graph HTML to include the screenshot button and functionality
    modified_html = graph_html.replace('</head>', f'{screenshot_js}</head>')
    modified_html = modified_html.replace('<body>', '<body><button onclick="takeScreenshot()">Take Screenshot</button><div id="graph-container">')
    modified_html = modified_html.replace('</body>', '</div></body>')

    # Display the graph
    st.components.v1.html(modified_html, height=850, scrolling=True)
