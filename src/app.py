import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime
from io import BytesIO
import streamlit as st
from utility import *

def load_data(file):
    # Handle different input types
    if isinstance(file, str):
        # String file path (for database files)
        file_type = file.split('.')[-1]
        if file_type == 'csv':
            return pd.read_csv(file)
        elif file_type == 'pkl':
            df = pd.read_pickle(f"src/{file}")
            return df
        elif file_type in ['xlsx', 'xls']:
            df = pd.read_excel(file, sheet_name=None)
            df_dict = {}
            for sheet_name, df_ in df.items():
                df_dict[sheet_name] = df_
            st.info(df.keys())
            return df_dict
            
    else:
        # File object from Streamlit uploader
        if hasattr(file, 'name'):
            file_type = file.name.split('.')[-1]
        else:
            file_type = 'xlsx'  # Default assumption for uploaded files
        
        if file_type in ['xlsx', 'xls']:
            df = pd.read_excel(file, sheet_name=None)
            df_dict = {}
            for sheet_name, df_ in df.items():
                df_dict[sheet_name] = df_
            st.info(df.keys())
            return df_dict
        elif file_type == 'pkl':
            df = pd.read_pickle(f"src/{file}")
            return df
        elif file_type == 'csv':
            return pd.read_csv(file)


def save_data(df):
    df.to_pickle('src/kunmings.pkl')

def create_color_key(df,color_map):
    df['Color Key'] = df.Color.map(lambda x: color_map[x] if x in color_map else '')
    return df

def create_bucket(df,stock_bucket=stock_bucket):
    """
    df : Monthly Stock Data Sheet
    stock_bucket : Dictionary containing bucket ranges
    """
    for key , values in stock_bucket.items():
        lower_bound , upper_bound = values
        index = df[(df['Weight']>=lower_bound) & (df['Weight']<upper_bound)].index.tolist()
        df.loc[index,'Buckets'] = key
    return df

def calculate_avg(df):
    """
    df : Monthly Stock Data Sheet
    """
    df['avg'] = df['Weight'] * df['Average\nCost\n(USD)']
    return df

def create_date_join(df):
    """
    df : Monthly Stock Data Sheet
    """
    df['Month'] = pd.to_datetime('today').month_name()
    df['Year'] = pd.to_datetime('today').year
    df['Join'] = df['Month'].astype(str) + '-' + df['Year'].map(lambda x: x-2000).astype(str)
    return df

def concatenate_first_two_rows(df):
    result = {}
    for col in df.columns:
        value1 = str(df.iloc[0][col])
        value2 = str(df.iloc[1][col])
        result[col] = f"{value1}_{value2}"
    return result

def populate_max_qty(df,MONTHLY_STOCK_DATA):
    """
    df : Max Qty Sheet
    MONTHLY_STOCK_DATA : Monthly Stock Data Sheet
    """
    columns=list(concatenate_first_two_rows(df.iloc[0:2,2:]).values())
    columns = ['Months','Buckets'] + columns
    df.columns = columns
    df=df.iloc[2:,:]
    df.reset_index(drop=True,inplace=True)
    _MAX_QTY_ = []
    MONTHLY_STOCK_DATA['Max Qty'] = None
    for indx, row in MONTHLY_STOCK_DATA.iterrows():
        join = row['Join']
        Shape = row['Shape key']
        Color = row['Color Key']
        Bucket = row['Buckets']
        if pd.isna(Color):
            value = None
        else:
            col_name = f"{Shape}_{Color}"
            if col_name in df.columns.tolist():
                value = df[(df['Months'] == join) & (df['Buckets'] == Bucket)][col_name].values.tolist()
            else:
                value = 0
        _MAX_QTY_.append(value)
    MONTHLY_STOCK_DATA['Max Qty'] = _MAX_QTY_
    MONTHLY_STOCK_DATA['Max Qty']=MONTHLY_STOCK_DATA['Max Qty'].map(lambda x:x[0] if isinstance(x, list) and len(x) > 0 else 0)
    return MONTHLY_STOCK_DATA

def populate_min_qty(df,MONTHLY_STOCK_DATA):
    """
    df : Buying Min Qty Sheet
    MONTHLY_STOCK_DATA : Monthly Stock Data Sheet
    """
    columns=list(concatenate_first_two_rows(df.iloc[0:2,2:]).values())
    columns = ['Months','Buckets'] + columns
    df.columns = columns
    df=df.iloc[2:,:]
    df.reset_index(drop=True,inplace=True)
    _MIN_QTY_ = []
    MONTHLY_STOCK_DATA['Min Qty'] = None
    for _, row in MONTHLY_STOCK_DATA.iterrows():
        join = row['Join']
        Shape = row['Shape key']
        Color = row['Color Key']
        Bucket = row['Buckets']
        if pd.isna(Color):
            value = None
        else:
            col_name = f"{Shape}_{Color}"
            if col_name in df.columns.tolist():
                value = df[(df['Months'] == join) & (df['Buckets'] == Bucket)][col_name].values.tolist()
            else:
                value = 0
        _MIN_QTY_.append(value)
    MONTHLY_STOCK_DATA['Min Qty'] = _MIN_QTY_
    MONTHLY_STOCK_DATA['Min Qty']=MONTHLY_STOCK_DATA['Min Qty'].map(lambda x:x[0] if isinstance(x, list) and len(x) > 0 else 0)
    return MONTHLY_STOCK_DATA

def populate_buying_prices(df,MONTHLY_STOCK_DATA):
    """
    df : Buying Max Prices Sheet 
    MONTHLY_STOCK_DATA : Monthly Stock Data Sheet
    """
    columns=list(concatenate_first_two_rows(df.iloc[0:2,2:]).values())
    columns = ['Months','Buckets'] + columns
    df.columns = columns
    df=df.iloc[2:,:]
    df.reset_index(drop=True,inplace=True)
    _BUYING_PRICE_ = []
    MONTHLY_STOCK_DATA['Max Buying Price'] = None
    for indx, row in MONTHLY_STOCK_DATA.iterrows():
        join = row['Join']
        Shape = row['Shape key']
        Color = row['Color Key']
        Bucket = row['Buckets']
        if pd.isna(Color):
            value = None
        else:
            col_name = f"{Shape}_{Color}"
            if col_name in df.columns.tolist():
                value = df[(df['Months'] == join) & (df['Buckets'] == Bucket)][col_name].values.tolist()
            else:
                value = 0
        _BUYING_PRICE_.append(value)
    MONTHLY_STOCK_DATA['Max Buying Price'] = _BUYING_PRICE_
    MONTHLY_STOCK_DATA['Max Buying Price']=MONTHLY_STOCK_DATA['Max Buying Price'].map(lambda x:x[0] if isinstance(x, list) and len(x) > 0 else 0)
    return MONTHLY_STOCK_DATA

def calculate_buying_price_avg(df):
    df['Buying Price Avg'] = df['Max Buying Price'] * df['Weight']
    return df

def get_quarter(month):
    Quarter_Month_Map = {
    'Q1': ['January', 'February', 'March'],
    'Q2': ['April', 'May', 'June'],
    'Q3': ['July', 'August', 'September'],
    'Q4': ['October', 'November', 'December']
    }
    year = pd.to_datetime('today').year
    yr = year - 2000

    if month in Quarter_Month_Map['Q1']:
        return f'Q1-{yr}'
    elif month in Quarter_Month_Map['Q2']:
        return f'Q2-{yr}'
    elif month in Quarter_Month_Map['Q3']:
        return f'Q3-{yr}'
    elif month in Quarter_Month_Map['Q4']:
        return f'Q4-{yr}'
    else:
        return None

def populate_quarter(df):
    """
    df : Monthly Stock Data Sheet
    """
    df['Quarter'] = df['Month'].apply(get_quarter)
    return df

def create_shape_key(x):
    if x.__contains__(r'CUSHION'):
        return 'Cushion'
    elif x.__contains__(r'OVAL'):
        return 'Oval'
    elif x.__contains__(r'PEAR'):
        return 'Pear'
    elif x.__contains__(r'CUT-CORNERED'):
        return 'Radiant'
    elif x.__contains__(r'MODIFIED RECTANGULAR'):
        return 'Cushion'
    elif x.__contains__(r'MODIFIED SQUARE'):
        return 'Cushion'
    elif x.__contains__(r'HEART'):
        return 'Cushion'
    elif x.__contains__(r'MARQUISE MODIFIED'):
        return 'Cushion'
    elif x.__contains__(r'ROUND_CORNERED'):
        return 'Cushion'
    elif x.__contains__(r'EMERALD'):
        return 'Emerald'
    else:
        return 'Other'

def poplutate_monthly_stock_sheet(file):
    """
    df_stock : Monthly Stock Data Sheet
    df_buying : Buying Max Prices Sheet
    df_min_qty : Buying Min Qty Sheet
    df_max_qty : Max Qty Sheet
    """
    df = load_data(file)
    df_stock = df['Monthly Stock Data']
    df_buying = df['Buying Max Prices']
    df_min_qty = df['MIN Data']
    df_max_qty = df['MAX Data']
    if df_stock.empty or df_buying.empty or df_min_qty.empty or df_max_qty.empty:
        raise ValueError("One or more dataframes are empty. Please check the input files.")
    df_stock = create_date_join(df_stock)
    df_stock = populate_quarter(df_stock)
    df_stock = calculate_avg(df_stock)
    df_stock = create_bucket(df_stock)
    df_stock = create_color_key(df_stock, color_map)
    df_stock['Shape key'] = df_stock['Shape'].apply(create_shape_key)
    df_stock = populate_max_qty(df_max_qty, df_stock)
    df_stock = populate_min_qty(df_min_qty, df_stock)
    df_stock = populate_buying_prices(df_buying, df_stock)
    df_stock = calculate_buying_price_avg(df_stock)
    return df_stock

def calculate_qoq_variance_percentage(current_quarter_price, previous_quarter_price):
    """
    Calculate quarter-on-quarter variance percentage of price.
    
    Args:
        current_quarter_price (float): Price for the current quarter
        previous_quarter_price (float): Price for the previous quarter
    
    Returns:
        float: Variance percentage (positive for increase, negative for decrease)
        
    Raises:
        ValueError: If previous quarter price is zero or negative
        TypeError: If inputs are not numeric
    """
    # Input validation
    if not isinstance(current_quarter_price, (int, float)) or not isinstance(previous_quarter_price, (int, float)):
        raise TypeError("Both prices must be numeric values")
    
    if previous_quarter_price <= 0:
        variance_percentage = 0.00001
        # raise ValueError("Previous quarter price must be positive (cannot be zero or negative)")
    
    # Calculate variance percentage
    if previous_quarter_price !=0:
        variance_percentage = ((current_quarter_price - previous_quarter_price) / previous_quarter_price) * 100
    else:
        variance_percentage = ((current_quarter_price - previous_quarter_price) / (previous_quarter_price+current_quarter_price)) * 100
    return round(variance_percentage, 2)

def calculate_qoq_variance_series(price_data):
    """
    Calculate quarter-on-quarter variance for a series of quarterly prices.
    
    Args:
        price_data (list): List of quarterly prices in chronological order
    
    Returns:
        list: List of QoQ variance percentages (starts from Q2 since Q1 has no previous quarter)
    """
    if len(price_data) < 2:
        raise ValueError("Need at least 2 quarters of data to calculate variance")
    
    variances = []
    for i in range(1, len(price_data)):
        variance = calculate_qoq_variance_percentage(price_data[i], price_data[i-1])
        variances.append(variance)
    
    return variances

def monthly_variance(df,col):
    analysis=df.groupby(['Month','Year'],as_index=False)[col].sum()
    analysis['Num_Month'] = analysis['Month'].map(month_map)
    analysis.sort_values(by=['Year','Num_Month'],inplace=True)
    analysis['Monthly_change']=analysis[col].pct_change().fillna(0).round(2)*100
    analysis['qaurter_change']=[0]+calculate_qoq_variance_series(analysis[col].tolist())
    return analysis

def gap_analysis(max_qty,min_qty,stock_in_hand):
    """
    max_qty : Maximum Quantity
    min_qty : Minimum Quantity
    stock_in_hand : Stock in Hand
    """
    if stock_in_hand > max_qty:
        excess_qty = stock_in_hand - max_qty
        return excess_qty
    elif stock_in_hand < min_qty:
        deficit_qty = stock_in_hand - min_qty
        return deficit_qty
    else:
        return 0

def get_filtered_data(FILTER_MONTH,FILTE_YEAR,FILTER_SHAPE,FILTER_COLOR,FILTER_BUCKET,FILTER_MONTHLY_VAR_COL):
    """
    file : Monthly Stock Data Sheet
    FILTER_MONTH : Month to filter
    FILTE_YEAR : Year to filter
    FILTER_SHAPE : Shape Key to filter
    FILTER_COLOR : Color Key to filter
    FILTER_BUCKET : Buckets to filter
    FILTER_MONTHLY_VAR_COL : Column to calculate monthly variance
    PARENT_DF : Parent DataFrame to concatenate with the monthly stock data
    """
    master_df = load_data('kunmings.pkl')
    if (type(FILTE_YEAR)==str) & (str(FILTE_YEAR).isnumeric()):
        FILTE_YEAR = int(FILTE_YEAR)
    #     FILTE_YEAR = int(FILTE_YEAR)
    #     filter_data=master_df[(master_df['Month'] == FILTER_MONTH) | \
    #                                   (master_df['Year'] == FILTE_YEAR) | \
    #                                     (master_df['Shape key'] == FILTER_SHAPE) |\
    #                                     (master_df['Color Key'] == FILTER_COLOR) |\
    #                                     (master_df['Buckets'] == FILTER_BUCKET)]
    # else:
    #     filter_data=master_df[(master_df['Month'] == FILTER_MONTH) | \
                                      
    #                                     (master_df['Shape key'] == FILTER_SHAPE) |\
    #                                     (master_df['Color Key'] == FILTER_COLOR) |\
    #                                     (master_df['Buckets'] == FILTER_BUCKET)]
    filter_data=master_df[(master_df['Month'] == FILTER_MONTH) & \
                                      (master_df['Year'] == FILTE_YEAR) & \
                                        (master_df['Shape key'] == FILTER_SHAPE) &\
                                        (master_df['Color Key'] == FILTER_COLOR) &\
                                        (master_df['Buckets'] == FILTER_BUCKET)]
    max_qty = filter_data['Max Qty'].max()
    min_qty = filter_data['Min Qty'].min()
    stock_in_hand = filter_data.shape[0]
    gap_analysis_op = gap_analysis(max_qty, min_qty, stock_in_hand)
    _filter_ = master_df[(master_df['Shape key'] == FILTER_SHAPE) &\
                                        (master_df['Color Key'] == FILTER_COLOR) &\
                                        (master_df['Buckets'] == FILTER_BUCKET)]
    try:
        max_buying_price = filter_data['Max Buying Price'].max()
        current_avg_cost = sum(.9*((filter_data['Max Buying Price'] * filter_data['Weight'])/(filter_data['Weight'].sum() if filter_data['Weight'].sum() != 0 else 1)))
        avg_value = master_df[FILTER_MONTHLY_VAR_COL].mean()
        MOM_Variance = (sum((filter_data[FILTER_MONTHLY_VAR_COL] - avg_value)/ avg_value )/filter_data.shape[0]) * 100
        var_analysis = monthly_variance(_filter_,FILTER_MONTHLY_VAR_COL)
        MOM_Percent_Change = var_analysis[(var_analysis['Month'] == FILTER_MONTH) & (var_analysis['Year'] == FILTE_YEAR)]['Monthly_change'].values.tolist()[0]
        MOM_QoQ_Percent_Change = var_analysis[(var_analysis['Month'] == FILTER_MONTH) & (var_analysis['Year'] == FILTE_YEAR)]['qaurter_change'].values.tolist()[0]
        if MOM_Percent_Change == np.inf:
            MOM_Percent_Change = 0
        if MOM_QoQ_Percent_Change == np.inf:
            MOM_QoQ_Percent_Change = 0
        return [filter_data,int(max_buying_price),int(current_avg_cost), int(MOM_Variance), MOM_Percent_Change, MOM_QoQ_Percent_Change,gap_analysis_op]
    except:
        return [pd.DataFrame(columns=master_df.columns.tolist()),f"There is {filter_data.shape[0]} rows after filter",f"There is {filter_data.shape[0]} rows after filter",f"There is {filter_data.shape[0]} rows after filter",f"There is {filter_data.shape[0]} rows after filter",f"There is {filter_data.shape[0]} rows after filter",gap_analysis_op]

def get_final_data(file,PARENT_DF = 'kunmings.pkl'):
    df = poplutate_monthly_stock_sheet(file)
    parent_df = load_data(PARENT_DF)
    master_df = pd.concat([df, parent_df], ignore_index=True,axis=0)
    save_data(master_df)
    return master_df

def sort_months(months):
    """
    Sort months supporting both full names and abbreviations.
    
    Args:
        months: List of month names (full names or abbreviations)
    
    Returns:
        List of months sorted in chronological order
    """
    import calendar
    
    # Create mapping for both full names and abbreviations
    month_mapping = {}
    
    for i in range(1, 13):
        full_name = calendar.month_name[i]
        abbr_name = calendar.month_abbr[i]
        month_mapping[full_name] = i
        month_mapping[abbr_name] = i
        month_mapping[full_name.lower()] = i
        month_mapping[abbr_name.lower()] = i
    
    # Sort based on month order
    sorted_months = sorted(months, key=lambda month: month_mapping.get(month, 13))
    
    return sorted_months

def create_metric_with_tooltip(label, value, tooltip_text):
    """
    Create a metric with tooltip using pure CSS - Streamlit compatible version
    """
    # Create unique ID for each metric
    metric_id = f"metric_{label.replace(' ', '_').lower()}_{hash(label) % 1000}"
    
    # HTML with pure CSS tooltip (no JavaScript needed)
    html_content = f"""
    <div style="position: relative; display: inline-block; width: 100%; margin-bottom: 10px;">
        <div class="metric-container" style="
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            text-align: center;
            cursor: help;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            min-height: 80px;
            position: relative;
        ">
            <div style="font-size: 14px; color: #666; margin-bottom: 8px; font-weight: 600;">
                {label}
            </div>
            <div style="font-size: 24px; font-weight: bold; color: #1f77b4; margin-bottom: 4px;">
                {value}
            </div>
            <div style="font-size: 10px; color: #999; font-style: italic;">
                Hover for details
            </div>
            
            <!-- Tooltip positioned absolutely within the container -->
            <div class="tooltip-content" style="
                position: absolute;
                bottom: 100%;
                left: 50%;
                transform: translateX(-50%);
                background: #2c3e50;
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                font-size: 12px;
                line-height: 1.4;
                max-width: 280px;
                white-space: normal;
                text-align: left;
                z-index: 1000;
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
                box-shadow: 0 8px 16px rgba(0,0,0,0.3);
                border: 1px solid #34495e;
                margin-bottom: 10px;
                pointer-events: none;
            ">
                <strong style="color: #3498db; display: block; margin-bottom: 8px; font-size: 13px;">{label}</strong>
                <div style="color: #ecf0f1; font-size: 11px; line-height: 1.5;">
                    {tooltip_text}
                </div>
                <!-- Tooltip arrow -->
                <div style="
                    position: absolute;
                    top: 100%;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 0;
                    height: 0;
                    border-left: 8px solid transparent;
                    border-right: 8px solid transparent;
                    border-top: 8px solid #2c3e50;
                "></div>
            </div>
        </div>
    </div>
    
    <style>
        /* Pure CSS hover effect - more reliable in Streamlit */
        .metric-container:hover .tooltip-content {{
            opacity: 1 !important;
            visibility: visible !important;
            transform: translateX(-50%) translateY(-5px) !important;
        }}
        
        .metric-container:hover {{
            background: linear-gradient(135deg, #f0f7ff 0%, #e8f2ff 100%) !important;
            border-color: #3498db !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
        }}
        
        /* Ensure tooltip stays visible when hovering */
        .metric-container:hover .tooltip-content,
        .tooltip-content:hover {{
            opacity: 1 !important;
            visibility: visible !important;
        }}
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {{
            .tooltip-content {{
                max-width: 200px !important;
                font-size: 11px !important;
                padding: 12px 16px !important;
            }}
        }}
    </style>
    """
    return html_content


def create_metric_with_tooltip_alternative(label, value, tooltip_text):
    """
    Alternative implementation using Streamlit's built-in help parameter
    This is more reliable but less visually appealing
    """
    import streamlit as st
    
    # Create columns for better layout
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.metric(
            label=label,
            value=value,
            help=tooltip_text
        )
    
    return None


def create_metric_with_tooltip_expander(label, value, tooltip_text):
    """
    Another alternative using expander for detailed information
    """
    import streamlit as st
    
    # Main metric display
    st.metric(label=label, value=value)
    
    # Expander for detailed info
    with st.expander(f"ℹ️ About {label}"):
        st.write(tooltip_text)
    
    return None
def main():
    st.set_page_config(page_title="Yellow Diamond Dashboard", layout="wide")
    st.title("Yellow Diamond Dashboard")
    st.markdown("Upload Excel files to process multiple sheets and filter data.")
    
    # Initialize session state
    if 'data_processed' not in st.session_state:
        st.session_state.data_processed = False
    if 'master_df' not in st.session_state:
        st.session_state.master_df = pd.DataFrame()
    
    # Sidebar for controls
    st.sidebar.header("Controls")
    
    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload Excel File",
        type=['xlsx', 'xls'],
        help="Upload an Excel file with multiple sheets"
    )
    
    # Main content area
    if uploaded_file is not None and not st.session_state.data_processed:
        with st.spinner("Processing Excel file..."):
            st.subheader("🗄️ Master Database")
            st.session_state.master_df = get_final_data(uploaded_file)
            st.session_state.data_processed = True
    
    if not st.session_state.master_df.empty or uploaded_file is not None:
        Month, Year, Shape, Color, Bucket, Variance_Column = st.columns(6)
        
        with Month:
            categories = ["None"] + sort_months(list(st.session_state.master_df['Month'].unique()))
            selected_month = st.selectbox("Filter by Month", categories)
        with Year:
            years = ["None"] + sorted(list(st.session_state.master_df['Year'].unique()))
            selected_year = st.selectbox("Filter by Year", years)
        with Shape:
            shapes = ["None"] + list(st.session_state.master_df['Shape key'].unique())
            selected_shape = st.selectbox("Filter by Shape", shapes)
        with Color:
            colors = ["None"] + list(st.session_state.master_df['Color Key'].unique())
            selected_color = st.selectbox("Filter by Color", colors)
        with Bucket:
            buckets = ["None"] + list(stock_bucket.keys())
            selected_bucket = st.selectbox("Filter by Bucket", buckets)
        with Variance_Column:
            variance_columns = ["None"] + ['Buying Price Avg', 'Max Buying Price']
            selected_variance_column = st.selectbox("Select Variance Column", variance_columns)
        
        # Apply filters
        filtered_df = st.session_state.master_df.copy()
        
        if ((selected_month != "None") & (selected_year != "None") & (selected_shape != "None") & 
            (selected_color != "None") & (selected_bucket != "None")):
            
            filter_data, max_buying_price, current_avg_cost, MOM_Variance, MOM_Percent_Change, MOM_QoQ_Percent_Change, gap_output = get_filtered_data(
                selected_month, selected_year, selected_shape, selected_color, selected_bucket, selected_variance_column
            )
            
            # Display summary metrics with tooltips
            st.subheader("📊 Summary Metrics")
            
            # Define tooltips for each metric
            tooltips = {
                "Gap Analysis": "Shows the difference between current stock and optimal stock levels. Positive values indicate excess stock, negative values indicate shortage.",
                "Max Buying Price": "The highest price you should pay when purchasing this category of diamonds based on current market conditions.",
                "Current Avg Cost": "The weighted average cost of diamonds currently in stock for this category, calculated at 90% of max buying price.",
                "MOM Variance": "Month-over-Month variance showing how much the current month's values differ from the average, expressed as a percentage.",
                "MOM Percent Change": "Month-over-Month percentage change comparing current month to previous month's values.",
                "MOM QoQ Percent Change": "Quarter-over-Quarter percentage change comparing current quarter to previous quarter's values."
            }
            
            # Create columns for metrics
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            if type(max_buying_price) != str:
                # Format values for display
                gap_display = f"{gap_output:+d}" if gap_output != 0 else "Optimal"
                mbp_display = f"${max_buying_price:,.2f}"
                cac_display = f"${current_avg_cost:,.2f}"
                mom_var_display = f"{MOM_Variance:,.2f}%"
                mom_perc_display = f"{MOM_Percent_Change:.2f}%"
                qoq_perc_display = f"{MOM_QoQ_Percent_Change:.2f}%"
                
                with col1:
                     st.components.v1.html(
                                                create_metric_with_tooltip("Gap Analysis", gap_display, tooltips["Gap Analysis"]), 
                                                height=160
                                            )
                with col2:
                    st.components.v1.html(
                create_metric_with_tooltip("Max Buying Price", mbp_display, tooltips["Max Buying Price"]), 
                height=160
            )
                with col3:
                    st.components.v1.html(
                create_metric_with_tooltip("Current Avg Cost", cac_display, tooltips["Current Avg Cost"]), 
                height=160
            )
                with col4:
                    st.components.v1.html(
                create_metric_with_tooltip("MOM Variance", mom_var_display, tooltips["MOM Variance"]), 
                height=160
            )
                with col5:
                    st.components.v1.html(
                create_metric_with_tooltip("MOM Percent Change", mom_perc_display, tooltips["MOM Percent Change"]), 
                height=160
            )
                with col6:
                    st.components.v1.html(
                create_metric_with_tooltip("MOM QoQ Percent Change", qoq_perc_display, tooltips["MOM QoQ Percent Change"]), 
                height=160
            )
            else:
                # No data case
                gap_display = f"{gap_output:+d}" if gap_output != 0 else "Optimal"
                mbp_display = 0
                cac_display = 0
                mom_var_display = 0
                mom_perc_display = "0.00%"
                qoq_perc_display = "0.00%"
                with col1:
                     st.components.v1.html(
                                            create_metric_with_tooltip("Gap Analysis", gap_display, tooltips["Gap Analysis"]), 
                                            height=160
                                        )
                with col2:
                    st.components.v1.html(
                create_metric_with_tooltip("Max Buying Price", mbp_display, tooltips["Max Buying Price"]), 
                height=160
            )
                with col3:
                    st.components.v1.html(
                create_metric_with_tooltip("Current Avg Cost", cac_display, tooltips["Current Avg Cost"]), 
                height=160
            )
                with col4:
                    st.components.v1.html(
                create_metric_with_tooltip("MOM Variance", mom_var_display, tooltips["MOM Variance"]), 
                height=160
            )
                with col5:
                    st.components.v1.html(
                create_metric_with_tooltip("MOM Percent Change", mom_perc_display, tooltips["MOM Percent Change"]), 
                height=160
            )
                with col6:
                    st.components.v1.html(
                create_metric_with_tooltip("MOM QoQ Percent Change", qoq_perc_display, tooltips["MOM QoQ Percent Change"]), 
                height=160
            )   
                st.subheader("No Data Present for This Filter")
            
            st.subheader("📊 Data Table")
            st.dataframe(
                filter_data,
                use_container_width=True,
                hide_index=True
            )
            
            # Download processed data
            st.subheader("💾 Download Filtered Data")
            csv = filter_data.loc[:, ['Product Id', 'Shape key', 'Color Key', 'avg', 'Min Qty', 'Max Qty', 'Buying Price Avg', 'Max Buying Price']].to_csv(index=False)
            st.download_button(
                label="Download Filtered Data as CSV",
                data=csv,
                file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            st.subheader("💾 Download Master Data")
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download Master Data as CSV",
                data=csv,
                file_name=f"processed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Please select all filter options to view the analysis.")
    else:
        st.info("No data in master database. Upload an Excel file to get started!")
    
    # Reset button
    if st.sidebar.button("Reset Data Processing"):
        st.session_state.data_processed = False
        st.session_state.master_df = pd.DataFrame()
        st.rerun()

if __name__ == "__main__":
    main()
