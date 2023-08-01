
# Documentation for Logio App
The Logio App is a dashboard application built using the Dash framework to visualize and analyze data related to manufacturing and logistics processes. It provides insights into manufacturing costs, production quantities, and transportation of components between different plants.

## Purpose
The main purpose of the Logio App is to help users understand and optimize manufacturing and transportation processes within a company. The app uses input data files, processes the data, and presents it in interactive graphs and tables. Users can filter data based on date ranges and select specific production plants to focus on.

## Requirements
To run the Logio App, you need the following libraries and dependencies:

Python 3
Dash library
Dash Bootstrap Components library
Plotly Express library
NumPy library
Pandas library

## Data Sources
The Logio App reads data from the following CSV and TXT files:

dodavatele.csv: Supplier data.
dodavky.csv: Supply data.
komponenty.csv: Component data.
pohyby.csv: Movement data.
produkty.csv: Product data.
sklady.csv: Warehouse data.
stav_skladu_08_2018.csv: Warehouse status data (as of August 2018).
zavody.csv: Plant data.
matice_vyroby.txt: Manufacturing matrix data.
vyroba.txt: Production data.

## Data Processing
The app performs several data processing functions before displaying the data on the dashboard:

read_data(file): Reads data from the given file name and returns it as a Pandas DataFrame. The function uses different separators (',' or '\t') based on the number of columns in the data. \\
get_product_price(produkty, matice_vyroby, komponenty): Calculates the manufacturing cost for each product based on its components and prices of components.\\
get_production_costs(produkty_all, vyroba): Calculates the manufacturing cost for manufactured products by multiplying the manufacturing cost of each product by the quantity manufactured.
get_transport(pohyby): Calculates the distance between plants for component transport.
Dashboard Layout
The dashboard layout consists of the following components:

Sidebar: It contains filters for date range, plant selection, and an input field for the cost per kilometer.
Table: Displays a table of production data based on the selected date range.
Bar Chart: Shows the production quantities of products in the selected plant.
Bar Chart: Shows the transportation details of components to the selected plant, including the transported weight and estimated transportation cost.
App Execution
To run the Logio App, execute the script containing the code. The app will be launched, and the dashboard can be accessed through the local server at http://127.0.0.1:8050/.
The application was deployed using https://dashboard.render.com/. Application can be launched as stand-alone API on https://logio-ukol-marzova-2023.onrender.com/.

## Usage
Select a date range in the sidebar using the date picker to filter the production data.
Use the dropdown in the sidebar to select a specific production plant.
Enter the cost per kilometer in the input field to estimate the transportation cost.
The table will display the filtered production data based on the selected date range.
The bar chart will show the production quantities of products in the selected plant.
The second bar chart will show the transportation details of components to the selected plant.

## Conclusion
The Logio App provides valuable insights into manufacturing and transportation processes, enabling users to optimize production and logistics for cost-effective operations. By visualizing the data, users can make informed decisions to improve efficiency and reduce manufacturing and transportation costs.
