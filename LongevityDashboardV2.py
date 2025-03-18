import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import math
import base64
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import tempfile
import os
from fpdf import FPDF
import plotly.io as pio
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Longevity Clinic Financial Dashboard",
    page_icon="🧬",
    layout="wide"
)

# Add this near the top of your file, after imports but before any other content
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "hatch_end_delights":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

# Then add this right after the page configuration but before displaying any content
if not check_password():
    st.stop()  # Stop execution if password is not correct

# Title and introduction
st.title("Longevity Clinic Financial Dashboard")
st.markdown("Comprehensive financial tracking and analysis tool for longevity and wellness clinics.")

# Create sidebar for inputs
st.sidebar.header("Business Parameters")

# Input parameters with default values
with st.sidebar.expander("Business Details", expanded=True):
    business_name = st.text_input("Business Name", "Longevity Clinic Hatch End")
    business_type = st.selectbox("Business Type", ["Wellness Center", "Medical Clinic", "Spa & Wellness", "Longevity Clinic"])
    business_location = st.text_input("Location", "Hatch End, London")
    business_size_sqft = st.number_input("Business Size (sq ft)", min_value=500, value=1600, step=100)
    operating_hours_weekly = st.number_input("Operating Hours per Week", min_value=20, value=66, step=1)
    
with st.sidebar.expander("Initial Investment", expanded=True):
    renovation_cost = st.number_input("Renovation Cost (£)", min_value=10000, value=135000, step=5000)
    equipment_cost = st.number_input("Equipment Cost (£)", min_value=10000, value=50000, step=5000)
    marketing_branding_initial = st.number_input("Initial Marketing & Branding (£)", min_value=1000, value=15000, step=1000)
    legal_permits_licenses = st.number_input("Legal, Permits & Licenses (£)", min_value=1000, value=10000, step=1000)

with st.sidebar.expander("Service Pricing", expanded=True):
    cryotherapy_price = st.number_input("Cryotherapy Session Price (£)", min_value=10, value=45, step=5)
    infrared_sauna_price = st.number_input("Infrared Sauna Session Price (£)", min_value=10, value=45, step=5)
    iv_therapy_basic_price = st.number_input("IV Therapy Basic Session Price (£)", min_value=50, value=150, step=10)
    iv_therapy_premium_price = st.number_input("IV Therapy Premium Session Price (£)", min_value=100, value=250, step=10)
    face_treatment_price = st.number_input("Infrared Face Treatment Price (£)", min_value=10, value=50, step=5)
    
    # Calculate average IV therapy price
    avg_iv_therapy_price = (iv_therapy_basic_price + iv_therapy_premium_price) / 2
    
with st.sidebar.expander("Membership Options", expanded=True):
    silver_membership_price = st.number_input("Silver Membership (4 services/month) (£)", min_value=50, value=225, step=25)
    gold_membership_price = st.number_input("Gold Membership (8 services/month) (£)", min_value=100, value=400, step=25)
    platinum_membership_price = st.number_input("Platinum Membership (12 services/month) (£)", min_value=200, value=550, step=25)

with st.sidebar.expander("Capacity & Utilization", expanded=True):
    cryotherapy_capacity_per_hour = st.number_input("Cryotherapy Sessions per Hour", min_value=1, value=3, step=1)
    infrared_sauna_capacity_per_hour = st.number_input("Infrared Sauna Sessions per Hour", min_value=1, value=4, step=1)
    iv_therapy_capacity_per_hour = st.number_input("IV Therapy Sessions per Hour", min_value=1, value=1, step=1)
    face_treatment_capacity_per_hour = st.number_input("Face Treatment Sessions per Hour", min_value=1, value=2, step=1)
    
    # Utilization rates
    year1_start_utilization = st.slider("Year 1 Starting Utilization (%)", min_value=5, max_value=50, value=20, step=5)
    year1_end_utilization = st.slider("Year 1 Ending Utilization (%)", min_value=10, max_value=70, value=40, step=5)
    year2_start_utilization = st.slider("Year 2 Starting Utilization (%)", min_value=20, max_value=70, value=40, step=5)
    year2_end_utilization = st.slider("Year 2 Ending Utilization (%)", min_value=30, max_value=80, value=60, step=5)
    year3_utilization = st.slider("Year 3 Utilization (%)", min_value=40, max_value=90, value=65, step=5)
    
    # Calculate average utilization for each year
    year1_avg_utilization = (year1_start_utilization + year1_end_utilization) / 2
    year2_avg_utilization = (year2_start_utilization + year2_end_utilization) / 2
    
    # Service-specific utilization adjustments
    cryotherapy_utilization_factor = st.slider("Cryotherapy Utilization Factor", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
    infrared_sauna_utilization_factor = st.slider("Infrared Sauna Utilization Factor", min_value=0.5, max_value=1.5, value=1.2, step=0.1)
    iv_therapy_utilization_factor = st.slider("IV Therapy Utilization Factor", min_value=0.5, max_value=1.5, value=0.5, step=0.1)
    face_treatment_utilization_factor = st.slider("Face Treatment Utilization Factor", min_value=0.5, max_value=1.5, value=1.0, step=0.1)

with st.sidebar.expander("Operating Expenses", expanded=True):
    rent_monthly = st.number_input("Monthly Rent (£)", min_value=1000, value=5000, step=500)
    staff_count = st.number_input("Number of Staff", min_value=1, value=3, step=1)
    staff_annual_salary = st.number_input("Annual Salary per Staff (£)", min_value=20000, value=30000, step=1000)
    staff_benefits_tax_percent = st.number_input("Staff Benefits & Tax (%)", min_value=10.0, value=20.0, step=1.0)
    equipment_finance_monthly = st.number_input("Monthly Equipment Finance (£)", min_value=500, value=3500, step=100)
    utilities_monthly = st.number_input("Monthly Utilities (£)", min_value=500, value=2000, step=100)
    supplies_percent_of_revenue = st.number_input("Supplies (% of Revenue)", min_value=5.0, value=20.0, step=1.0)
    insurance_annual = st.number_input("Annual Insurance (£)", min_value=1000, value=6000, step=500)
    marketing_percent_of_revenue_y1 = st.number_input("Marketing Year 1 (% of Revenue)", min_value=5.0, value=12.0, step=1.0)
    marketing_percent_of_revenue = st.number_input("Marketing Year 2+ (% of Revenue)", min_value=3.0, value=8.0, step=1.0)
    accounting_legal_annual = st.number_input("Annual Accounting/Legal (£)", min_value=1000, value=6000, step=500)
    maintenance_annual = st.number_input("Annual Maintenance (£)", min_value=1000, value=7200, step=500)
    miscellaneous_annual = st.number_input("Annual Miscellaneous (£)", min_value=1000, value=5000, step=500)

with st.sidebar.expander("Growth & Inflation", expanded=True):
    price_increase_y2 = st.number_input("Price Increase Year 2 (%)", min_value=0.0, value=10.0, step=1.0)
    price_increase_y3 = st.number_input("Price Increase Year 3 (%)", min_value=0.0, value=5.0, step=1.0)
    expense_inflation = st.number_input("Annual Expense Inflation (%)", min_value=0.0, value=3.0, step=0.5)
    maintenance_increase = st.number_input("Annual Maintenance Increase (%)", min_value=0.0, value=25.0, step=5.0)

# Add this in the "Capacity & Utilization" section
with st.sidebar.expander("Membership Projections", expanded=True):
    # Membership projections
    silver_members_y1 = st.number_input("Silver Members (Year 1)", min_value=0, value=20, step=5)
    gold_members_y1 = st.number_input("Gold Members (Year 1)", min_value=0, value=10, step=5)
    platinum_members_y1 = st.number_input("Platinum Members (Year 1)", min_value=0, value=5, step=2)
    
    membership_growth_y2 = st.slider("Membership Growth Year 2 (%)", min_value=0, max_value=100, value=50, step=10)
    membership_growth_y3 = st.slider("Membership Growth Year 3 (%)", min_value=0, max_value=100, value=30, step=10)

# Calculations
# Initial investment
total_initial_investment = renovation_cost + equipment_cost + marketing_branding_initial + legal_permits_licenses

# Revenue calculations for Year 1
weeks_per_year = 52

# Calculate service-specific utilization rates for Year 1
cryo_util_y1 = (year1_avg_utilization / 100) * cryotherapy_utilization_factor
sauna_util_y1 = (year1_avg_utilization / 100) * infrared_sauna_utilization_factor
iv_util_y1 = (year1_avg_utilization / 100) * iv_therapy_utilization_factor
face_util_y1 = (year1_avg_utilization / 100) * face_treatment_utilization_factor

# Cap utilization at 100%
cryo_util_y1 = min(cryo_util_y1, 1.0)
sauna_util_y1 = min(sauna_util_y1, 1.0)
iv_util_y1 = min(iv_util_y1, 1.0)
face_util_y1 = min(face_util_y1, 1.0)

# Year 1 Revenue
cryo_revenue_y1 = cryotherapy_price * cryotherapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * cryo_util_y1
sauna_revenue_y1 = infrared_sauna_price * infrared_sauna_capacity_per_hour * operating_hours_weekly * weeks_per_year * sauna_util_y1
iv_revenue_y1 = avg_iv_therapy_price * iv_therapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * iv_util_y1
face_revenue_y1 = face_treatment_price * face_treatment_capacity_per_hour * operating_hours_weekly * weeks_per_year * face_util_y1

# Calculate membership revenue
silver_revenue_y1 = silver_members_y1 * silver_membership_price * 12  # Annual revenue
gold_revenue_y1 = gold_members_y1 * gold_membership_price * 12
platinum_revenue_y1 = platinum_members_y1 * platinum_membership_price * 12
membership_revenue_y1 = silver_revenue_y1 + gold_revenue_y1 + platinum_revenue_y1

# After calculating individual service revenues and membership revenue, add:
total_revenue_y1 = cryo_revenue_y1 + sauna_revenue_y1 + iv_revenue_y1 + face_revenue_y1 + membership_revenue_y1

# Then calculate expenses that depend on total revenue
supplies_y1 = total_revenue_y1 * (supplies_percent_of_revenue / 100)
marketing_y1 = total_revenue_y1 * (marketing_percent_of_revenue_y1 / 100)

# Year 1 Expenses
rent_annual = rent_monthly * 12
staff_cost_annual = staff_count * staff_annual_salary * (1 + staff_benefits_tax_percent / 100)
equipment_finance_annual = equipment_finance_monthly * 12
utilities_annual = utilities_monthly * 12
insurance_annual = insurance_annual

total_expenses_y1 = (
    rent_annual + 
    staff_cost_annual + 
    equipment_finance_annual + 
    utilities_annual + 
    supplies_y1 + 
    insurance_annual + 
    marketing_y1 + 
    accounting_legal_annual + 
    maintenance_annual + 
    miscellaneous_annual
)

# Year 1 EBITDA
ebitda_y1 = total_revenue_y1 - total_expenses_y1
ebitda_margin_y1 = (ebitda_y1 / total_revenue_y1) * 100 if total_revenue_y1 > 0 else 0

# Year 2 calculations
# Price increases for Year 2
cryo_price_y2 = cryotherapy_price * (1 + price_increase_y2 / 100)
sauna_price_y2 = infrared_sauna_price * (1 + price_increase_y2 / 100)
iv_price_y2 = avg_iv_therapy_price * (1 + price_increase_y2 / 100)
face_price_y2 = face_treatment_price * (1 + price_increase_y2 / 100)

# Calculate service-specific utilization rates for Year 2
cryo_util_y2 = (year2_avg_utilization / 100) * cryotherapy_utilization_factor
sauna_util_y2 = (year2_avg_utilization / 100) * infrared_sauna_utilization_factor
iv_util_y2 = (year2_avg_utilization / 100) * iv_therapy_utilization_factor
face_util_y2 = (year2_avg_utilization / 100) * face_treatment_utilization_factor

# Cap utilization at 100%
cryo_util_y2 = min(cryo_util_y2, 1.0)
sauna_util_y2 = min(sauna_util_y2, 1.0)
iv_util_y2 = min(iv_util_y2, 1.0)
face_util_y2 = min(face_util_y2, 1.0)

# Year 2 Revenue
cryo_revenue_y2 = cryo_price_y2 * cryotherapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * cryo_util_y2
sauna_revenue_y2 = sauna_price_y2 * infrared_sauna_capacity_per_hour * operating_hours_weekly * weeks_per_year * sauna_util_y2
iv_revenue_y2 = iv_price_y2 * iv_therapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * iv_util_y2
face_revenue_y2 = face_price_y2 * face_treatment_capacity_per_hour * operating_hours_weekly * weeks_per_year * face_util_y2

# Calculate membership revenue
silver_members_y2 = silver_members_y1 * (1 + membership_growth_y2/100)
gold_members_y2 = gold_members_y1 * (1 + membership_growth_y2/100)
platinum_members_y2 = platinum_members_y1 * (1 + membership_growth_y2/100)

silver_price_y2 = silver_membership_price * (1 + price_increase_y2/100)
gold_price_y2 = gold_membership_price * (1 + price_increase_y2/100)
platinum_price_y2 = platinum_membership_price * (1 + price_increase_y2/100)

silver_revenue_y2 = silver_members_y2 * silver_price_y2 * 12
gold_revenue_y2 = gold_members_y2 * gold_price_y2 * 12
platinum_revenue_y2 = platinum_members_y2 * platinum_price_y2 * 12
membership_revenue_y2 = silver_revenue_y2 + gold_revenue_y2 + platinum_revenue_y2

# After calculating individual service revenues and membership revenue, add:
total_revenue_y2 = cryo_revenue_y2 + sauna_revenue_y2 + iv_revenue_y2 + face_revenue_y2 + membership_revenue_y2

# After calculating total_revenue_y2, add:
supplies_y2 = total_revenue_y2 * (supplies_percent_of_revenue / 100)

# Year 2 Expenses with inflation
rent_annual_y2 = rent_annual * (1 + expense_inflation / 100)
staff_cost_annual_y2 = staff_cost_annual * (1 + expense_inflation / 100)
utilities_annual_y2 = utilities_annual * (1 + expense_inflation / 100)
insurance_annual_y2 = insurance_annual * (1 + expense_inflation / 100)
marketing_y2 = total_revenue_y2 * (marketing_percent_of_revenue / 100)
accounting_legal_annual_y2 = accounting_legal_annual * (1 + expense_inflation / 100)
maintenance_annual_y2 = maintenance_annual * (1 + maintenance_increase / 100)
miscellaneous_annual_y2 = miscellaneous_annual * (1 + expense_inflation / 100)

total_expenses_y2 = (
    rent_annual_y2 + 
    staff_cost_annual_y2 + 
    equipment_finance_annual + 
    utilities_annual_y2 + 
    supplies_y2 + 
    insurance_annual_y2 + 
    marketing_y2 + 
    accounting_legal_annual_y2 + 
    maintenance_annual_y2 + 
    miscellaneous_annual_y2
)

# Year 2 EBITDA
ebitda_y2 = total_revenue_y2 - total_expenses_y2
ebitda_margin_y2 = (ebitda_y2 / total_revenue_y2) * 100 if total_revenue_y2 > 0 else 0

# Year 3 calculations
# Price increases for Year 3
cryo_price_y3 = cryo_price_y2 * (1 + price_increase_y3 / 100)
sauna_price_y3 = sauna_price_y2 * (1 + price_increase_y3 / 100)
iv_price_y3 = iv_price_y2 * (1 + price_increase_y3 / 100)
face_price_y3 = face_price_y2 * (1 + price_increase_y3 / 100)

# Calculate service-specific utilization rates for Year 3
cryo_util_y3 = (year3_utilization / 100) * cryotherapy_utilization_factor
sauna_util_y3 = (year3_utilization / 100) * infrared_sauna_utilization_factor
iv_util_y3 = (year3_utilization / 100) * iv_therapy_utilization_factor
face_util_y3 = (year3_utilization / 100) * face_treatment_utilization_factor

# Cap utilization at 100%
cryo_util_y3 = min(cryo_util_y3, 1.0)
sauna_util_y3 = min(sauna_util_y3, 1.0)
iv_util_y3 = min(iv_util_y3, 1.0)
face_util_y3 = min(face_util_y3, 1.0)

# Year 3 Revenue
cryo_revenue_y3 = cryo_price_y3 * cryotherapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * cryo_util_y3
sauna_revenue_y3 = sauna_price_y3 * infrared_sauna_capacity_per_hour * operating_hours_weekly * weeks_per_year * sauna_util_y3
iv_revenue_y3 = iv_price_y3 * iv_therapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * iv_util_y3
face_revenue_y3 = face_price_y3 * face_treatment_capacity_per_hour * operating_hours_weekly * weeks_per_year * face_util_y3

# Calculate membership revenue
silver_members_y3 = silver_members_y2 * (1 + membership_growth_y3/100)
gold_members_y3 = gold_members_y2 * (1 + membership_growth_y3/100)
platinum_members_y3 = platinum_members_y2 * (1 + membership_growth_y3/100)

silver_price_y3 = silver_price_y2 * (1 + price_increase_y3/100)
gold_price_y3 = gold_price_y2 * (1 + price_increase_y3/100)
platinum_price_y3 = platinum_price_y2 * (1 + price_increase_y3/100)

silver_revenue_y3 = silver_members_y3 * silver_price_y3 * 12
gold_revenue_y3 = gold_members_y3 * gold_price_y3 * 12
platinum_revenue_y3 = platinum_members_y3 * platinum_price_y3 * 12
membership_revenue_y3 = silver_revenue_y3 + gold_revenue_y3 + platinum_revenue_y3

# After calculating individual service revenues and membership revenue, add:
total_revenue_y3 = cryo_revenue_y3 + sauna_revenue_y3 + iv_revenue_y3 + face_revenue_y3 + membership_revenue_y3

# After calculating total_revenue_y3, add:
supplies_y3 = total_revenue_y3 * (supplies_percent_of_revenue / 100)

# Year 3 Expenses with inflation
rent_annual_y3 = rent_annual_y2 * (1 + expense_inflation / 100)
# Increase staff for Year 3 (3.5 FTE as per forecast)
staff_cost_annual_y3 = (staff_count + 0.5) * staff_annual_salary * (1 + staff_benefits_tax_percent / 100) * (1 + expense_inflation / 100)
utilities_annual_y3 = utilities_annual_y2 * (1 + expense_inflation / 100)
insurance_annual_y3 = insurance_annual_y2 * (1 + expense_inflation / 100)
marketing_y3 = total_revenue_y3 * (marketing_percent_of_revenue / 100)
accounting_legal_annual_y3 = accounting_legal_annual_y2 * (1 + expense_inflation / 100)
maintenance_annual_y3 = maintenance_annual_y2 * (1 + maintenance_increase / 100)
miscellaneous_annual_y3 = miscellaneous_annual_y2 * (1 + expense_inflation / 100)

total_expenses_y3 = (
    rent_annual_y3 + 
    staff_cost_annual_y3 + 
    equipment_finance_annual + 
    utilities_annual_y3 + 
    supplies_y3 + 
    insurance_annual_y3 + 
    marketing_y3 + 
    accounting_legal_annual_y3 + 
    maintenance_annual_y3 + 
    miscellaneous_annual_y3
)

# Year 3 EBITDA
ebitda_y3 = total_revenue_y3 - total_expenses_y3
ebitda_margin_y3 = (ebitda_y3 / total_revenue_y3) * 100 if total_revenue_y3 > 0 else 0

# Break-even analysis
monthly_fixed_costs = (
    rent_monthly + 
    (staff_cost_annual / 12) + 
    equipment_finance_monthly + 
    utilities_monthly + 
    (insurance_annual / 12) + 
    (accounting_legal_annual / 12) + 
    (maintenance_annual / 12) + 
    (miscellaneous_annual / 12)
)

# Calculate average revenue and variable cost per customer visit
avg_service_price = (cryotherapy_price + infrared_sauna_price + avg_iv_therapy_price + face_treatment_price) / 4
avg_variable_cost_per_visit = avg_service_price * ((supplies_percent_of_revenue + marketing_percent_of_revenue_y1) / 100)
contribution_margin_per_visit = avg_service_price - avg_variable_cost_per_visit

# Break-even calculations
monthly_break_even_visits = monthly_fixed_costs / contribution_margin_per_visit
weekly_break_even_visits = monthly_break_even_visits / 4.33  # Average weeks per month
daily_break_even_visits = weekly_break_even_visits / 6  # Assuming 6 days per week operation

# ROI calculations
cumulative_ebitda_y1 = ebitda_y1
cumulative_ebitda_y2 = ebitda_y1 + ebitda_y2
cumulative_ebitda_y3 = ebitda_y1 + ebitda_y2 + ebitda_y3

roi_y1 = (ebitda_y1 / total_initial_investment) * 100
roi_y2 = (cumulative_ebitda_y2 / total_initial_investment) * 100
roi_y3 = (cumulative_ebitda_y3 / total_initial_investment) * 100

# Payback period calculation (simplified)
monthly_ebitda_y1 = ebitda_y1 / 12
payback_months = total_initial_investment / monthly_ebitda_y1 if monthly_ebitda_y1 > 0 else float('inf')

# Main dashboard
# KPI metrics in columns
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Year 3 Revenue", f"£{total_revenue_y3:,.0f}")
with col2:
    st.metric("Year 3 EBITDA", f"£{ebitda_y3:,.0f}")
with col3:
    st.metric("Year 3 EBITDA Margin", f"{ebitda_margin_y3:.1f}%")
with col4:
    st.metric("3-Year ROI", f"{roi_y3:.1f}%")

# Revenue and EBITDA growth
st.subheader("Revenue & EBITDA Growth")

# Create data for the chart
years = ["Year 1", "Year 2", "Year 3"]
revenue_data = [total_revenue_y1, total_revenue_y2, total_revenue_y3]
ebitda_data = [ebitda_y1, ebitda_y2, ebitda_y3]
margin_data = [ebitda_margin_y1, ebitda_margin_y2, ebitda_margin_y3]

# Create a figure with two y-axes
fig = go.Figure()

# Add revenue bars
fig.add_trace(go.Bar(
    x=years,
    y=revenue_data,
    name="Revenue",
    marker_color='blue',
    opacity=0.7
))

# Add EBITDA bars
fig.add_trace(go.Bar(
    x=years,
    y=ebitda_data,
    name="EBITDA",
    marker_color='green',
    opacity=0.7
))

# Add EBITDA margin line
fig.add_trace(go.Scatter(
    x=years,
    y=margin_data,
    name="EBITDA Margin (%)",
    mode='lines+markers',
    yaxis='y2',
    line=dict(color='red', width=3),
    marker=dict(size=10)
))

# Update layout for dual y-axis
fig.update_layout(
    title='Revenue, EBITDA & Margin Growth',
    yaxis=dict(
        title=dict(text="Amount (£)", font=dict(color="blue")),
        tickfont=dict(color="blue")
    ),
    yaxis2=dict(
        title=dict(text="EBITDA Margin (%)", font=dict(color="red")),
        tickfont=dict(color="red"),
        anchor="x",
        overlaying="y",
        side="right"
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    barmode='group',
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='black')
)

st.plotly_chart(fig, use_container_width=True)

# Two columns for Revenue Breakdown and Expense Breakdown
col1, col2 = st.columns(2)

# Revenue breakdown pie chart
with col1:
    st.subheader("Year 1 Revenue Breakdown")
    revenue_data = {
        'Service': [
            'Cryotherapy', 'Infrared Sauna', 'IV Therapy', 'Face Treatments', 'Memberships'
        ],
        'Revenue': [
            cryo_revenue_y1, sauna_revenue_y1, iv_revenue_y1, face_revenue_y1, membership_revenue_y1
        ]
    }
    df_revenue = pd.DataFrame(revenue_data)
    fig_revenue = px.pie(
        df_revenue, 
        values='Revenue', 
        names='Service',
        title='Revenue Breakdown by Service',
        color_discrete_sequence=['blue', 'green', 'red', 'orange', 'purple'],
        hole=0.4
    )
    fig_revenue.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        marker=dict(line=dict(color='white', width=2))
    )
    fig_revenue.update_layout(
        font=dict(color='black'),
        legend=dict(orientation='h', yanchor='bottom', y=-0.2),
        paper_bgcolor='white'
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

# Expense breakdown pie chart
with col2:
    st.subheader("Year 1 Expense Breakdown")
    expense_data = {
        'Category': [
            'Rent', 'Staff', 'Equipment Finance', 'Utilities', 'Supplies', 
            'Insurance', 'Marketing', 'Accounting/Legal', 'Maintenance', 'Miscellaneous'
        ],
        'Expense': [
            rent_annual, staff_cost_annual, equipment_finance_annual, utilities_annual, 
            supplies_y1, insurance_annual, marketing_y1, accounting_legal_annual, 
            maintenance_annual, miscellaneous_annual
        ]
    }
    df_expenses = pd.DataFrame(expense_data)
    fig_expenses = px.pie(
        df_expenses, 
        values='Expense', 
        names='Category',
        title='Expense Breakdown',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4
    )
    fig_expenses.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        marker=dict(line=dict(color='white', width=2))
    )
    fig_expenses.update_layout(
        font=dict(color='black'),
        legend=dict(orientation='h', yanchor='bottom', y=-0.2),
        paper_bgcolor='white'
    )
    st.plotly_chart(fig_expenses, use_container_width=True)

# Financial metrics
st.subheader("Financial Metrics")
financial_metrics = {
    'Metric': [
        'Initial Investment',
        'Year 1 Revenue',
        'Year 1 EBITDA',
        'Year 1 EBITDA Margin',
        'Year 2 Revenue',
        'Year 2 EBITDA',
        'Year 2 EBITDA Margin',
        'Year 3 Revenue',
        'Year 3 EBITDA',
        'Year 3 EBITDA Margin',
        'Monthly Break-Even (Visits)',
        'Weekly Break-Even (Visits)',
        'Daily Break-Even (Visits)',
        'Payback Period (Months)',
        '1-Year ROI',
        '2-Year ROI',
        '3-Year ROI'
    ],
    'Value': [
        f"£{total_initial_investment:,.0f}",
        f"£{total_revenue_y1:,.0f}",
        f"£{ebitda_y1:,.0f}",
        f"{ebitda_margin_y1:.1f}%",
        f"£{total_revenue_y2:,.0f}",
        f"£{ebitda_y2:,.0f}",
        f"{ebitda_margin_y2:.1f}%",
        f"£{total_revenue_y3:,.0f}",
        f"£{ebitda_y3:,.0f}",
        f"{ebitda_margin_y3:.1f}%",
        f"{monthly_break_even_visits:.0f}",
        f"{weekly_break_even_visits:.0f}",
        f"{daily_break_even_visits:.0f}",
        f"{payback_months:.1f}",
        f"{roi_y1:.1f}%",
        f"{roi_y2:.1f}%",
        f"{roi_y3:.1f}%"
    ]
}
df_metrics = pd.DataFrame(financial_metrics)
st.table(df_metrics)

# Detailed Revenue Breakdown
st.subheader("Detailed Revenue Breakdown")

# Create detailed revenue breakdown table
detailed_revenue = {
    'Service': [
        'Cryotherapy',
        'Infrared Sauna',
        'IV Therapy',
        'Face Treatments',
        'Memberships'
    ],
    'Year 1 Revenue': [
        cryo_revenue_y1,
        sauna_revenue_y1,
        iv_revenue_y1,
        face_revenue_y1,
        membership_revenue_y1
    ],
    'Year 2 Revenue': [
        cryo_revenue_y2,
        sauna_revenue_y2,
        iv_revenue_y2,
        face_revenue_y2,
        membership_revenue_y2
    ],
    'Year 3 Revenue': [
        cryo_revenue_y3,
        sauna_revenue_y3,
        iv_revenue_y3,
        face_revenue_y3,
        membership_revenue_y3
    ]
}

df_detailed_revenue = pd.DataFrame(detailed_revenue)

# Format the numbers
df_detailed_revenue['Year 1 Revenue'] = df_detailed_revenue['Year 1 Revenue'].apply(lambda x: f"£{x:,.0f}")
df_detailed_revenue['Year 2 Revenue'] = df_detailed_revenue['Year 2 Revenue'].apply(lambda x: f"£{x:,.0f}")
df_detailed_revenue['Year 3 Revenue'] = df_detailed_revenue['Year 3 Revenue'].apply(lambda x: f"£{x:,.0f}")

st.table(df_detailed_revenue)

# Detailed Expense Breakdown
st.subheader("Detailed Expense Breakdown")

# Create detailed expense breakdown table
detailed_expenses = {
    'Expense Category': [
        'Rent',
        'Staff Costs',
        'Equipment Finance',
        'Utilities',
        'Supplies',
        'Insurance',
        'Marketing',
        'Accounting/Legal',
        'Maintenance',
        'Miscellaneous'
    ],
    'Year 1 Expense': [
        rent_annual,
        staff_cost_annual,
        equipment_finance_annual,
        utilities_annual,
        supplies_y1,
        insurance_annual,
        marketing_y1,
        accounting_legal_annual,
        maintenance_annual,
        miscellaneous_annual
    ],
    'Year 2 Expense': [
        rent_annual_y2,
        staff_cost_annual_y2,
        equipment_finance_annual,
        utilities_annual_y2,
        supplies_y2,
        insurance_annual_y2,
        marketing_y2,
        accounting_legal_annual_y2,
        maintenance_annual_y2,
        miscellaneous_annual_y2
    ],
    'Year 3 Expense': [
        rent_annual_y3,
        staff_cost_annual_y3,
        equipment_finance_annual,
        utilities_annual_y3,
        supplies_y3,
        insurance_annual_y3,
        marketing_y3,
        accounting_legal_annual_y3,
        maintenance_annual_y3,
        miscellaneous_annual_y3
    ]
}

df_detailed_expenses = pd.DataFrame(detailed_expenses)

# Format the numbers
df_detailed_expenses['Year 1 Expense'] = df_detailed_expenses['Year 1 Expense'].apply(lambda x: f"£{x:,.0f}")
df_detailed_expenses['Year 2 Expense'] = df_detailed_expenses['Year 2 Expense'].apply(lambda x: f"£{x:,.0f}")
df_detailed_expenses['Year 3 Expense'] = df_detailed_expenses['Year 3 Expense'].apply(lambda x: f"£{x:,.0f}")

st.table(df_detailed_expenses)

# Add Budget vs. Actual Tracking
st.subheader("Budget vs. Actual Tracking")

with st.expander("Budget vs. Actual Revenue Tracking"):
    # Create tabs for data entry and visualization
    budget_actual_tab1, budget_actual_tab2 = st.tabs(["Data Entry", "Visualization"])
    
    with budget_actual_tab1:
        st.markdown("### Enter Actual Revenue")
        st.markdown("Track your business's actual revenue against the budget.")
        
        # Create a dataframe with the main revenue categories
        actual_revenue_data = {
            'Service Category': [
                'Cryotherapy',
                'Infrared Sauna',
                'IV Therapy',
                'Face Treatments'
            ],
            'Budgeted Revenue': [
                cryo_revenue_y1,
                sauna_revenue_y1,
                iv_revenue_y1,
                face_revenue_y1
            ],
            'Actual Revenue': [0, 0, 0, 0],
            'Completion (%)': [0, 0, 0, 0]
        }
        
        df_actual_revenue = pd.DataFrame(actual_revenue_data)
        
        # Create input fields for actual revenue and completion percentages
        for i, category in enumerate(df_actual_revenue['Service Category']):
            col1, col2 = st.columns(2)
            with col1:
                actual_revenue = st.number_input(
                    f"Actual Revenue - {category} (£)",
                    min_value=0,
                    value=int(df_actual_revenue.loc[i, 'Actual Revenue']),
                    step=1000
                )
                df_actual_revenue.loc[i, 'Actual Revenue'] = actual_revenue
            
            with col2:
                completion = st.slider(
                    f"Completion % - {category}",
                    min_value=0,
                    max_value=100,
                    value=int(df_actual_revenue.loc[i, 'Completion (%)']),
                    step=5
                )
                df_actual_revenue.loc[i, 'Completion (%)'] = completion
        
        # Calculate variance
        df_actual_revenue['Variance'] = df_actual_revenue['Budgeted Revenue'] - df_actual_revenue['Actual Revenue']
        df_actual_revenue['Variance %'] = (df_actual_revenue['Variance'] / df_actual_revenue['Budgeted Revenue']) * 100
        
        # Format for display
        df_actual_revenue_display = df_actual_revenue.copy()
        df_actual_revenue_display['Budgeted Revenue'] = df_actual_revenue_display['Budgeted Revenue'].apply(lambda x: f"£{x:,.0f}")
        df_actual_revenue_display['Actual Revenue'] = df_actual_revenue_display['Actual Revenue'].apply(lambda x: f"£{x:,.0f}")
        df_actual_revenue_display['Variance'] = df_actual_revenue_display['Variance'].apply(lambda x: f"£{x:,.0f}")
        df_actual_revenue_display['Variance %'] = df_actual_revenue_display['Variance %'].apply(lambda x: f"{x:.1f}%")
        df_actual_revenue_display['Completion (%)'] = df_actual_revenue_display['Completion (%)'].apply(lambda x: f"{x}%")
        
        st.table(df_actual_revenue_display)
    
    with budget_actual_tab2:
        # Create visualizations for budget vs actual
        st.markdown("### Budget vs. Actual Visualization")
        
        # Bar chart comparing budget vs actual
        budget_vs_actual_data = pd.DataFrame({
            'Category': df_actual_revenue['Service Category'],
            'Budgeted': df_actual_revenue['Budgeted Revenue'],
            'Actual': df_actual_revenue['Actual Revenue']
        })
        
        budget_vs_actual_melted = pd.melt(
            budget_vs_actual_data, 
            id_vars=['Category'],
            value_vars=['Budgeted', 'Actual'],
            var_name='Type',
            value_name='Revenue'
        )
        
        fig_budget_actual = px.bar(
            budget_vs_actual_melted,
            x='Category',
            y='Revenue',
            color='Type',
            barmode='group',
            title="Budget vs. Actual Revenue by Service",
            labels={'Revenue': 'Revenue (£)', 'Category': 'Service Category'},
            color_discrete_map={
                'Budgeted': 'blue',
                'Actual': 'green'
            }
        )
        
        fig_budget_actual.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='black'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        st.plotly_chart(fig_budget_actual, use_container_width=True)
        
        # Calculate overall project completion and budget status
        total_budget = sum(df_actual_revenue['Budgeted Revenue'])
        total_actual = sum(df_actual_revenue['Actual Revenue'])
        budget_variance = total_budget - total_actual
        budget_variance_pct = (budget_variance / total_budget) * 100 if total_budget > 0 else 0
        weighted_completion = sum(df_actual_revenue['Completion (%)'] * df_actual_revenue['Budgeted Revenue']) / total_budget if total_budget > 0 else 0
        
        # Create KPI metrics for business status
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Completion", f"{weighted_completion:.1f}%")
        with col2:
            st.metric("Budget Variance", f"£{budget_variance:,.0f}", f"{budget_variance_pct:.1f}%")
        with col3:
            status = "On Budget" if abs(budget_variance_pct) < 5 else ("Over Budget" if budget_variance_pct < 0 else "Under Budget")
            st.metric("Budget Status", status)

# Sensitivity Analysis
st.subheader("Sensitivity Analysis")

with st.expander("Profit Sensitivity Analysis"):
    # 1. Price sensitivity
    st.subheader("Price Sensitivity")
    price_variations = np.linspace(0.8, 1.2, 9)  # 80% to 120% of current prices
    price_ebitda_results = []
    price_margin_results = []
    
    for price_factor in price_variations:
        # Recalculate revenues with adjusted prices
        new_cryo_revenue = cryotherapy_price * price_factor * cryotherapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * cryo_util_y1
        new_sauna_revenue = infrared_sauna_price * price_factor * infrared_sauna_capacity_per_hour * operating_hours_weekly * weeks_per_year * sauna_util_y1
        new_iv_revenue = avg_iv_therapy_price * price_factor * iv_therapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * iv_util_y1
        new_face_revenue = face_treatment_price * price_factor * face_treatment_capacity_per_hour * operating_hours_weekly * weeks_per_year * face_util_y1
        
        new_total_revenue = new_cryo_revenue + new_sauna_revenue + new_iv_revenue + new_face_revenue
        
        # Recalculate variable expenses
        new_supplies = new_total_revenue * (supplies_percent_of_revenue / 100)
        new_marketing = new_total_revenue * (marketing_percent_of_revenue_y1 / 100)
        
        # Fixed expenses remain the same
        new_total_expenses = (
            rent_annual + 
            staff_cost_annual + 
            equipment_finance_annual + 
            utilities_annual + 
            new_supplies + 
            insurance_annual + 
            new_marketing + 
            accounting_legal_annual + 
            maintenance_annual + 
            miscellaneous_annual
        )
        
        new_ebitda = new_total_revenue - new_total_expenses
        new_margin = (new_ebitda / new_total_revenue) * 100 if new_total_revenue > 0 else 0
        
        price_ebitda_results.append(new_ebitda)
        price_margin_results.append(new_margin)
    
    price_sensitivity_df = pd.DataFrame({
        'Price Factor': [f"{factor:.1f}x" for factor in price_variations],
        'EBITDA (£)': [f"£{ebitda:,.0f}" for ebitda in price_ebitda_results],
        'EBITDA Margin (%)': [f"{margin:.1f}%" for margin in price_margin_results]
    })
    
    st.table(price_sensitivity_df)
    
    fig_price_sensitivity = px.line(
        x=price_variations, 
        y=price_ebitda_results,
        labels={'x': 'Price Factor', 'y': 'EBITDA (£)'},
        title="EBITDA Sensitivity to Pricing"
    )
    fig_price_sensitivity.update_traces(
        line=dict(color='blue', width=3),
        mode='lines+markers',
        marker=dict(size=8, color='blue')
    )
    fig_price_sensitivity.add_hline(
        y=ebitda_y1,
        line=dict(color='red', width=1, dash='dash'),
        annotation_text="Current EBITDA",
        annotation_position="bottom right"
    )
    fig_price_sensitivity.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        xaxis=dict(gridcolor='white', linecolor='white', tickformat='.1f'),
        yaxis=dict(gridcolor='white', linecolor='white'),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_price_sensitivity, use_container_width=True)

    # 2. Utilization sensitivity
    st.subheader("Utilization Sensitivity")
    utilization_variations = np.linspace(0.5, 1.5, 9)  # 50% to 150% of current utilization
    utilization_ebitda_results = []
    utilization_margin_results = []
    
    for util_factor in utilization_variations:
        # Recalculate revenues with adjusted utilization
        new_cryo_util = min((year1_avg_utilization / 100) * cryotherapy_utilization_factor * util_factor, 1.0)
        new_sauna_util = min((year1_avg_utilization / 100) * infrared_sauna_utilization_factor * util_factor, 1.0)
        new_iv_util = min((year1_avg_utilization / 100) * iv_therapy_utilization_factor * util_factor, 1.0)
        new_face_util = min((year1_avg_utilization / 100) * face_treatment_utilization_factor * util_factor, 1.0)
        
        new_cryo_revenue = cryotherapy_price * cryotherapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * new_cryo_util
        new_sauna_revenue = infrared_sauna_price * infrared_sauna_capacity_per_hour * operating_hours_weekly * weeks_per_year * new_sauna_util
        new_iv_revenue = avg_iv_therapy_price * iv_therapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * new_iv_util
        new_face_revenue = face_treatment_price * face_treatment_capacity_per_hour * operating_hours_weekly * weeks_per_year * new_face_util
        
        new_total_revenue = new_cryo_revenue + new_sauna_revenue + new_iv_revenue + new_face_revenue
        
        # Recalculate variable expenses
        new_supplies = new_total_revenue * (supplies_percent_of_revenue / 100)
        new_marketing = new_total_revenue * (marketing_percent_of_revenue_y1 / 100)
        
        # Fixed expenses remain the same
        new_total_expenses = (
            rent_annual + 
            staff_cost_annual + 
            equipment_finance_annual + 
            utilities_annual + 
            new_supplies + 
            insurance_annual + 
            new_marketing + 
            accounting_legal_annual + 
            maintenance_annual + 
            miscellaneous_annual
        )
        
        new_ebitda = new_total_revenue - new_total_expenses
        new_margin = (new_ebitda / new_total_revenue) * 100 if new_total_revenue > 0 else 0
        
        utilization_ebitda_results.append(new_ebitda)
        utilization_margin_results.append(new_margin)
    
    utilization_sensitivity_df = pd.DataFrame({
        'Utilization Factor': [f"{factor:.1f}x" for factor in utilization_variations],
        'EBITDA (£)': [f"£{ebitda:,.0f}" for ebitda in utilization_ebitda_results],
        'EBITDA Margin (%)': [f"{margin:.1f}%" for margin in utilization_margin_results]
    })
    
    st.table(utilization_sensitivity_df)
    
    fig_utilization_sensitivity = px.line(
        x=utilization_variations, 
        y=utilization_ebitda_results,
        labels={'x': 'Utilization Factor', 'y': 'EBITDA (£)'},
        title="EBITDA Sensitivity to Utilization"
    )
    fig_utilization_sensitivity.update_traces(
        line=dict(color='green', width=3),
        mode='lines+markers',
        marker=dict(size=8, color='green')
    )
    fig_utilization_sensitivity.add_hline(
        y=ebitda_y1,
        line=dict(color='red', width=1, dash='dash'),
        annotation_text="Current EBITDA",
        annotation_position="bottom right"
    )
    fig_utilization_sensitivity.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        xaxis=dict(gridcolor='white', linecolor='white', tickformat='.1f'),
        yaxis=dict(gridcolor='white', linecolor='white'),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_utilization_sensitivity, use_container_width=True)

# Scenario Comparison
st.subheader("Scenario Comparison")

with st.expander("Compare Different Scenarios"):
    st.markdown("### Create and Compare Business Scenarios")
    
    # Create tabs for different scenarios
    scenario_tab1, scenario_tab2, scenario_tab3 = st.tabs(["Base Case", "Optimistic", "Pessimistic"])
    
    # Base case (current values)
    with scenario_tab1:
        st.markdown("#### Base Case Scenario")
        st.markdown("Current business parameters")
        
        base_metrics = {
            'Metric': [
                'Year 1 Revenue (£)',
                'Year 1 EBITDA (£)',
                'Year 1 EBITDA Margin (%)',
                'Year 3 Revenue (£)',
                'Year 3 EBITDA (£)',
                'Year 3 EBITDA Margin (%)',
                'Break-Even (Daily Visits)',
                'Payback Period (Months)'
            ],
            'Value': [
                f"{total_revenue_y1:,.0f}",
                f"{ebitda_y1:,.0f}",
                f"{ebitda_margin_y1:.1f}",
                f"{total_revenue_y3:,.0f}",
                f"{ebitda_y3:,.0f}",
                f"{ebitda_margin_y3:.1f}",
                f"{daily_break_even_visits:.1f}",
                f"{payback_months:.1f}"
            ]
        }
        
        st.table(pd.DataFrame(base_metrics))
    
    # Optimistic scenario
    with scenario_tab2:
        st.markdown("#### Optimistic Scenario")
        
        # Optimistic adjustments
        opt_price_factor = 1.1  # 10% higher prices
        opt_util_factor = 1.2   # 20% higher utilization
        opt_supplies_percent = supplies_percent_of_revenue - 2  # 2% lower supplies cost
        
        # Recalculate with optimistic values for Year 1
        opt_cryo_util_y1 = min((year1_avg_utilization / 100) * cryotherapy_utilization_factor * opt_util_factor, 1.0)
        opt_sauna_util_y1 = min((year1_avg_utilization / 100) * infrared_sauna_utilization_factor * opt_util_factor, 1.0)
        opt_iv_util_y1 = min((year1_avg_utilization / 100) * iv_therapy_utilization_factor * opt_util_factor, 1.0)
        opt_face_util_y1 = min((year1_avg_utilization / 100) * face_treatment_utilization_factor * opt_util_factor, 1.0)
        
        opt_cryo_revenue_y1 = cryotherapy_price * opt_price_factor * cryotherapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * opt_cryo_util_y1
        opt_sauna_revenue_y1 = infrared_sauna_price * opt_price_factor * infrared_sauna_capacity_per_hour * operating_hours_weekly * weeks_per_year * opt_sauna_util_y1
        opt_iv_revenue_y1 = avg_iv_therapy_price * opt_price_factor * iv_therapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * opt_iv_util_y1
        opt_face_revenue_y1 = face_treatment_price * opt_price_factor * face_treatment_capacity_per_hour * operating_hours_weekly * weeks_per_year * opt_face_util_y1
        
        opt_total_revenue_y1 = opt_cryo_revenue_y1 + opt_sauna_revenue_y1 + opt_iv_revenue_y1 + opt_face_revenue_y1 + membership_revenue_y1
        
        opt_supplies_y1 = opt_total_revenue_y1 * (opt_supplies_percent / 100)
        opt_marketing_y1 = opt_total_revenue_y1 * (marketing_percent_of_revenue_y1 / 100)
        
        opt_total_expenses_y1 = (
            rent_annual + 
            staff_cost_annual + 
            equipment_finance_annual + 
            utilities_annual + 
            opt_supplies_y1 + 
            insurance_annual + 
            opt_marketing_y1 + 
            accounting_legal_annual + 
            maintenance_annual + 
            miscellaneous_annual
        )
        
        opt_ebitda_y1 = opt_total_revenue_y1 - opt_total_expenses_y1
        opt_ebitda_margin_y1 = (opt_ebitda_y1 / opt_total_revenue_y1) * 100 if opt_total_revenue_y1 > 0 else 0
        
        # Optimistic Year 3
        opt_cryo_util_y3 = min((year3_utilization / 100) * cryotherapy_utilization_factor * opt_util_factor, 1.0)
        opt_sauna_util_y3 = min((year3_utilization / 100) * infrared_sauna_utilization_factor * opt_util_factor, 1.0)
        opt_iv_util_y3 = min((year3_utilization / 100) * iv_therapy_utilization_factor * opt_util_factor, 1.0)
        opt_face_util_y3 = min((year3_utilization / 100) * face_treatment_utilization_factor * opt_util_factor, 1.0)
        
        # Year 3 prices with optimistic increases
        opt_cryo_price_y3 = cryotherapy_price * (1 + price_increase_y2 / 100) * (1 + price_increase_y3 / 100) * opt_price_factor
        opt_sauna_price_y3 = infrared_sauna_price * (1 + price_increase_y2 / 100) * (1 + price_increase_y3 / 100) * opt_price_factor
        opt_iv_price_y3 = avg_iv_therapy_price * (1 + price_increase_y2 / 100) * (1 + price_increase_y3 / 100) * opt_price_factor
        opt_face_price_y3 = face_treatment_price * (1 + price_increase_y2 / 100) * (1 + price_increase_y3 / 100) * opt_price_factor
        
        opt_cryo_revenue_y3 = opt_cryo_price_y3 * cryotherapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * opt_cryo_util_y3
        opt_sauna_revenue_y3 = opt_sauna_price_y3 * infrared_sauna_capacity_per_hour * operating_hours_weekly * weeks_per_year * opt_sauna_util_y3
        opt_iv_revenue_y3 = opt_iv_price_y3 * iv_therapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * opt_iv_util_y3
        opt_face_revenue_y3 = opt_face_price_y3 * face_treatment_capacity_per_hour * operating_hours_weekly * weeks_per_year * opt_face_util_y3
        
        opt_total_revenue_y3 = opt_cryo_revenue_y3 + opt_sauna_revenue_y3 + opt_iv_revenue_y3 + opt_face_revenue_y3 + membership_revenue_y3
        
        opt_supplies_y3 = opt_total_revenue_y3 * (opt_supplies_percent / 100)
        opt_marketing_y3 = opt_total_revenue_y3 * (marketing_percent_of_revenue / 100)
        
        # Other Year 3 expenses remain the same as base case
        opt_total_expenses_y3 = (
            rent_annual_y3 + 
            staff_cost_annual_y3 + 
            equipment_finance_annual + 
            utilities_annual_y3 + 
            opt_supplies_y3 + 
            insurance_annual_y3 + 
            opt_marketing_y3 + 
            accounting_legal_annual_y3 + 
            maintenance_annual_y3 + 
            miscellaneous_annual_y3
        )
        
        opt_ebitda_y3 = opt_total_revenue_y3 - opt_total_expenses_y3
        opt_ebitda_margin_y3 = (opt_ebitda_y3 / opt_total_revenue_y3) * 100 if opt_total_revenue_y3 > 0 else 0
        
        # Optimistic break-even and payback
        opt_avg_service_price = avg_service_price * opt_price_factor
        opt_avg_variable_cost_per_visit = opt_avg_service_price * ((opt_supplies_percent + marketing_percent_of_revenue_y1) / 100)
        opt_contribution_margin_per_visit = opt_avg_service_price - opt_avg_variable_cost_per_visit
        
        opt_daily_break_even_visits = (monthly_fixed_costs / opt_contribution_margin_per_visit) / 26  # 26 days per month
        opt_monthly_ebitda_y1 = opt_ebitda_y1 / 12
        opt_payback_months = total_initial_investment / opt_monthly_ebitda_y1 if opt_monthly_ebitda_y1 > 0 else float('inf')
        
        # Display optimistic metrics
        opt_metrics = {
            'Metric': [
                'Year 1 Revenue (£)',
                'Year 1 EBITDA (£)',
                'Year 1 EBITDA Margin (%)',
                'Year 3 Revenue (£)',
                'Year 3 EBITDA (£)',
                'Year 3 EBITDA Margin (%)',
                'Break-Even (Daily Visits)',
                'Payback Period (Months)'
            ],
            'Value': [
                f"{opt_total_revenue_y1:,.0f}",
                f"{opt_ebitda_y1:,.0f}",
                f"{opt_ebitda_margin_y1:.1f}",
                f"{opt_total_revenue_y3:,.0f}",
                f"{opt_ebitda_y3:,.0f}",
                f"{opt_ebitda_margin_y3:.1f}",
                f"{opt_daily_break_even_visits:.1f}",
                f"{opt_payback_months:.1f}"
            ],
            'Change from Base': [
                f"{((opt_total_revenue_y1/total_revenue_y1)-1)*100:+.1f}%",
                f"{((opt_ebitda_y1/ebitda_y1)-1)*100:+.1f}%",
                f"{opt_ebitda_margin_y1-ebitda_margin_y1:+.1f}%",
                f"{((opt_total_revenue_y3/total_revenue_y3)-1)*100:+.1f}%",
                f"{((opt_ebitda_y3/ebitda_y3)-1)*100:+.1f}%",
                f"{opt_ebitda_margin_y3-ebitda_margin_y3:+.1f}%",
                f"{opt_daily_break_even_visits-daily_break_even_visits:+.1f}",
                f"{opt_payback_months-payback_months:+.1f}"
            ]
        }
        
        st.table(pd.DataFrame(opt_metrics))
        
        # Key assumptions
        st.markdown("**Key Assumptions:**")
        st.markdown(f"- Service prices increased by 10%")
        st.markdown(f"- Utilization rates increased by 20%")
        st.markdown(f"- Supplies cost reduced by 2%")
        
    # Pessimistic scenario
    with scenario_tab3:
        st.markdown("#### Pessimistic Scenario")
        
        # Pessimistic adjustments
        pes_price_factor = 0.9  # 10% lower prices
        pes_util_factor = 0.8   # 20% lower utilization
        pes_supplies_percent = supplies_percent_of_revenue + 2  # 2% higher supplies cost
        
        # Recalculate with pessimistic values for Year 1
        pes_cryo_util_y1 = min((year1_avg_utilization / 100) * cryotherapy_utilization_factor * pes_util_factor, 1.0)
        pes_sauna_util_y1 = min((year1_avg_utilization / 100) * infrared_sauna_utilization_factor * pes_util_factor, 1.0)
        pes_iv_util_y1 = min((year1_avg_utilization / 100) * iv_therapy_utilization_factor * pes_util_factor, 1.0)
        pes_face_util_y1 = min((year1_avg_utilization / 100) * face_treatment_utilization_factor * pes_util_factor, 1.0)
        
        pes_cryo_revenue_y1 = cryotherapy_price * pes_price_factor * cryotherapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * pes_cryo_util_y1
        pes_sauna_revenue_y1 = infrared_sauna_price * pes_price_factor * infrared_sauna_capacity_per_hour * operating_hours_weekly * weeks_per_year * pes_sauna_util_y1
        pes_iv_revenue_y1 = avg_iv_therapy_price * pes_price_factor * iv_therapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * pes_iv_util_y1
        pes_face_revenue_y1 = face_treatment_price * pes_price_factor * face_treatment_capacity_per_hour * operating_hours_weekly * weeks_per_year * pes_face_util_y1
        
        pes_total_revenue_y1 = pes_cryo_revenue_y1 + pes_sauna_revenue_y1 + pes_iv_revenue_y1 + pes_face_revenue_y1 + membership_revenue_y1
        
        pes_supplies_y1 = pes_total_revenue_y1 * (pes_supplies_percent / 100)
        pes_marketing_y1 = pes_total_revenue_y1 * (marketing_percent_of_revenue_y1 / 100)
        
        # Other Year 1 expenses remain the same
        pes_total_expenses_y1 = (
            rent_annual + 
            staff_cost_annual + 
            equipment_finance_annual + 
            utilities_annual + 
            pes_supplies_y1 + 
            insurance_annual + 
            pes_marketing_y1 + 
            accounting_legal_annual + 
            maintenance_annual + 
            miscellaneous_annual
        )
        
        pes_ebitda_y1 = pes_total_revenue_y1 - pes_total_expenses_y1
        pes_ebitda_margin_y1 = (pes_ebitda_y1 / pes_total_revenue_y1) * 100 if pes_total_revenue_y1 > 0 else 0
        
        # Pessimistic Year 3
        pes_cryo_util_y3 = min((year3_utilization / 100) * cryotherapy_utilization_factor * pes_util_factor, 1.0)
        pes_sauna_util_y3 = min((year3_utilization / 100) * infrared_sauna_utilization_factor * pes_util_factor, 1.0)
        pes_iv_util_y3 = min((year3_utilization / 100) * iv_therapy_utilization_factor * pes_util_factor, 1.0)
        pes_face_util_y3 = min((year3_utilization / 100) * face_treatment_utilization_factor * pes_util_factor, 1.0)
        
        # Year 3 prices with pessimistic decreases
        pes_cryo_price_y3 = cryotherapy_price * (1 - price_increase_y2 / 100) * (1 - price_increase_y3 / 100) * pes_price_factor
        pes_sauna_price_y3 = infrared_sauna_price * (1 - price_increase_y2 / 100) * (1 - price_increase_y3 / 100) * pes_price_factor
        pes_iv_price_y3 = avg_iv_therapy_price * (1 - price_increase_y2 / 100) * (1 - price_increase_y3 / 100) * pes_price_factor
        pes_face_price_y3 = face_treatment_price * (1 - price_increase_y2 / 100) * (1 - price_increase_y3 / 100) * pes_price_factor
        
        pes_cryo_revenue_y3 = pes_cryo_price_y3 * cryotherapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * pes_cryo_util_y3
        pes_sauna_revenue_y3 = pes_sauna_price_y3 * infrared_sauna_capacity_per_hour * operating_hours_weekly * weeks_per_year * pes_sauna_util_y3
        pes_iv_revenue_y3 = pes_iv_price_y3 * iv_therapy_capacity_per_hour * operating_hours_weekly * weeks_per_year * pes_iv_util_y3
        pes_face_revenue_y3 = pes_face_price_y3 * face_treatment_capacity_per_hour * operating_hours_weekly * weeks_per_year * pes_face_util_y3
        
        pes_total_revenue_y3 = pes_cryo_revenue_y3 + pes_sauna_revenue_y3 + pes_iv_revenue_y3 + pes_face_revenue_y3 + membership_revenue_y3
        
        pes_supplies_y3 = pes_total_revenue_y3 * (pes_supplies_percent / 100)
        pes_marketing_y3 = pes_total_revenue_y3 * (marketing_percent_of_revenue / 100)
        
        # Other Year 3 expenses remain the same as base case
        pes_total_expenses_y3 = (
            rent_annual_y3 + 
            staff_cost_annual_y3 + 
            equipment_finance_annual + 
            utilities_annual_y3 + 
            pes_supplies_y3 + 
            insurance_annual_y3 + 
            pes_marketing_y3 + 
            accounting_legal_annual_y3 + 
            maintenance_annual_y3 + 
            miscellaneous_annual_y3
        )
        
        pes_ebitda_y3 = pes_total_revenue_y3 - pes_total_expenses_y3
        pes_ebitda_margin_y3 = (pes_ebitda_y3 / pes_total_revenue_y3) * 100 if pes_total_revenue_y3 > 0 else 0
        
        # Pessimistic break-even and payback
        pes_avg_service_price = avg_service_price * pes_price_factor
        pes_avg_variable_cost_per_visit = pes_avg_service_price * ((pes_supplies_percent + marketing_percent_of_revenue_y1) / 100)
        pes_contribution_margin_per_visit = pes_avg_service_price - pes_avg_variable_cost_per_visit
        
        pes_daily_break_even_visits = (monthly_fixed_costs / pes_contribution_margin_per_visit) / 26  # 26 days per month
        pes_monthly_ebitda_y1 = pes_ebitda_y1 / 12
        pes_payback_months = total_initial_investment / pes_monthly_ebitda_y1 if pes_monthly_ebitda_y1 > 0 else float('inf')
        
        # Display pessimistic metrics
        pes_metrics = {
            'Metric': [
                'Year 1 Revenue (£)',
                'Year 1 EBITDA (£)',
                'Year 1 EBITDA Margin (%)',
                'Year 3 Revenue (£)',
                'Year 3 EBITDA (£)',
                'Year 3 EBITDA Margin (%)',
                'Break-Even (Daily Visits)',
                'Payback Period (Months)'
            ],
            'Value': [
                f"{pes_total_revenue_y1:,.0f}",
                f"{pes_ebitda_y1:,.0f}",
                f"{pes_ebitda_margin_y1:.1f}",
                f"{pes_total_revenue_y3:,.0f}",
                f"{pes_ebitda_y3:,.0f}",
                f"{pes_ebitda_margin_y3:.1f}",
                f"{pes_daily_break_even_visits:.1f}",
                f"{pes_payback_months:.1f}"
            ],
            'Change from Base': [
                f"{((pes_total_revenue_y1/total_revenue_y1)-1)*100:+.1f}%",
                f"{((pes_ebitda_y1/ebitda_y1)-1)*100:+.1f}%" if ebitda_y1 != 0 else "N/A",
                f"{pes_ebitda_margin_y1-ebitda_margin_y1:+.1f}%",
                f"{((pes_total_revenue_y3/total_revenue_y3)-1)*100:+.1f}%",
                f"{((pes_ebitda_y3/ebitda_y3)-1)*100:+.1f}%" if ebitda_y3 != 0 else "N/A",
                f"{pes_ebitda_margin_y3-ebitda_margin_y3:+.1f}%",
                f"{pes_daily_break_even_visits-daily_break_even_visits:+.1f}" if pes_daily_break_even_visits != float('inf') else "N/A",
                f"{pes_payback_months-payback_months:+.1f}" if pes_payback_months != float('inf') else "N/A"
            ]
        }
        
        st.table(pd.DataFrame(pes_metrics))
        
        # Key assumptions
        st.markdown("**Key Assumptions:**")
        st.markdown(f"- Service prices decreased by 10%")
        st.markdown(f"- Utilization rates decreased by 20%")
        st.markdown(f"- Supplies cost increased by 2% of revenue")

# Compare all scenarios in a chart
st.subheader("Scenario Comparison Chart")

# Create data for comparison chart
scenario_names = ["Pessimistic", "Base Case", "Optimistic"]
y1_revenue_data = [pes_total_revenue_y1, total_revenue_y1, opt_total_revenue_y1]
y1_ebitda_data = [pes_ebitda_y1, ebitda_y1, opt_ebitda_y1]
y3_revenue_data = [pes_total_revenue_y3, total_revenue_y3, opt_total_revenue_y3]
y3_ebitda_data = [pes_ebitda_y3, ebitda_y3, opt_ebitda_y3]

# Create figure
fig_scenarios = go.Figure()

# Add Year 1 Revenue bars
fig_scenarios.add_trace(go.Bar(
    x=scenario_names,
    y=y1_revenue_data,
    name="Year 1 Revenue",
    marker_color='lightblue',
    text=[f"£{x:,.0f}" for x in y1_revenue_data],
    textposition='auto'
))

# Add Year 1 EBITDA bars
fig_scenarios.add_trace(go.Bar(
    x=scenario_names,
    y=y1_ebitda_data,
    name="Year 1 EBITDA",
    marker_color='darkblue',
    text=[f"£{x:,.0f}" for x in y1_ebitda_data],
    textposition='auto'
))

# Add Year 3 Revenue bars
fig_scenarios.add_trace(go.Bar(
    x=scenario_names,
    y=y3_revenue_data,
    name="Year 3 Revenue",
    marker_color='lightgreen',
    text=[f"£{x:,.0f}" for x in y3_revenue_data],
    textposition='auto'
))

# Add Year 3 EBITDA bars
fig_scenarios.add_trace(go.Bar(
    x=scenario_names,
    y=y3_ebitda_data,
    name="Year 3 EBITDA",
    marker_color='darkgreen',
    text=[f"£{x:,.0f}" for x in y3_ebitda_data],
    textposition='auto'
))

# Update layout
fig_scenarios.update_layout(
    title='Financial Comparison Across Scenarios',
    barmode='group',
    xaxis=dict(title='Scenario'),
    yaxis=dict(title='Amount (£)'),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='black')
)

st.plotly_chart(fig_scenarios, use_container_width=True)

# Business Recommendations
st.subheader("Business Recommendations")

with st.expander("Key Recommendations", expanded=True):
    st.markdown("### Strategic Recommendations")
    
    # Generate recommendations based on the analysis
    recommendations = []
    
    # Pricing recommendations
    if ebitda_margin_y1 < 20:
        recommendations.append("**Pricing Strategy**: Consider increasing prices as the sensitivity analysis shows significant impact on profitability.")
    else:
        recommendations.append("**Pricing Strategy**: Current pricing appears optimal. Focus on maintaining premium positioning while monitoring competitor pricing.")
    
    # Utilization recommendations
    if year1_avg_utilization < 30:
        recommendations.append("**Utilization Improvement**: Implement targeted marketing campaigns to increase utilization, which has the strongest impact on profitability.")
    else:
        recommendations.append("**Capacity Management**: Current utilization projections are healthy. Consider expanding capacity for high-demand services if utilization exceeds 70%.")
    
    # Cost management
    if supplies_percent_of_revenue > 18:
        recommendations.append("**Cost Management**: Explore opportunities to reduce supplies costs through bulk purchasing or alternative suppliers.")
    
    # Service mix recommendations
    service_revenues = [cryo_revenue_y1, sauna_revenue_y1, iv_revenue_y1, face_revenue_y1]
    service_names = ["Cryotherapy", "Infrared Sauna", "IV Therapy", "Face Treatments"]
    highest_revenue_service = service_names[service_revenues.index(max(service_revenues))]
    lowest_revenue_service = service_names[service_revenues.index(min(service_revenues))]
    
    recommendations.append(f"**Service Mix Optimization**: Focus marketing efforts on {highest_revenue_service}, which generates the highest revenue. Consider enhancing the offering for {lowest_revenue_service} to improve its performance.")
    
    # Membership recommendations
    recommendations.append("**Membership Program**: Actively promote membership options to create recurring revenue and improve cash flow predictability.")
    
    # Financial recommendations
    if payback_months > 24:
        recommendations.append("**Financial Planning**: The current payback period exceeds 24 months. Consider phasing equipment purchases or negotiating better financing terms.")
    else:
        recommendations.append("**Expansion Planning**: With a healthy payback period, begin planning for potential expansion or additional service offerings after year 2.")
    
    # Display recommendations
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")
    
    # Risk factors
    st.markdown("### Key Risk Factors")
    
    risk_factors = [
        "**Market Competition**: New competitors entering the market could impact both utilization and pricing power.",
        "**Utilization Assumptions**: The forecast assumes steady customer adoption. If utilization rates are 25% lower than projected, EBITDA would decrease significantly.",
        "**Equipment Downtime**: Specialized equipment failures could impact revenue if replacement/repair timeframes are lengthy.",
        "**Regulatory Changes**: Changes in regulations around IV therapy or other treatments could impact operations.",
        "**Staff Retention**: Skilled staff are essential for service delivery. High turnover could impact quality and customer satisfaction."
    ]
    
    for i, risk in enumerate(risk_factors, 1):
        st.markdown(f"{i}. {risk}")

# PDF Report Generation
st.subheader("Generate PDF Report")

def create_pdf_report(business_name, location, business_type, size_sqft, total_revenue_y1, total_expenses_y1, 
                     ebitda_y1, ebitda_margin_y1, roi_y3, fig_revenue_expense, fig_revenue, df_metrics, 
                     df_detailed_revenue, fig_scenarios, recommendations):
    """
    Create a PDF report with the financial analysis
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Add title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'{business_name} - Financial Analysis', 0, 1, 'C')
    
    # Add business details
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Location: {location}', 0, 1, 'L')
    pdf.cell(0, 10, f'Business Type: {business_type}', 0, 1, 'L')
    pdf.cell(0, 10, f'Size: {size_sqft} sq ft', 0, 1, 'L')
    pdf.cell(0, 10, f'Report Date: {datetime.now().strftime("%d %b %Y")}', 0, 1, 'L')
    
    pdf.ln(5)
    
    # Add key metrics
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Key Financial Metrics', 0, 1, 'L')
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Year 1 Revenue: £{total_revenue_y1:,.0f}', 0, 1, 'L')
    pdf.cell(0, 10, f'Year 1 Expenses: £{total_expenses_y1:,.0f}', 0, 1, 'L')
    pdf.cell(0, 10, f'Year 1 EBITDA: £{ebitda_y1:,.0f}', 0, 1, 'L')
    pdf.cell(0, 10, f'Year 1 EBITDA Margin: {ebitda_margin_y1:.1f}%', 0, 1, 'L')
    pdf.cell(0, 10, f'3-Year ROI: {roi_y3:.1f}%', 0, 1, 'L')
    
    pdf.ln(5)
    
    # Add revenue and expense chart
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Revenue & Expense Projection', 0, 1, 'L')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        pio.write_image(fig_revenue_expense, tmp.name, width=800, height=400)
        pdf.image(tmp.name, x=10, y=None, w=190)
        os.unlink(tmp.name)
    
    pdf.ln(5)
    
    # Add revenue breakdown chart
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Revenue Breakdown by Service', 0, 1, 'L')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        pio.write_image(fig_revenue, tmp.name, width=800, height=400)
        pdf.image(tmp.name, x=10, y=None, w=190)
        os.unlink(tmp.name)
    
    pdf.ln(5)
    
    # Add financial metrics table
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Financial Metrics', 0, 1, 'L')
    
    # Convert DataFrame to table in PDF
    pdf.set_font('Arial', 'B', 10)
    col_width = 95
    row_height = 10
    
    # Header
    pdf.cell(col_width, row_height, 'Metric', 1, 0, 'C')
    pdf.cell(col_width, row_height, 'Value', 1, 1, 'C')
    
    # Data rows
    pdf.set_font('Arial', '', 10)
    for i in range(len(df_metrics)):
        pdf.cell(col_width, row_height, df_metrics.iloc[i, 0], 1, 0, 'L')
        pdf.cell(col_width, row_height, df_metrics.iloc[i, 1], 1, 1, 'R')
    
    pdf.ln(10)
    
    # Add detailed revenue table
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Detailed Revenue Breakdown', 0, 1, 'L')
    
    # Convert DataFrame to table in PDF
    pdf.set_font('Arial', 'B', 10)
    col_width = 47.5
    
    # Header
    pdf.cell(col_width, row_height, 'Service', 1, 0, 'C')
    pdf.cell(col_width, row_height, 'Year 1', 1, 0, 'C')
    pdf.cell(col_width, row_height, 'Year 2', 1, 0, 'C')
    pdf.cell(col_width, row_height, 'Year 3', 1, 1, 'C')
    
    # Data rows
    pdf.set_font('Arial', '', 10)
    for i in range(len(df_detailed_revenue)):
        pdf.cell(col_width, row_height, df_detailed_revenue.iloc[i, 0], 1, 0, 'L')
        pdf.cell(col_width, row_height, df_detailed_revenue.iloc[i, 1], 1, 0, 'R')
        pdf.cell(col_width, row_height, df_detailed_revenue.iloc[i, 2], 1, 0, 'R')
        pdf.cell(col_width, row_height, df_detailed_revenue.iloc[i, 3], 1, 1, 'R')
    
    pdf.ln(10)
    
    # Scenario comparison
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Scenario Comparison', 0, 1, 'L')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        pio.write_image(fig_scenarios, tmp.name, width=800, height=400)
        pdf.image(tmp.name, x=10, y=None, w=190)
        os.unlink(tmp.name)
    
    pdf.ln(5)
    
    # Recommendations
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Recommendations', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    
    for i, rec in enumerate(recommendations, 1):
        pdf.multi_cell(0, 10, f"{i}. {rec}")
    
    pdf.ln(5)
    
    # Footer
    pdf.set_y(-30)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 10, f'Longevity Clinic Financial Report - Generated on {datetime.now().strftime("%d %b %Y")}', 0, 0, 'C')
    
    return pdf

# Email functionality
def send_email(email_address, pdf_data, business_name):
    """
    Send the PDF report via email
    """
    try:
        # This is a placeholder - in a real application, you would use your own SMTP server
        # and credentials. For security reasons, these should be stored as environment variables.
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_username = os.environ.get('SMTP_USERNAME', '')
        smtp_password = os.environ.get('SMTP_PASSWORD', '')
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email_address
        msg['Subject'] = f"Longevity Clinic Financial Report: {business_name}"
        
        # Email body
        body = f"""
        Dear Client,
        
        Please find attached the financial report for {business_name}.
        
        This report includes financial metrics, revenue projections, cost breakdowns, and recommendations.
        
        Best regards,
        Longevity Clinic Dashboard
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        attachment = MIMEApplication(pdf_data, _subtype='pdf')
        attachment.add_header('Content-Disposition', 'attachment', filename=f"{business_name}_report.pdf")
        msg.attach(attachment)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

# Add export options
st.markdown("---")
export_col1, export_col2 = st.columns([3, 1])

with export_col1:
    email_address = st.text_input("Email address for report delivery (optional)")

with export_col2:
    export_button = st.button("Generate PDF Report")

if export_button:
    with st.spinner("Generating PDF report..."):
        # Create PDF
        pdf = create_pdf_report(
            business_name, 
            business_location, 
            business_type, 
            business_size_sqft,
            total_revenue_y1, 
            total_expenses_y1, 
            ebitda_y1, 
            ebitda_margin_y1,
            roi_y3, 
            fig, 
            fig_revenue, 
            df_metrics, 
            df_detailed_revenue,
            fig_scenarios, 
            recommendations
        )
        
        # Save PDF to BytesIO
        pdf_output = BytesIO()
        pdf_data = pdf.output(dest='S').encode('latin1')  # Use 'S' to return as string
        pdf_output.write(pdf_data)
        pdf_output.seek(0)
        
        # Create download link
        b64_pdf = base64.b64encode(pdf_output.getvalue()).decode('utf-8')
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{business_name}_report.pdf">Download PDF Report</a>'
        st.markdown(href, unsafe_allow_html=True)
        
        # Send email if address provided
        if email_address:
            success, message = send_email(email_address, pdf_output.getvalue(), business_name)
            if success:
                st.success(message)
            else:
                st.error(message)

# Add footer
st.markdown("---")
st.markdown("### About This Dashboard")
st.markdown("""
This dashboard provides comprehensive financial analysis and projections for longevity and wellness clinics.
It allows you to model different scenarios, track performance, and generate detailed reports.

**Key Features:**
- Revenue and expense projections for 3 years
- Break-even analysis and ROI calculations
- Scenario comparison (optimistic, base case, pessimistic)
- Sensitivity analysis for key variables
- PDF report generation and email delivery

For support or customization, please contact support@longevityclinic.com
""")