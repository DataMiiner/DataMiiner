from flask import Flask, render_template, request, Response, send_file,session
import yfinance as yf
import pandas as pd
import requests
#import os
import io
from io import StringIO
#from io import BytesIO
from pandas.errors import ParserError
import csv



app = Flask(__name__)


# Set a secret key for your Flask application
app.secret_key = 'your_secret_key_here'
file_name=""
temp="not"
data_available = False

data_categories = {
    'Demographic Data': ['Population Data', 'Gender Data', 'Age Distribution Data'],
    'Financial Data': ['Stock Data', 'Economic Data', 'Inflation Rate', 'Interest Rate', 'GDP of Country', 'Poverty Rate Data', 'Housing Market Data'],
    'Educational Data': ['Literacy Rate', 'Dropout Rate', 'Educational Spending', 'Education Qualification', 'Higher Education Enrollment'],
    'Energy Data': ['Energy Prices', 'Electicity Consumption', 'Nuclear Energy'],
    'Natural Calamity Data': ['Earthquakes', 'Tsunamis', 'Volcanic Eruption', 'Drought'],
    'Country data':["Country's Capital"],
    'Criminal Data': [],
    'Tourism Data': [],
    'News Headlines': [],
    'Health':[]
}

@app.route('/')
def index():
    return render_template('index.html', data_categories=data_categories.keys())

@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/process_data', methods=['POST'])
def process_data():
    selected_category = request.form.get('data_category')
    selected_sub_category = request.form.get('sub_data_category')
    global file_name
    global temp
    global data_available
    # Clear the session data after sending the CSV
    session.clear()
    #stock data----------------------------------------------------------
    if selected_sub_category == 'Stock Data':
        
        stock_name = request.form.get('stock_name')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        file_name=stock_name
        temp=stock_name
        try:
            # Fetch stock data using Yahoo Finance API
            stock_data = yf.download(stock_name, start=start_date, end=end_date)

            # Convert the stock data to CSV format and store it in a variable
            csv_data = stock_data.to_csv(index=True)

            # Store the CSV  data in the session for later retrieval
            session['csv_data'] = csv_data
            # Add a notification message
            notification = "Data has been successfully exported to CSV."
            print("Notification:", notification)
            return render_template('index.html', csv_data=csv_data)
        except Exception as e:
            return str(e)
     
    #--------------------------Population Data------------------------------------    
    elif selected_sub_category == 'Population Data':
            
         file_name="Population Data"
         def get_all_country_populations():
            url = 'https://restcountries.com/v2/all'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                populations = {country['name']: country['population'] for country in data}
                return populations
            else:
                print("Failed to retrieve population data for all countries")
                return None
 
        # Example usage:
         all_populations = get_all_country_populations()

         if all_populations is not None:
            csv_data = "Country,Population\n"
            for country, population in all_populations.items():
                csv_data += f"{country},{population}\n"

            # Optionally, you can save the CSV data to a file.
            with open('country_populations.csv', 'w', newline='') as csv_file:
                csv_file.write(csv_data)
          # Store the CSV  data in the session for later retrieval
            session['csv_data'] = csv_data
            notification = "Data has been successfully exported to CSV."
            print("Notification:", notification)
            
            return render_template('index.html', csv_data=csv_data)
     #-----------------------------------------Earthquakes-----------------       
        
    elif selected_sub_category == 'Earthquakes':
            
            file_name="Earthquakes" 
                    # Define the USGS Earthquake API endpoint URL
            api_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

            # Define API parameters (customize as needed)
            params = {
                'format': 'geojson',  # Data format (GeoJSON)
                'starttime': '2021-01-01',
                'endtime': '2023-06-14',
                'minmagnitude': 7.0,  # Minimum earthquake magnitude
                'eventtype': 'earthquake',  # Event type (earthquake)
                'orderby': 'time'  # Order by time
            }

            # Send an HTTP GET request to fetch earthquake data
            response = requests.get(api_url, params=params)

            if response.status_code == 200:
                # Convert the response JSON to a Pandas DataFrame
                data = response.json()
                
                # Extract relevant data fields from the JSON
                earthquake_data = pd.DataFrame(data['features'])
                
                # Process and analyze the data as needed
                earthquake_data['Magnitude'] = earthquake_data['properties'].apply(lambda x: x['mag'])
                earthquake_data['Location'] = earthquake_data['properties'].apply(lambda x: x['place'])
                earthquake_data['Coordinates'] = earthquake_data['geometry'].apply(lambda x: x['coordinates'])
                earthquake_data['Date'] = earthquake_data['properties'].apply(lambda x: pd.Timestamp(x['time']))
                
                # Select and reorder columns
                earthquake_data = earthquake_data[['Date', 'Magnitude', 'Location', 'Coordinates']]
                
                # Convert the data to a CSV file
                csv_data = earthquake_data.to_csv(index=False)
                
                # Save the CSV data to a variable
                csv_file = "earthquake_data.csv"
                with open(csv_file, 'w') as f:
                    f.write(csv_data)
                # Store the CSV  data in the session for later retrieval
            session['csv_data'] = csv_data
            notification = "Data has been successfully exported to CSV."
            print("Notification:", notification)
            return render_template('index.html', csv_data=csv_data)    
    #-----------------------------------------Inflation Rate-----------------       
        
    elif selected_sub_category == 'Inflation Rate':
            
        file_name="Inflation Rate"   
            # Define the World Bank API URL for India's inflation rate (CPI)
        api_url = "https://api.worldbank.org/v2/country/IND/indicator/FP.CPI.TOTL.ZG?format=json"

        try:
            # Send an HTTP GET request to fetch the data
            response = requests.get(api_url)

            if response.status_code == 200:
                # Convert the response JSON to a Pandas DataFrame
                data = response.json()[1]  # The actual data is in the second element of the JSON response
                df = pd.DataFrame(data)

                # Filter and process the data as needed
                # For example, you can rename columns:
                df = df.rename(columns={'value': 'InflationRate', 'date': 'Year'})

                # Convert the DataFrame to CSV format and store it in the 'csv_data' variable
                csv_data = df.to_csv(index=False)

            else:
                print(f'Failed to retrieve data. Status Code: {response.status_code}')

        except Exception as e:
            print(f'Error: {e}')

        # Store the CSV  data in the session for later retrieval
        session['csv_data'] = csv_data
        notification = "Data has been successfully exported to CSV."
        print("Notification:", notification)
        return render_template('index.html', csv_data=csv_data) 
       
        #--------------------------Country's Capital------------------------------------    
    elif selected_sub_category == "Country's Capital":
            
        file_name="Country's Capital"
                 
                 
    return render_template('index.html')



#csv and excel download link
@app.route('/download_csv')
def download_csv():
    csv_data = session.get('csv_data', '')
  

    if csv_data:
        response = Response(csv_data, content_type='text/csv')
        response.headers['Content-Disposition'] = f'attachment; filename={file_name}.csv'
        
        
        return response
    else:
        return "Collecting Data............."
@app.route('/download_excel')
def download_excel():
    if file_name==temp:
        csv_data = session.get('csv_data', '')

        if csv_data:
            # Read the CSV data from the session using 'io.StringIO'
            df = pd.read_csv(io.StringIO(csv_data))

            # Create a BytesIO object to store the Excel file
            excel_file = io.BytesIO()

            # Write the DataFrame to an Excel file
            with pd.ExcelWriter(excel_file, engine='xlsxwriter', mode='xlsx', datetime_format='yyyy-mm-dd') as writer:
                df.to_excel(writer, sheet_name='Sheet1', index=False)

            # Seek to the beginning of the BytesIO object
            excel_file.seek(0)

            # Serve the Excel file for download
            response = Response(excel_file.read())
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename={file_name}.xlsx'
            session.clear()
            return response
        else:
            return "Collecting Data............."
        
    else:
        csv_data = session.get('csv_data', '')

        if csv_data:
            try:
                # Read the CSV data from the session using 'io.StringIO' and create a DataFrame
                df = pd.read_csv(io.StringIO(csv_data))
            except ParserError as e:
                
                 # Handle the parsing error by filtering out problematic rows
                lines = csv_data.strip().split('\n')
                header_row = lines[0]  # Assuming the first row is the header
                num_columns = len(header_row.split(','))  # Detect the number of columns

                valid_lines = [line for line in lines if len(line.split(',')) == num_columns]
                df = pd.read_csv(io.StringIO('\n'.join(valid_lines)))
                
            # Create an Excel file
            excel_data = io.BytesIO()
            with pd.ExcelWriter(excel_data, engine='xlsxwriter') as excel_writer:
                df.to_excel(excel_writer, sheet_name=f"{file_name}", index=False)

            excel_data.seek(0)

            response = Response(excel_data.read())
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response.headers['Content-Disposition'] = f'attachment; filename={file_name}.xlsx'
             # Clean the buffer and close it
            excel_data.close()
            session.clear()
            
            return response
            
        else:
            return "Collecting Data............."
                

@app.route('/clear_session')
def clear_session():
    session.clear()
    return "Session cleared"






@app.route('/get_subcategories', methods=['POST'])
def get_subcategories():
    selected_category = request.form.get('data_category')
    sub_categories = data_categories.get(selected_category, [])
    return {'sub_categories': sub_categories}


if __name__ == '__main__':
    app.secret_key = 'your_secret_key_here'
    app.run(debug=True)
    