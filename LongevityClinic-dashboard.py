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
    page_title="Property Development Financial Dashboard",
    page_icon="🏢",
    layout="wide"
)

# Title and introduction
st.title("Property Development Financial Dashboard")
st.markdown("Comprehensive financial tracking and analysis tool for property development projects in Central London.")

# Create sidebar for inputs
st.sidebar.header("Project Parameters")

# Input parameters with default values
with st.sidebar.expander("Project Details", expanded=True):
    project_name = st.text_input("Project Name", "Central London Development")
    project_type = st.selectbox("Project Type", ["Residential", "Commercial", "Mixed-Use", "Renovation"])
    project_location = st.selectbox("Location", ["Mayfair", "Kensington", "Chelsea", "Westminster", "City of London", "Canary Wharf", "Other"])
    project_size_sqft = st.number_input("Project Size (sq ft)", min_value=1000, value=10000, step=1000)
    project_duration_months = st.number_input("Project Duration (months)", min_value=1, value=24, step=1)
    
with st.sidebar.expander("Acquisition Costs", expanded=True):
    land_cost = st.number_input("Land/Property Acquisition Cost (£)", min_value=100000, value=5000000, step=100000)
    stamp_duty_rate = st.number_input("Stamp Duty Rate (%)", min_value=0.0, value=5.0, step=0.1)
    legal_fees_acquisition = st.number_input("Legal Fees - Acquisition (£)", min_value=1000, value=50000, step=1000)
    survey_costs = st.number_input("Survey Costs (£)", min_value=1000, value=15000, step=1000)

with st.sidebar.expander("Planning & Design", expanded=True):
    planning_application_fees = st.number_input("Planning Application Fees (£)", min_value=1000, value=25000, step=1000)
    architect_fees = st.number_input("Architect Fees (£)", min_value=10000, value=200000, step=10000)
    engineering_fees = st.number_input("Engineering Fees (£)", min_value=10000, value=150000, step=10000)
    other_consultant_fees = st.number_input("Other Consultant Fees (£)", min_value=0, value=75000, step=5000)
    planning_contingency = st.number_input("Planning Contingency (£)", min_value=0, value=50000, step=5000)

with st.sidebar.expander("Construction Costs", expanded=True):
    construction_cost_per_sqft = st.number_input("Construction Cost (£ per sq ft)", min_value=100, value=350, step=10)
    fit_out_cost_per_sqft = st.number_input("Fit-out Cost (£ per sq ft)", min_value=0, value=100, step=10)
    external_works = st.number_input("External Works (£)", min_value=0, value=200000, step=10000)
    construction_contingency_percent = st.number_input("Construction Contingency (%)", min_value=0.0, value=10.0, step=0.5)

with st.sidebar.expander("Professional Fees", expanded=True):
    project_management_percent = st.number_input("Project Management Fee (%)", min_value=0.0, value=3.0, step=0.5)
    quantity_surveyor_percent = st.number_input("Quantity Surveyor Fee (%)", min_value=0.0, value=1.5, step=0.1)
    building_control_fees = st.number_input("Building Control Fees (£)", min_value=1000, value=15000, step=1000)
    health_safety_fees = st.number_input("Health & Safety Fees (£)", min_value=1000, value=10000, step=1000)

with st.sidebar.expander("Finance & Legal", expanded=True):
    interest_rate = st.number_input("Interest Rate (%)", min_value=0.1, value=6.5, step=0.1)
    loan_to_cost_ratio = st.number_input("Loan to Cost Ratio (%)", min_value=0.0, value=70.0, step=5.0)
    arrangement_fee_percent = st.number_input("Loan Arrangement Fee (%)", min_value=0.0, value=1.5, step=0.1)
    legal_fees_finance = st.number_input("Legal Fees - Finance (£)", min_value=0, value=25000, step=5000)
    monitoring_surveyor_fees = st.number_input("Monitoring Surveyor Fees (£)", min_value=0, value=30000, step=5000)

with st.sidebar.expander("Marketing & Disposal", expanded=True):
    marketing_budget = st.number_input("Marketing Budget (£)", min_value=0, value=100000, step=10000)
    agent_fees_percent = st.number_input("Agent Fees (%)", min_value=0.0, value=1.5, step=0.1)
    legal_fees_disposal = st.number_input("Legal Fees - Disposal (£)", min_value=0, value=35000, step=5000)

with st.sidebar.expander("Revenue Projections", expanded=True):
    sales_price_per_sqft = st.number_input("Sales Price (£ per sq ft)", min_value=0, value=1200, step=50)
    rental_price_per_sqft = st.number_input("Annual Rental Price (£ per sq ft)", min_value=0, value=60, step=5)
    occupancy_rate = st.number_input("Occupancy Rate (%)", min_value=0.0, value=95.0, step=1.0)
    exit_yield = st.number_input("Exit Yield (%)", min_value=0.1, value=4.5, step=0.1)
    sales_absorption_rate = st.number_input("Sales Absorption Rate (units/month)", min_value=0.1, value=2.0, step=0.1)

# Calculations
# Acquisition costs
stamp_duty = land_cost * (stamp_duty_rate / 100)
total_acquisition_costs = land_cost + stamp_duty + legal_fees_acquisition + survey_costs

# Planning & design costs
total_planning_design_costs = planning_application_fees + architect_fees + engineering_fees + other_consultant_fees + planning_contingency

# Construction costs
base_construction_cost = construction_cost_per_sqft * project_size_sqft
fit_out_cost = fit_out_cost_per_sqft * project_size_sqft
construction_contingency = (base_construction_cost + fit_out_cost + external_works) * (construction_contingency_percent / 100)
total_construction_costs = base_construction_cost + fit_out_cost + external_works + construction_contingency

# Professional fees
project_management_fee = total_construction_costs * (project_management_percent / 100)
quantity_surveyor_fee = total_construction_costs * (quantity_surveyor_percent / 100)
total_professional_fees = project_management_fee + quantity_surveyor_fee + building_control_fees + health_safety_fees

# Finance costs
total_development_cost_before_finance = total_acquisition_costs + total_planning_design_costs + total_construction_costs + total_professional_fees
loan_amount = total_development_cost_before_finance * (loan_to_cost_ratio / 100)
equity_required = total_development_cost_before_finance - loan_amount
arrangement_fee = loan_amount * (arrangement_fee_percent / 100)

# Simple interest calculation (can be made more complex with drawdown schedule)
average_loan_duration = project_duration_months / 2  # Assuming gradual drawdown
interest_cost = loan_amount * (interest_rate / 100) * (average_loan_duration / 12)

total_finance_costs = arrangement_fee + interest_cost + legal_fees_finance + monitoring_surveyor_fees

# Marketing & disposal costs
agent_fees = (sales_price_per_sqft * project_size_sqft) * (agent_fees_percent / 100)
total_marketing_disposal_costs = marketing_budget + agent_fees + legal_fees_disposal

# Total development costs
total_development_costs = (
    total_acquisition_costs + 
    total_planning_design_costs + 
    total_construction_costs + 
    total_professional_fees + 
    total_finance_costs + 
    total_marketing_disposal_costs
)

# Revenue calculations
gross_development_value_sales = sales_price_per_sqft * project_size_sqft
annual_rental_income = rental_price_per_sqft * project_size_sqft * (occupancy_rate / 100)
gross_development_value_investment = annual_rental_income / (exit_yield / 100)

# Use the higher of sales or investment value as the GDV
gross_development_value = max(gross_development_value_sales, gross_development_value_investment)

# Profit calculations
profit = gross_development_value - total_development_costs
profit_margin = (profit / total_development_costs) * 100
profit_on_gdv = (profit / gross_development_value) * 100
return_on_equity = (profit / equity_required) * 100

# Cost per square foot
cost_per_sqft = total_development_costs / project_size_sqft

# Main dashboard
# KPI metrics in columns
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Gross Development Value", f"£{gross_development_value:,.0f}")
with col2:
    st.metric("Total Development Costs", f"£{total_development_costs:,.0f}")
with col3:
    st.metric("Profit", f"£{profit:,.0f}")
with col4:
    st.metric("Profit Margin", f"{profit_margin:.2f}%")

# Project timeline and cashflow
st.subheader("Project Timeline & Cashflow")

# Create a simplified monthly cashflow projection
months = list(range(1, project_duration_months + 1))

# Simplified S-curve for construction costs
def s_curve(x, duration):
    return 1 / (1 + np.exp(-0.5 * (x - duration/2)))

# Create spending curves for different cost categories
acquisition_curve = np.zeros(project_duration_months)
acquisition_curve[0] = 1  # All acquisition costs in month 1

planning_curve = np.zeros(project_duration_months)
planning_months = min(6, project_duration_months)
planning_curve[:planning_months] = 1/planning_months  # Spread over first 6 months or project duration

construction_start = min(3, project_duration_months - 1)
construction_duration = project_duration_months - construction_start
construction_curve = np.zeros(project_duration_months)
for i in range(construction_start, project_duration_months):
    month_in_construction = i - construction_start
    construction_curve[i] = (s_curve(month_in_construction + 1, construction_duration) - 
                            s_curve(month_in_construction, construction_duration))

# Professional fees follow construction
professional_curve = construction_curve.copy()

# Finance costs spread evenly
finance_curve = np.ones(project_duration_months) / project_duration_months

# Marketing and disposal weighted toward end
marketing_curve = np.zeros(project_duration_months)
marketing_start = max(0, project_duration_months - 6)
marketing_curve[marketing_start:] = 1 / (project_duration_months - marketing_start)

# Calculate monthly costs
monthly_acquisition = acquisition_curve * total_acquisition_costs
monthly_planning = planning_curve * total_planning_design_costs
monthly_construction = construction_curve * total_construction_costs
monthly_professional = professional_curve * total_professional_fees
monthly_finance = finance_curve * total_finance_costs
monthly_marketing = marketing_curve * total_marketing_disposal_costs

monthly_total_costs = (
    monthly_acquisition + 
    monthly_planning + 
    monthly_construction + 
    monthly_professional + 
    monthly_finance + 
    monthly_marketing
)

# Revenue comes at the end for sales model
monthly_revenue = np.zeros(project_duration_months)
if gross_development_value == gross_development_value_sales:
    # Sales model - revenue at the end
    sales_start = max(0, project_duration_months - int(project_size_sqft / 1000 / sales_absorption_rate))
    for i in range(sales_start, project_duration_months):
        monthly_revenue[i] = gross_development_value / (project_duration_months - sales_start)
else:
    # Investment model - revenue at the end
    monthly_revenue[-1] = gross_development_value

# Calculate cumulative cashflow
cumulative_costs = np.cumsum(monthly_total_costs)
cumulative_revenue = np.cumsum(monthly_revenue)
cumulative_cashflow = cumulative_revenue - cumulative_costs

# Create dataframe for plotting
df_cashflow = pd.DataFrame({
    'Month': months,
    'Monthly Costs': monthly_total_costs,
    'Monthly Revenue': monthly_revenue,
    'Cumulative Costs': cumulative_costs,
    'Cumulative Revenue': cumulative_revenue,
    'Cumulative Cashflow': cumulative_cashflow
})

# Plot cashflow
fig_cashflow = go.Figure()

# Add revenue line
fig_cashflow.add_trace(go.Scatter(
    x=months,
    y=cumulative_revenue,
    mode='lines',
    name='Cumulative Revenue',
    line=dict(color='blue', width=3)
))

# Add cost line
fig_cashflow.add_trace(go.Scatter(
    x=months,
    y=cumulative_costs,
    mode='lines',
    name='Cumulative Costs',
    line=dict(color='green', width=3)
))

# Add cashflow line
fig_cashflow.add_trace(go.Scatter(
    x=months,
    y=cumulative_cashflow,
    mode='lines',
    name='Net Cashflow',
    line=dict(color='red', width=4, dash='dot')
))

# Add zero line
fig_cashflow.add_hline(
    y=0, 
    line=dict(color='black', width=1, dash='dash'),
    annotation_text="Break-even",
    annotation_position="bottom right"
)

# Update layout
fig_cashflow.update_layout(
    title='Project Cashflow Projection',
    xaxis_title='Month',
    yaxis_title='Amount (£)',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='black'),
    hovermode='x unified'
)

st.plotly_chart(fig_cashflow, use_container_width=True)

# Two columns for Cost Breakdown and Financial Metrics
col1, col2 = st.columns(2)

# Cost breakdown pie chart
with col1:
    st.subheader("Development Cost Breakdown")
    cost_data = {
        'Category': [
            'Acquisition', 'Planning & Design', 'Construction', 
            'Professional Fees', 'Finance', 'Marketing & Disposal'
        ],
        'Cost': [
            total_acquisition_costs, total_planning_design_costs, total_construction_costs,
            total_professional_fees, total_finance_costs, total_marketing_disposal_costs
        ]
    }
    df_costs = pd.DataFrame(cost_data)
    fig_costs = px.pie(
        df_costs, 
        values='Cost', 
        names='Category',
        title='Development Cost Breakdown',
        color_discrete_sequence=['blue', 'green', 'red', 'orange', 'purple', 'pink'],
        hole=0.4
    )
    fig_costs.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        marker=dict(line=dict(color='white', width=2))
    )
    fig_costs.update_layout(
        font=dict(color='black'),
        legend=dict(orientation='h', yanchor='bottom', y=-0.2),
        paper_bgcolor='white'
    )
    st.plotly_chart(fig_costs, use_container_width=True)

# Financial metrics
with col2:
    st.subheader("Financial Metrics")
    financial_metrics = {
        'Metric': [
            'Gross Development Value (GDV)',
            'Total Development Costs (TDC)',
            'Profit',
            'Profit Margin (% of TDC)',
            'Profit on GDV (%)',
            'Return on Equity (%)',
            'Cost per Square Foot',
            'Revenue per Square Foot',
            'Equity Required',
            'Loan Amount'
        ],
        'Value': [
            f"£{gross_development_value:,.0f}",
            f"£{total_development_costs:,.0f}",
            f"£{profit:,.0f}",
            f"{profit_margin:.2f}%",
            f"{profit_on_gdv:.2f}%",
            f"{return_on_equity:.2f}%",
            f"£{cost_per_sqft:.0f}",
            f"£{sales_price_per_sqft:.0f}",
            f"£{equity_required:,.0f}",
            f"£{loan_amount:,.0f}"
        ]
    }
    df_metrics = pd.DataFrame(financial_metrics)
    st.table(df_metrics)

# Detailed Cost Breakdown
st.subheader("Detailed Cost Breakdown")

# Create detailed cost breakdown table
detailed_costs = {
    'Cost Category': [
        'Land/Property Acquisition',
        'Stamp Duty',
        'Legal Fees - Acquisition',
        'Survey Costs',
        'Planning Application Fees',
        'Architect Fees',
        'Engineering Fees',
        'Other Consultant Fees',
        'Planning Contingency',
        'Base Construction',
        'Fit-out',
        'External Works',
        'Construction Contingency',
        'Project Management',
        'Quantity Surveyor',
        'Building Control Fees',
        'Health & Safety Fees',
        'Loan Arrangement Fee',
        'Interest Cost',
        'Legal Fees - Finance',
        'Monitoring Surveyor Fees',
        'Marketing Budget',
        'Agent Fees',
        'Legal Fees - Disposal'
    ],
    'Cost': [
        land_cost,
        stamp_duty,
        legal_fees_acquisition,
        survey_costs,
        planning_application_fees,
        architect_fees,
        engineering_fees,
        other_consultant_fees,
        planning_contingency,
        base_construction_cost,
        fit_out_cost,
        external_works,
        construction_contingency,
        project_management_fee,
        quantity_surveyor_fee,
        building_control_fees,
        health_safety_fees,
        arrangement_fee,
        interest_cost,
        legal_fees_finance,
        monitoring_surveyor_fees,
        marketing_budget,
        agent_fees,
        legal_fees_disposal
    ]
}

df_detailed_costs = pd.DataFrame(detailed_costs)
df_detailed_costs['Percentage of Total'] = (df_detailed_costs['Cost'] / total_development_costs) * 100
df_detailed_costs['Cost per sq ft'] = df_detailed_costs['Cost'] / project_size_sqft

# Format the numbers
df_detailed_costs['Cost'] = df_detailed_costs['Cost'].apply(lambda x: f"£{x:,.0f}")
df_detailed_costs['Percentage of Total'] = df_detailed_costs['Percentage of Total'].apply(lambda x: f"{x:.1f}%")
df_detailed_costs['Cost per sq ft'] = df_detailed_costs['Cost per sq ft'].apply(lambda x: f"£{x:.2f}")

st.table(df_detailed_costs)

# Add after the "Detailed Cost Breakdown" section
st.subheader("Budget vs. Actual Tracking")

with st.expander("Budget vs. Actual Cost Tracking"):
    # Create tabs for data entry and visualization
    budget_actual_tab1, budget_actual_tab2 = st.tabs(["Data Entry", "Visualization"])
    
    with budget_actual_tab1:
        st.markdown("### Enter Actual Costs")
        st.markdown("Track your project's actual costs against the budget.")
        
        # Create a dataframe with the main cost categories
        actual_costs_data = {
            'Cost Category': [
                'Land/Property Acquisition',
                'Planning & Design',
                'Construction',
                'Professional Fees',
                'Finance',
                'Marketing & Disposal'
            ],
            'Budgeted Cost': [
                total_acquisition_costs,
                total_planning_design_costs,
                total_construction_costs,
                total_professional_fees,
                total_finance_costs,
                total_marketing_disposal_costs
            ],
            'Actual Cost': [0, 0, 0, 0, 0, 0],
            'Completion (%)': [0, 0, 0, 0, 0, 0]
        }
        
        df_actual_costs = pd.DataFrame(actual_costs_data)
        
        # Create input fields for actual costs and completion percentages
        for i, category in enumerate(df_actual_costs['Cost Category']):
            col1, col2 = st.columns(2)
            with col1:
                actual_cost = st.number_input(
                    f"Actual Cost - {category} (£)",
                    min_value=0,
                    value=int(df_actual_costs.loc[i, 'Actual Cost']),
                    step=10000
                )
                df_actual_costs.loc[i, 'Actual Cost'] = actual_cost
            
            with col2:
                completion = st.slider(
                    f"Completion % - {category}",
                    min_value=0,
                    max_value=100,
                    value=int(df_actual_costs.loc[i, 'Completion (%)']),
                    step=5
                )
                df_actual_costs.loc[i, 'Completion (%)'] = completion
        
        # Calculate variance
        df_actual_costs['Variance'] = df_actual_costs['Budgeted Cost'] - df_actual_costs['Actual Cost']
        df_actual_costs['Variance %'] = (df_actual_costs['Variance'] / df_actual_costs['Budgeted Cost']) * 100
        
        # Format for display
        df_actual_costs_display = df_actual_costs.copy()
        df_actual_costs_display['Budgeted Cost'] = df_actual_costs_display['Budgeted Cost'].apply(lambda x: f"£{x:,.0f}")
        df_actual_costs_display['Actual Cost'] = df_actual_costs_display['Actual Cost'].apply(lambda x: f"£{x:,.0f}")
        df_actual_costs_display['Variance'] = df_actual_costs_display['Variance'].apply(lambda x: f"£{x:,.0f}")
        df_actual_costs_display['Variance %'] = df_actual_costs_display['Variance %'].apply(lambda x: f"{x:.1f}%")
        df_actual_costs_display['Completion (%)'] = df_actual_costs_display['Completion (%)'].apply(lambda x: f"{x}%")
        
        st.table(df_actual_costs_display)
    
    with budget_actual_tab2:
        # Create visualizations for budget vs actual
        st.markdown("### Budget vs. Actual Visualization")
        
        # Bar chart comparing budget vs actual
        budget_vs_actual_data = pd.DataFrame({
            'Category': df_actual_costs['Cost Category'],
            'Budgeted': df_actual_costs['Budgeted Cost'],
            'Actual': df_actual_costs['Actual Cost']
        })
        
        budget_vs_actual_melted = pd.melt(
            budget_vs_actual_data, 
            id_vars=['Category'],
            value_vars=['Budgeted', 'Actual'],
            var_name='Type',
            value_name='Cost'
        )
        
        fig_budget_actual = px.bar(
            budget_vs_actual_melted,
            x='Category',
            y='Cost',
            color='Type',
            barmode='group',
            title="Budget vs. Actual Costs by Category",
            labels={'Cost': 'Cost (£)', 'Category': 'Cost Category'},
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
        weighted_completion = sum(df_actual_costs['Completion (%)'] * df_actual_costs['Budgeted Cost']) / sum(df_actual_costs['Budgeted Cost'])
        total_budget = sum(df_actual_costs['Budgeted Cost'])
        total_actual = sum(df_actual_costs['Actual Cost'])
        budget_variance = total_budget - total_actual
        budget_variance_pct = (budget_variance / total_budget) * 100 if total_budget > 0 else 0
        
        # Create KPI metrics for project status
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Project Completion", f"{weighted_completion:.1f}%")
        with col2:
            st.metric("Budget Variance", f"£{budget_variance:,.0f}", f"{budget_variance_pct:.1f}%")
        with col3:
            status = "On Budget" if abs(budget_variance_pct) < 5 else ("Over Budget" if budget_variance_pct < 0 else "Under Budget")
            st.metric("Budget Status", status)

# Sensitivity Analysis
st.subheader("Sensitivity Analysis")

with st.expander("Profit Sensitivity Analysis"):
    # 1. Sales price sensitivity
    st.subheader("Sales Price Sensitivity")
    price_variations = np.linspace(sales_price_per_sqft * 0.8, sales_price_per_sqft * 1.2, 9)
    price_profit_results = []
    price_margin_results = []
    
    for price in price_variations:
        new_gdv = price * project_size_sqft
        new_profit = new_gdv - total_development_costs
        new_margin = (new_profit / total_development_costs) * 100
        price_profit_results.append(new_profit)
        price_margin_results.append(new_margin)
    
    price_sensitivity_df = pd.DataFrame({
        'Sales Price (£/sq ft)': [f"£{price:.0f}" for price in price_variations],
        'Profit (£)': [f"£{profit:,.0f}" for profit in price_profit_results],
        'Profit Margin (%)': [f"{margin:.1f}%" for margin in price_margin_results]
    })
    
    st.table(price_sensitivity_df)
    
    fig_price_sensitivity = px.line(
        x=price_variations, 
        y=price_profit_results,
        labels={'x': 'Sales Price (£/sq ft)', 'y': 'Profit (£)'},
        title="Profit Sensitivity to Sales Price"
    )
    fig_price_sensitivity.update_traces(
        line=dict(color='blue', width=3),
        mode='lines+markers',
        marker=dict(size=8, color='blue')
    )
    fig_price_sensitivity.add_hline(
        y=profit,
        line=dict(color='red', width=1, dash='dash'),
        annotation_text="Current Profit",
        annotation_position="bottom right"
    )
    fig_price_sensitivity.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        xaxis=dict(gridcolor='white', linecolor='white'),
        yaxis=dict(gridcolor='white', linecolor='white'),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_price_sensitivity, use_container_width=True)

    # 2. Construction cost sensitivity
    st.subheader("Construction Cost Sensitivity")
    construction_variations = np.linspace(construction_cost_per_sqft * 0.8, construction_cost_per_sqft * 1.2, 9)
    construction_profit_results = []
    construction_margin_results = []
    
    for cost in construction_variations:
        new_construction_cost = cost * project_size_sqft
        new_contingency = (new_construction_cost + fit_out_cost + external_works) * (construction_contingency_percent / 100)
        new_total_construction = new_construction_cost + fit_out_cost + external_works + new_contingency
        
        # Recalculate professional fees
        new_pm_fee = new_total_construction * (project_management_percent / 100)
        new_qs_fee = new_total_construction * (quantity_surveyor_percent / 100)
        new_prof_fees = new_pm_fee + new_qs_fee + building_control_fees + health_safety_fees
        
        # Calculate new total cost
        new_total_cost = (
            total_acquisition_costs + 
            total_planning_design_costs + 
            new_total_construction + 
            new_prof_fees + 
            total_finance_costs + 
            total_marketing_disposal_costs
        )
        
        new_profit = gross_development_value - new_total_cost
        new_margin = (new_profit / new_total_cost) * 100
        construction_profit_results.append(new_profit)
        construction_margin_results.append(new_margin)
    
    construction_sensitivity_df = pd.DataFrame({
        'Construction Cost (£/sq ft)': [f"£{cost:.0f}" for cost in construction_variations],
        'Profit (£)': [f"£{profit:,.0f}" for profit in construction_profit_results],
        'Profit Margin (%)': [f"{margin:.1f}%" for margin in construction_margin_results]
    })
    
    st.table(construction_sensitivity_df)
    
    fig_construction_sensitivity = px.line(
        x=construction_variations, 
        y=construction_profit_results,
        labels={'x': 'Construction Cost (£/sq ft)', 'y': 'Profit (£)'},
        title="Profit Sensitivity to Construction Cost"
    )
    fig_construction_sensitivity.update_traces(
        line=dict(color='blue', width=3),
        mode='lines+markers',
        marker=dict(size=8, color='blue')
    )
    fig_construction_sensitivity.add_hline(
        y=profit,
        line=dict(color='red', width=1, dash='dash'),
        annotation_text="Current Profit",
        annotation_position="bottom right"
    )
    fig_construction_sensitivity.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        xaxis=dict(gridcolor='white', linecolor='white'),
        yaxis=dict(gridcolor='white', linecolor='white'),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_construction_sensitivity, use_container_width=True)

    # 3. Interest rate sensitivity
    st.subheader("Interest Rate Sensitivity")
    interest_variations = np.linspace(max(0.5, interest_rate - 2), interest_rate + 2, 9)
    interest_profit_results = []
    interest_margin_results = []
    
    for rate in interest_variations:
        new_interest_cost = loan_amount * (rate / 100) * (average_loan_duration / 12)
        new_finance_costs = arrangement_fee + new_interest_cost + legal_fees_finance + monitoring_surveyor_fees
        
        new_total_cost = (
            total_acquisition_costs + 
            total_planning_design_costs + 
            total_construction_costs + 
            total_professional_fees + 
            new_finance_costs + 
            total_marketing_disposal_costs
        )
        
        new_profit = gross_development_value - new_total_cost
        new_margin = (new_profit / new_total_cost) * 100
        interest_profit_results.append(new_profit)
        interest_margin_results.append(new_margin)
    
    interest_sensitivity_df = pd.DataFrame({
        'Interest Rate (%)': [f"{rate:.1f}%" for rate in interest_variations],
        'Profit (£)': [f"£{profit:,.0f}" for profit in interest_profit_results],
        'Profit Margin (%)': [f"{margin:.1f}%" for margin in interest_margin_results]
    })
    
    st.table(interest_sensitivity_df)
    
    fig_interest_sensitivity = px.line(
        x=interest_variations, 
        y=interest_profit_results,
        labels={'x': 'Interest Rate (%)', 'y': 'Profit (£)'},
        title="Profit Sensitivity to Interest Rate"
    )
    fig_interest_sensitivity.update_traces(
        line=dict(color='blue', width=3),
        mode='lines+markers',
        marker=dict(size=8, color='blue')
    )
    fig_interest_sensitivity.add_hline(
        y=profit,
        line=dict(color='red', width=1, dash='dash'),
        annotation_text="Current Profit",
        annotation_position="bottom right"
    )
    fig_interest_sensitivity.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        xaxis=dict(gridcolor='white', linecolor='white'),
        yaxis=dict(gridcolor='white', linecolor='white'),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_interest_sensitivity, use_container_width=True)

# Add after the "Sensitivity Analysis" section
st.subheader("Scenario Comparison")

with st.expander("Compare Different Scenarios"):
    st.markdown("### Create and Compare Project Scenarios")
    
    # Create tabs for different scenarios
    scenario_tab1, scenario_tab2, scenario_tab3 = st.tabs(["Base Case", "Optimistic", "Pessimistic"])
    
    # Base case (current values)
    with scenario_tab1:
        st.markdown("#### Base Case Scenario")
        st.markdown("Current project parameters")
        
        base_metrics = {
            'Metric': [
                'GDV (£)',
                'Total Development Cost (£)',
                'Profit (£)',
                'Profit Margin (%)',
                'ROE (%)',
                'Project Duration (months)'
            ],
            'Value': [
                f"{gross_development_value:,.0f}",
                f"{total_development_costs:,.0f}",
                f"{profit:,.0f}",
                f"{profit_margin:.2f}",
                f"{return_on_equity:.2f}",
                f"{project_duration_months}"
            ]
        }
        
        st.table(pd.DataFrame(base_metrics))
    
    # Optimistic scenario
    with scenario_tab2:
        st.markdown("#### Optimistic Scenario")
        
        # Optimistic adjustments
        opt_sales_price = sales_price_per_sqft * 1.1
        opt_construction_cost = construction_cost_per_sqft * 0.9
        opt_interest_rate = max(interest_rate - 1, 0.5)
        opt_duration = max(project_duration_months - 3, 12)
        
        # Recalculate with optimistic values
        opt_gdv = opt_sales_price * project_size_sqft
        
        opt_construction_total = (opt_construction_cost * project_size_sqft) + fit_out_cost + external_works
        opt_construction_contingency = opt_construction_total * (construction_contingency_percent / 100)
        opt_construction_costs = opt_construction_total + opt_construction_contingency
        
        opt_prof_fees = opt_construction_costs * ((project_management_percent + quantity_surveyor_percent) / 100) + building_control_fees + health_safety_fees
        
        opt_dev_cost_before_finance = total_acquisition_costs + total_planning_design_costs + opt_construction_costs + opt_prof_fees
        opt_loan_amount = opt_dev_cost_before_finance * (loan_to_cost_ratio / 100)
        opt_interest_cost = opt_loan_amount * (opt_interest_rate / 100) * (opt_duration / 2 / 12)
        opt_finance_costs = arrangement_fee + opt_interest_cost + legal_fees_finance + monitoring_surveyor_fees
        
        opt_total_costs = total_acquisition_costs + total_planning_design_costs + opt_construction_costs + opt_prof_fees + opt_finance_costs + total_marketing_disposal_costs
        
        opt_profit = opt_gdv - opt_total_costs
        opt_margin = (opt_profit / opt_total_costs) * 100
        opt_equity = opt_dev_cost_before_finance - opt_loan_amount
        opt_roe = (opt_profit / opt_equity) * 100
        
        # Display optimistic metrics
        opt_metrics = {
            'Metric': [
                'GDV (£)',
                'Total Development Cost (£)',
                'Profit (£)',
                'Profit Margin (%)',
                'ROE (%)',
                'Project Duration (months)'
            ],
            'Value': [
                f"{opt_gdv:,.0f}",
                f"{opt_total_costs:,.0f}",
                f"{opt_profit:,.0f}",
                f"{opt_margin:.2f}",
                f"{opt_roe:.2f}",
                f"{opt_duration}"
            ],
            'Change from Base': [
                f"{((opt_gdv/gross_development_value)-1)*100:+.1f}%",
                f"{((opt_total_costs/total_development_costs)-1)*100:+.1f}%",
                f"{((opt_profit/profit)-1)*100:+.1f}%",
                f"{opt_margin-profit_margin:+.2f}%",
                f"{opt_roe-return_on_equity:+.2f}%",
                f"{opt_duration-project_duration_months:+d}"
            ]
        }
        
        st.table(pd.DataFrame(opt_metrics))
        
        # Key assumptions
        st.markdown("**Key Assumptions:**")
        st.markdown(f"- Sales price increased by 10% (£{sales_price_per_sqft:.0f} → £{opt_sales_price:.0f})")
        st.markdown(f"- Construction cost reduced by 10% (£{construction_cost_per_sqft:.0f} → £{opt_construction_cost:.0f})")
        st.markdown(f"- Interest rate reduced by 1% ({interest_rate:.1f}% → {opt_interest_rate:.1f}%)")
        st.markdown(f"- Project duration reduced by 3 months ({project_duration_months} → {opt_duration})")
    
    # Pessimistic scenario
    with scenario_tab3:
        st.markdown("#### Pessimistic Scenario")
        
        # Pessimistic adjustments
        pes_sales_price = sales_price_per_sqft * 0.9
        pes_construction_cost = construction_cost_per_sqft * 1.15
        pes_interest_rate = interest_rate + 1.5
        pes_duration = project_duration_months + 6
        
        # Recalculate with pessimistic values
        pes_gdv = pes_sales_price * project_size_sqft
        
        pes_construction_total = (pes_construction_cost * project_size_sqft) + fit_out_cost + external_works
        pes_construction_contingency = pes_construction_total * (construction_contingency_percent / 100)
        pes_construction_costs = pes_construction_total + pes_construction_contingency
        
        pes_prof_fees = pes_construction_costs * ((project_management_percent + quantity_surveyor_percent) / 100) + building_control_fees + health_safety_fees
        
        pes_dev_cost_before_finance = total_acquisition_costs + total_planning_design_costs + pes_construction_costs + pes_prof_fees
        pes_loan_amount = pes_dev_cost_before_finance * (loan_to_cost_ratio / 100)
        pes_interest_cost = pes_loan_amount * (pes_interest_rate / 100) * (pes_duration / 2 / 12)
        pes_finance_costs = arrangement_fee + pes_interest_cost + legal_fees_finance + monitoring_surveyor_fees
        
        pes_total_costs = total_acquisition_costs + total_planning_design_costs + pes_construction_costs + pes_prof_fees + pes_finance_costs + total_marketing_disposal_costs
        
        pes_profit = pes_gdv - pes_total_costs
        pes_margin = (pes_profit / pes_total_costs) * 100
        pes_equity = pes_dev_cost_before_finance - pes_loan_amount
        pes_roe = (pes_profit / pes_equity) * 100
        
        # Display pessimistic metrics
        pes_metrics = {
            'Metric': [
                'GDV (£)',
                'Total Development Cost (£)',
                'Profit (£)',
                'Profit Margin (%)',
                'ROE (%)',
                'Project Duration (months)'
            ],
            'Value': [
                f"{pes_gdv:,.0f}",
                f"{pes_total_costs:,.0f}",
                f"{pes_profit:,.0f}",
                f"{pes_margin:.2f}",
                f"{pes_roe:.2f}",
                f"{pes_duration}"
            ],
            'Change from Base': [
                f"{((pes_gdv/gross_development_value)-1)*100:+.1f}%",
                f"{((pes_total_costs/total_development_costs)-1)*100:+.1f}%",
                f"{((pes_profit/profit)-1)*100:+.1f}%",
                f"{pes_margin-profit_margin:+.2f}%",
                f"{pes_roe-return_on_equity:+.2f}%",
                f"{pes_duration-project_duration_months:+d}"
            ]
        }
        
        st.table(pd.DataFrame(pes_metrics))
        
        # Key assumptions
        st.markdown("**Key Assumptions:**")
        st.markdown(f"- Sales price decreased by 10% (£{sales_price_per_sqft:.0f} → £{pes_sales_price:.0f})")
        st.markdown(f"- Construction cost increased by 15% (£{construction_cost_per_sqft:.0f} → £{pes_construction_cost:.0f})")
        st.markdown(f"- Interest rate increased by 1.5% ({interest_rate:.1f}% → {pes_interest_rate:.1f}%)")
        st.markdown(f"- Project duration increased by 6 months ({project_duration_months} → {pes_duration})")
    
    # Scenario comparison chart
    st.markdown("### Scenario Comparison")
    
    scenario_data = {
        'Scenario': ['Base Case', 'Optimistic', 'Pessimistic'],
        'GDV': [gross_development_value, opt_gdv, pes_gdv],
        'Total Cost': [total_development_costs, opt_total_costs, pes_total_costs],
        'Profit': [profit, opt_profit, pes_profit],
        'Profit Margin': [profit_margin, opt_margin, pes_margin]
    }
    
    df_scenarios = pd.DataFrame(scenario_data)
    
    # Create bar chart for scenario comparison
    fig_scenarios = px.bar(
        df_scenarios,
        x='Scenario',
        y=['GDV', 'Total Cost', 'Profit'],
        barmode='group',
        title="Financial Comparison Across Scenarios",
        labels={'value': 'Amount (£)', 'variable': 'Metric'},
        color_discrete_sequence=['blue', 'green', 'red']
    )
    
    fig_scenarios.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    st.plotly_chart(fig_scenarios, use_container_width=True)
    
    # Create profit margin comparison
    fig_margins = px.bar(
        df_scenarios,
        x='Scenario',
        y='Profit Margin',
        title="Profit Margin Comparison Across Scenarios",
        labels={'Profit Margin': 'Profit Margin (%)'}
    )
    
    fig_margins.update_traces(
        marker_color=[
            'blue',  # Base case
            'green', # Optimistic
            'red'   # Pessimistic
        ]
    )
    
    fig_margins.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        margin=dict(l=20, r=20, t=60, b=20)
    )

# Risk Analysis
st.subheader("Risk Analysis")

with st.expander("Project Risk Assessment"):
    # Create a simple risk matrix
    risk_data = {
        'Risk Factor': [
            'Planning Permission Delay',
            'Construction Cost Overrun',
            'Interest Rate Increase',
            'Sales Price Decrease',
            'Construction Delay',
            'Supply Chain Issues',
            'Labor Shortages',
            'Regulatory Changes',
            'Market Downturn'
        ],
        'Impact (1-5)': [4, 5, 3, 5, 4, 3, 3, 2, 5],
        'Probability (1-5)': [3, 4, 3, 2, 3, 3, 2, 2, 2],
    }
    
    df_risk = pd.DataFrame(risk_data)
    df_risk['Risk Score'] = df_risk['Impact (1-5)'] * df_risk['Probability (1-5)']
    df_risk['Risk Level'] = df_risk['Risk Score'].apply(
        lambda x: 'High' if x >= 16 else ('Medium' if x >= 9 else 'Low')
    )
    
    # Sort by risk score
    df_risk = df_risk.sort_values('Risk Score', ascending=False)
    
    # Display risk matrix
    fig_risk = px.scatter(
        df_risk, 
        x='Probability (1-5)', 
        y='Impact (1-5)', 
        size='Risk Score',
        color='Risk Level',
        color_discrete_map={
            'High': 'red', 
            'Medium': 'yellow', 
            'Low': 'green'
        },
        text='Risk Factor',
        title="Risk Assessment Matrix"
    )
    
    fig_risk.update_traces(
        textposition='top center',
        marker=dict(line=dict(width=1, color='black'))
    )
    fig_risk.update_layout(
        xaxis=dict(range=[0.5, 5.5], title='Probability', gridcolor='white'),
        yaxis=dict(range=[0.5, 5.5], title='Impact', gridcolor='white'),
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black')
    )
    
    st.plotly_chart(fig_risk, use_container_width=True)
    st.table(df_risk)

# Project Profitability Analysis
st.subheader("Project Profitability Analysis")

# Create a comparison of different metrics
profitability_data = {
    'Metric': [
        'Development Profit',
        'Profit on Cost',
        'Profit on GDV',
        'Return on Equity',
        'Internal Rate of Return (IRR)',
        'Payback Period'
    ],
    'Value': [
        f"£{profit:,.0f}",
        f"{profit_margin:.2f}%",
        f"{profit_on_gdv:.2f}%",
        f"{return_on_equity:.2f}%",
        f"{return_on_equity / (project_duration_months/12):.2f}%",  # Simplified IRR
        f"{project_duration_months} months"
    ],
    'Industry Benchmark': [
        'Project Specific',
        '15-20%',
        '12-18%',
        '20-25%',
        '15-25%',
        '24-36 months'
    ],
    'Status': [
        'N/A',
        'Good' if profit_margin >= 15 else ('Average' if profit_margin >= 10 else 'Poor'),
        'Good' if profit_on_gdv >= 12 else ('Average' if profit_on_gdv >= 8 else 'Poor'),
        'Good' if return_on_equity >= 20 else ('Average' if return_on_equity >= 15 else 'Poor'),
        'Good' if return_on_equity / (project_duration_months/12) >= 15 else ('Average' if return_on_equity / (project_duration_months/12) >= 10 else 'Poor'),
        'Good' if project_duration_months <= 24 else ('Average' if project_duration_months <= 36 else 'Poor')
    ]
}

df_profitability = pd.DataFrame(profitability_data)
st.table(df_profitability)

# Recommendations based on analysis
st.subheader("Recommendations")

# Generate recommendations based on the analysis
recommendations = []

if profit_margin < 15:
    recommendations.append("Consider ways to increase profit margin, such as value engineering or negotiating better terms with contractors.")

if construction_cost_per_sqft > 300:
    recommendations.append("Construction costs are relatively high. Consider reviewing specifications and exploring alternative construction methods.")

if interest_rate > 5:
    recommendations.append("Interest rates are significant. Explore refinancing options or accelerating the development timeline to reduce finance costs.")

if loan_to_cost_ratio < 60:
    recommendations.append("Consider increasing leverage to improve return on equity, if the project can support additional debt.")

if project_duration_months > 24:
    recommendations.append("Project timeline is extended. Look for opportunities to accelerate construction to reduce holding costs and improve IRR.")

if profit_on_gdv < 12:
    recommendations.append("Profit on GDV is below industry benchmarks. Review sales/rental strategy to maximize revenue.")

# Add default recommendations if none were generated
if not recommendations:
    recommendations = [
        "The project appears financially sound based on current parameters.",
        "Continue to monitor construction costs and timeline to prevent overruns.",
        "Regularly review sales/rental market conditions to optimize exit strategy.",
        "Consider phasing the development to reduce risk and accelerate returns."
    ]

for i, rec in enumerate(recommendations, 1):
    st.markdown(f"{i}. {rec}")

# Footer
st.markdown("---")
st.markdown("Property Development Financial Dashboard - Created for Central London Developers")

# Add after the "Project Timeline & Cashflow" section
st.subheader("Project Timeline Gantt Chart")

with st.expander("Project Schedule"):
    # Create a sample project schedule
    today = datetime.now().date()
    project_start_date = st.date_input("Project Start Date", today)
    
    # Calculate end dates based on durations
    acquisition_duration = 1  # month
    planning_duration = min(6, project_duration_months // 4)
    design_duration = min(4, project_duration_months // 6)
    construction_duration = max(project_duration_months - planning_duration - design_duration - acquisition_duration - 2, 
                               project_duration_months // 2)
    marketing_duration = min(6, project_duration_months // 4)
    
    # Create task data
    tasks = [
        dict(Task="Acquisition", Start=project_start_date, 
             Finish=pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration),
             Resource="Acquisition"),
        dict(Task="Planning", 
             Start=pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration),
             Finish=pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration),
             Resource="Planning"),
        dict(Task="Design", 
             Start=pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration - 1),
             Finish=pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration + design_duration - 1),
             Resource="Design"),
        dict(Task="Construction", 
             Start=pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration + design_duration - 2),
             Finish=pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration + design_duration + construction_duration - 2),
             Resource="Construction"),
        dict(Task="Marketing & Sales", 
             Start=pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration + design_duration + construction_duration - 4),
             Finish=pd.Timestamp(project_start_date) + pd.DateOffset(months=project_duration_months),
             Resource="Marketing")
    ]
    
    # Convert to DataFrame
    df_tasks = pd.DataFrame(tasks)
    
    # Create Gantt chart
    fig_gantt = px.timeline(
        df_tasks, 
        x_start="Start", 
        x_end="Finish", 
        y="Task",
        color="Resource",
        title="Project Schedule Gantt Chart"
    )
    
    fig_gantt.update_layout(
        xaxis_title="Date",
        yaxis_title="Project Phase",
        height=400
    )
    
    st.plotly_chart(fig_gantt, use_container_width=True)
    
    # Add milestone tracking
    st.markdown("### Key Project Milestones")
    
    milestone_data = {
        'Milestone': [
            'Land Acquisition Complete',
            'Planning Permission Granted',
            'Design Complete',
            'Construction Start',
            'Superstructure Complete',
            'Building Watertight',
            'Fit-out Complete',
            'Practical Completion',
            'Marketing Launch',
            'First Sale/Letting',
            'Project Completion'
        ],
        'Planned Date': [
            pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration),
            pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration),
            pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration + design_duration - 1),
            pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration + design_duration - 2),
            pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration + design_duration + construction_duration//3),
            pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration + design_duration + construction_duration//2),
            pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration + design_duration + construction_duration - 1),
            pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration + design_duration + construction_duration),
            pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration + design_duration + construction_duration - 4),
            pd.Timestamp(project_start_date) + pd.DateOffset(months=acquisition_duration + planning_duration + design_duration + construction_duration - 2),
            pd.Timestamp(project_start_date) + pd.DateOffset(months=project_duration_months)
        ],
        'Status': ['Not Started'] * 11
    }
    
    df_milestones = pd.DataFrame(milestone_data)
    
    # Allow status updates
    for i, milestone in enumerate(df_milestones['Milestone']):
        status = st.selectbox(
            f"Status - {milestone}",
            options=['Not Started', 'In Progress', 'Completed', 'Delayed'],
            key=f"milestone_{i}"
        )
        df_milestones.loc[i, 'Status'] = status
    
    # Format dates for display
    df_milestones['Planned Date'] = df_milestones['Planned Date'].dt.strftime('%d %b %Y')
    
    # Display milestone table
    st.table(df_milestones)

# Add this function after the imports
def create_pdf_report(project_name, project_location, project_type, project_size_sqft, 
                     gross_development_value, total_development_costs, profit, profit_margin,
                     return_on_equity, fig_cashflow, fig_costs, df_metrics, df_detailed_costs,
                     fig_scenarios, fig_gantt, df_milestones, recommendations):
    """
    Create a PDF report with all the dashboard information
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Set up the PDF
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Property Development Report: {project_name}', 0, 1, 'C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Location: {project_location} | Type: {project_type} | Size: {project_size_sqft:,} sq ft', 0, 1, 'C')
    pdf.ln(5)
    
    # Key Financial Metrics
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Key Financial Metrics', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Gross Development Value: £{gross_development_value:,.0f}', 0, 1, 'L')
    pdf.cell(0, 10, f'Total Development Costs: £{total_development_costs:,.0f}', 0, 1, 'L')
    pdf.cell(0, 10, f'Profit: £{profit:,.0f}', 0, 1, 'L')
    pdf.cell(0, 10, f'Profit Margin: {profit_margin:.2f}%', 0, 1, 'L')
    pdf.cell(0, 10, f'Return on Equity: {return_on_equity:.2f}%', 0, 1, 'L')
    pdf.ln(5)
    
    # Save charts as images and add to PDF
    # Cashflow chart
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Project Cashflow', 0, 1, 'L')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        pio.write_image(fig_cashflow, tmp.name, width=800, height=400)
        pdf.image(tmp.name, x=10, y=None, w=190)
        os.unlink(tmp.name)
    
    pdf.ln(5)
    
    # Cost breakdown chart
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Development Cost Breakdown', 0, 1, 'L')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        pio.write_image(fig_costs, tmp.name, width=600, height=400)
        pdf.image(tmp.name, x=10, y=None, w=190)
        os.unlink(tmp.name)
    
    pdf.ln(5)
    
    # Financial metrics table
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
    
    # Scenario comparison
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Scenario Comparison', 0, 1, 'L')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        pio.write_image(fig_scenarios, tmp.name, width=800, height=400)
        pdf.image(tmp.name, x=10, y=None, w=190)
        os.unlink(tmp.name)
    
    pdf.ln(5)
    
    # Project timeline
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Project Timeline', 0, 1, 'L')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        pio.write_image(fig_gantt, tmp.name, width=800, height=400)
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
    pdf.cell(0, 10, f'Property Development Financial Report - Generated on {datetime.now().strftime("%d %b %Y")}', 0, 0, 'C')
    
    return pdf

def send_email(email_address, pdf_data, project_name):
    """
    Send the PDF report via email
    """
    try:
        # This is a placeholder - in a real application, you would use your own SMTP server
        # and credentials. For security reasons, these should be stored as environment variables.
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_username = os.environ.get('SMTP_USERNAME', 'neilpatel247@gmail.com')
        smtp_password = os.environ.get('SMTP_PASSWORD', 'fnxn idpz srlf velh')
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email_address
        msg['Subject'] = f"Property Development Report: {project_name}"
        
        # Email body
        body = f"""
        Dear Client,
        
        Please find attached the property development financial report for {project_name}.
        
        This report includes financial metrics, cashflow projections, cost breakdowns, and recommendations.
        
        Best regards,
        Property Development Dashboard
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        attachment = MIMEApplication(pdf_data, _subtype='pdf')
        attachment.add_header('Content-Disposition', 'attachment', filename=f"{project_name}_report.pdf")
        msg.attach(attachment)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

# Add this at the top of the main dashboard, after the title
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
            project_name, 
            project_location, 
            project_type, 
            project_size_sqft,
            gross_development_value, 
            total_development_costs, 
            profit, 
            profit_margin,
            return_on_equity, 
            fig_cashflow, 
            fig_costs, 
            df_metrics, 
            df_detailed_costs,
            fig_scenarios, 
            fig_gantt, 
            df_milestones, 
            recommendations
        )
        
        # Save PDF to BytesIO - fix for the error
        pdf_output = BytesIO()
        pdf_data = pdf.output(dest='S').encode('latin1')  # Use 'S' to return as string
        pdf_output.write(pdf_data)
        pdf_output.seek(0)
        
        # Create download link
        b64_pdf = base64.b64encode(pdf_output.getvalue()).decode('utf-8')
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{project_name}_report.pdf">Download PDF Report</a>'
        st.markdown(href, unsafe_allow_html=True)
        
        # Send email if address provided
        if email_address:
            success, message = send_email(email_address, pdf_output.getvalue(), project_name)
            if success:
                st.success(message)
            else:
                st.error(message) 