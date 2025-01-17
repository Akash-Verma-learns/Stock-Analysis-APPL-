import yfinance as yf
import pandas as pd
import streamlit as st

# Function to download stock data
def download_stock_data(ticker):
    try:
        data = yf.download(ticker, period="1y", interval="1d")
        if data.empty:
            raise ValueError("No data found for the specified ticker.")
        return data
    except Exception as e:
        st.error(f"Error downloading data: {e}")
        return None

# Feature engineering function
def feature_engineering(data):
    try:
        # Ensure the 'Close' column exists
        if 'Close' not in data.columns:
            raise ValueError("The 'Close' column is missing from the data.")

        # Calculate the 20-period Simple Moving Average (SMA)
        data['SMA_20'] = data['Close'].rolling(window=20, min_periods=1).mean()
        data["rolling_std"] = data['Close'].rolling(window=20, min_periods=1).std()
        data['Bollinger_High'] = data['SMA_20'] + (2 * data["rolling_std"])
        data['Bollinger_Low'] = data['SMA_20'] - (2 * data["rolling_std"])

        # Calculate Z-Score only when no NaN values are present
        for index, row in data.iterrows():
            # Check if any value in the row is NaN
            if row[['Close', 'SMA_20', 'rolling_std']].isna().any():
                continue  # Skip this row if any NaN is found
            else:
                # Make sure we are assigning a scalar value to the column
                data.at[index, 'Z-Score'] = (row['Close'] - row['SMA_20']) / row['rolling_std']

        # Drop rows with NaN values caused by insufficient data
        

        return data

    except Exception as e:
        st.error(f"Error in feature engineering: {e}")
        return None

# Streamlit dashboard function
def streamlit_dashboard():
    st.title("Stock Data Analysis with Technical Indicators")

    # Input for stock ticker
    ticker = st.text_input('Enter Stock Ticker (e.g., AAPL):', 'AAPL')

    if st.button("Fetch Data"):
        # Download stock data
        data = download_stock_data(ticker)
        if data is not None:
            # Perform feature engineering
            data = feature_engineering(data)
            if data is not None:
                # Reset index to avoid any multi-index issues
                data.reset_index(inplace=True)

                # Display data and charts
                st.write(data.tail())
                st.write("Basic Statistics:")
                st.write(data.describe())  # Display summary statistics for the data

                # Display the latest stock information
                latest_data = data.iloc[-1]  # Get the last row of data
                st.write(f"Latest data for {ticker}:")
                st.write(latest_data)

                # Provide an option to download the data as a CSV file
                st.download_button(
                    label="Download CSV",
                    data=data.to_csv().encode('utf-8'),
                    file_name=f"{ticker}_stock_data.csv",
                    mime="text/csv"
                )
                

# Run the Streamlit app
if __name__ == "__main__":
    streamlit_dashboard()
