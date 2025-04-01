import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import datetime

# Set page configuration
st.set_page_config(
    page_title="Investment Portfolio Advisor",
    page_icon="💰",
    layout="wide"
)

# Database functions
def setup_database():
    # Initialize SQLite database
    try:
        conn = sqlite3.connect('investment_advisor.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            income REAL,
            savings REAL,
            risk_score REAL,
            target_return REAL,
            investment_goals TEXT
        )
        ''')
        
        # Create portfolios table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            allocation TEXT,
            initial_investment REAL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def save_user_portfolio(user_data, portfolio_data):
    # store user and portfolio data to database
    try:
        conn = sqlite3.connect('investment_advisor.db')
        cursor = conn.cursor()
        
        # Insert user data
        cursor.execute('''
        INSERT INTO users (name, income, savings, risk_score, target_return, investment_goals)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_data['name'],
            user_data['income'],
            user_data['savings'],
            user_data['risk_score'],
            user_data['target_return'],
            str(user_data['investment_goals']),
        ))
        
        user_id = cursor.lastrowid
        
        # Insert portfolio data
        cursor.execute('''
        INSERT INTO portfolios (user_id, allocation, initial_investment)
        VALUES (?, ?, ?)
        ''', (
            user_id,
            str(portfolio_data['allocation']),
            portfolio_data['initial_investment'],
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database save error: {e}")
        return False

# Load default assets
def load_default_assets():
    # default investment assets
    return [
        {"name": "Nifty 500 ETF", "type": "stock", "return": 0.10, "risk": 0.8, "price": 450.0},
        {"name": "Total Bond ETF", "type": "bond", "return": 0.04, "risk": 0.3, "price": 80.0},
        {"name": "Gold ETF", "type": "commodity", "return": 0.05, "risk": 0.6, "price": 180.0},
        {"name": "Real Estate ETF", "type": "real_estate", "return": 0.08, "risk": 0.7, "price": 95.0},
        {"name": "High-Yield Dividend ETF", "type": "stock", "return": 0.07, "risk": 0.6, "price": 55.0},
        {"name": "Treasury Bonds", "type": "bond", "return": 0.03, "risk": 0.2, "price": 100.0},
        {"name": "International Stocks ETF", "type": "stock", "return": 0.09, "risk": 0.8, "price": 65.0},
        {"name": "Emerging Markets ETF", "type": "stock", "return": 0.11, "risk": 0.9, "price": 45.0},
        {"name": "Technology Sector ETF", "type": "stock", "return": 0.12, "risk": 0.9, "price": 160.0},
        {"name": "Corporate Bonds ETF", "type": "bond", "return": 0.05, "risk": 0.4, "price": 110.0}
    ]

# Risk assessment function
def risk_assessment():
    # Questions for user's risk tolerance
    st.subheader("Risk Assessment Questionnaire")
    st.write("Please answer the following questions to determine your risk tolerance.")
    
    questions = [
        {
            "question": "How would you react if your portfolio lost 20% of its value in a month?",
            "options": [
                "Sell everything immediately ",
                "Sell some investments to cut losses ",
                "Do nothing and wait for recovery ",
                "Buy more at the lower prices "
            ],
            "scores": [1, 3, 5, 10]
        },
        {
            "question": "How long do you keep your money invested?",
            "options": [
                "Less than 2 years ",
                "2-5 years ",
                "5-10 years ",
                "More than 10 years "
            ],
            "scores": [1, 4, 7, 10]
        },
        {
            "question": "What is your primary investment goal?",
            "options": [
                "Preserve capital ",
                "Generate income ",
                "Balanced growth and income ",
                "Maximize growth "
            ],
            "scores": [1, 4, 7, 10]
        },
        {
            "question": "How much financial knowledge do you have?",
            "options": [
                "Very little ",
                "Basic understanding ",
                "Good knowledge ",
                "Advanced/Professional "
            ],
            "scores": [2, 5, 8, 10]
        }       
    ]
    
    total_score = 0
    max_score = 0
    
    for q in questions:
        choice = st.radio(q["question"], q["options"])
        # Get index of selected choice
        index = q["options"].index(choice)
        # Add score
        total_score += q["scores"][index]
        max_score += 10
    
    # Normalize to 0-1 scale
    risk_score = total_score / max_score
    
    if risk_score < 0.3:
        risk_category = "low"
    elif risk_score < 0.7:
        risk_category = "medium"
    else:
        risk_category = "high"
    
    st.subheader("Your Risk Profile")
    st.write(f"Risk Score: {risk_score*100 :.2f}")
    st.write(f"Risk Category: {risk_category}")
    
    return risk_score

# Portfolio allocation function
def recommend_allocation(assets, risk_score):
    # Recommend asset allocation based on user's risk level
    allocation = {}
    
    if risk_score < 0.3:
            risk_category = "low"
    elif risk_score < 0.7:
        risk_category = "medium"
    else:
        risk_category = "high"

    # Basic asset classes
    asset_classes = {
        "stock": {"low": 0.30, "medium": 0.50, "high": 0.70},
        "bond": {"low": 0.50, "medium": 0.30, "high": 0.10},
        "commodity": {"low": 0.10, "medium": 0.10, "high": 0.10},
        "real_estate": {"low": 0.10, "medium": 0.10, "high": 0.10}
    }
    
    # Create asset_by_type dict according to type of asset ex.Stock,Bond,Etc.
    asset_by_type = {}
    for asset in assets:
        asset_type = asset["type"]
        if asset_type not in asset_by_type:
            asset_by_type[asset_type] = []
        asset_by_type[asset_type].append(asset)

# asset_class->This variable represents a specific type of asset
# allocations->This varable contain dictionary of value of asset_classes
# class_assets->Take a assest class sub dict
# allocation->contain the ammount of distribution of percentage

    # Set allocation for each asset class
    for asset_class, allocations in asset_classes.items():
        if asset_class in asset_by_type:
            class_assets = asset_by_type[asset_class]
            pct = allocations[risk_category]
            
            if class_assets:
                if risk_category == "high":
                    # Sort by return (high for high risk)
                    class_assets = sorted(class_assets, key=lambda x: x["return"], reverse=True)
                elif risk_category == "low":
                    # Sort by risk level (low risk first)
                    class_assets = sorted(class_assets, key=lambda x: x["risk"])
                
                class_allocation = pct / len(class_assets)
                for asset in class_assets:
                    allocation[asset["name"]] = class_allocation
    
    return allocation

# Portfolio simulation function
def simulate_growth(initial_investment, allocation, assets, years=5):
    # Show portfolio growth over specified years
    try:
        inflation_rate = 0.06 #6% inflation  
       
        # Create a date range for the simulation
        start_date = datetime.datetime.now()
        date_range = []
        for month in range(years * 12 + 1):
            # Add months to start date
            new_date = start_date.replace(month=((start_date.month - 1 + month) % 12) + 1,
                                         year=start_date.year + ((start_date.month - 1 + month) // 12))
            date_range.append(new_date)
        
        # Initialize results dataframe
        results = pd.DataFrame({
            'Date': date_range,
            'Year': [d.year for d in date_range],
            'Month': [d.month for d in date_range],
            'Total_Value': 0.0,
            'Inflation_Adjusted_Value': 0.0
        })
        
        # Add columns for each asset
        for asset in assets:
            results[asset["name"]] = 0.0
        
        # Initial allocation
        for asset in assets:
            if asset["name"] in allocation:
                results.loc[0, asset["name"]] = initial_investment * allocation[asset["name"]]
        
        results.loc[0, 'Total_Value'] = initial_investment
        results.loc[0, 'Inflation_Adjusted_Value'] = initial_investment
        
        # Simulate monthly growth
        for i in range(1, len(results)):
            for asset in assets:
                if asset["name"] in allocation:
                    # Monthly return (annual return / 12)
                    monthly_return = asset["return"] / 12
                    
                    # Previous value
                    prev_value = results.loc[i-1, asset["name"]]
                    
                    # New value with growth
                    new_value = prev_value * (1 + monthly_return)
                    results.loc[i, asset["name"]] = new_value
            
            # Calculate total value for this month
            asset_values = [results.loc[i, asset["name"]] for asset in assets if asset["name"] in allocation]
            results.loc[i, 'Total_Value'] = sum(asset_values)
            
            # Apply monthly inflation
            monthly_inflation = inflation_rate / 12
            results.loc[i, 'Inflation_Adjusted_Value'] = results.loc[i, 'Total_Value'] / (1 + monthly_inflation) ** i
        
        return results
    except Exception as e:
        st.error(f"Simulation error: {e}")
        return pd.DataFrame()

# Generate recommendations function
def generate_recommendations(user_data, portfolio_data, assets, simulation_results):
    # Generate personalized recommendations based on portfolio analysis
    recommendations = []
    
    try:
        # Calculate expected return
        expected_return = 0
        for asset in assets:
            if asset["name"] in portfolio_data["allocation"]:
                expected_return += asset["return"] * portfolio_data["allocation"][asset["name"]]
        
        # Compare with target return
        if expected_return < user_data["target_return"]:
            gap = (user_data["target_return"] - expected_return) * 100
            recommendations.append(
                f"Your current allocation may not meet your target annual return of {user_data['target_return'] * 100:.2f}%. "
                f"Consider increasing your allocation to higher-return assets to close the {gap:.2f}% gap."
            )
        
        # Diversification check
        high_allocation = []
        for asset_name, alloc in portfolio_data["allocation"].items():
            if alloc > 0.3:
                high_allocation.append(asset_name)
                
        if high_allocation:
            asset_names = ", ".join(high_allocation)
            recommendations.append(
                f"You have a high concentration in {asset_names}. Consider diversifying to reduce risk."
            )
        
        # Savings rate recommendation based on income
        recommended_savings = user_data["income"] * 0.2
        current_investment = portfolio_data["initial_investment"]
        
        if current_investment < recommended_savings:
            recommendations.append(
                f"Consider increasing your investment amount. A good target is 20% of your annual income (Rs.{recommended_savings:,.2f})."
            )
        
        # Long-term growth recommendation
        if not simulation_results.empty:
            final_value = simulation_results.iloc[-1]['Total_Value']
            initial_investment = portfolio_data["initial_investment"]
            total_growth = (final_value - initial_investment) / initial_investment
            
            if total_growth < 0.5:  # Less than 50% growth over simulation period
                recommendations.append(
                    "Your long-term growth projection is lower than average. Consider increasing your investment horizon or adjusting your asset allocation for better long-term results."
                )
        
        return recommendations
    except Exception as e:
        st.error(f"Recommendation generation error: {e}")
        return ["Unable to generate recommendations due to an error."]

# Create portfolio summary visualizations
def create_portfolio_visualizations(portfolio_data, simulation_results):
    """Create visualizations for portfolio allocation and growth"""
    try:
        fig = plt.figure(figsize=(15,8))

        # Plot 1: Asset Allocation Pie Chart (top-left)
        plt.subplot(1,2,1)
        labels = list(portfolio_data["allocation"].keys())
        sizes = [portfolio_data["allocation"][asset] * 100 for asset in labels]
        
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title('Asset Allocation')
        plt.axis('equal')
        
        # Plot 2: Portfolio Growth Over Time (top-right)
        plt.subplot(1,2,2)
        plt.plot(simulation_results['Date'], simulation_results['Total_Value'], label='Projected Value')
        plt.plot(simulation_results['Date'], simulation_results['Inflation_Adjusted_Value'],label='Inflation Adjusted', linestyle='--')
        plt.title('Portfolio Growth Projection')
        plt.xlabel('Date')
        plt.ylabel('Value (INR)')
        plt.legend()
        plt.grid(True)
         
        plt.tight_layout()
        return fig
    except Exception as e:
        st.error(f"Visualization error: {e}")
        return None

# Main Streamlit app
def main():
    # Setup database
    setup_database()
    import streamlit as st

    # Title and description
    st.title("Personalized Investment Portfolio Advisor")
    st.write("""
    This application helps you create a personalized investment portfolio based on your financial profile, 
    risk tolerance, and investment goals. It provides asset allocation recommendations, 
    portfolio growth simulations, and financial insights.
    """)
    
    # Load default assets
    assets = load_default_assets()
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4= st.tabs(["User Profile", "Portfolio Analysis", "Recommendations", "Presentation"])
    
    # Initialize session state to store user data
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'portfolio_data' not in st.session_state:
        st.session_state.portfolio_data = None
    if 'simulation_results' not in st.session_state:
        st.session_state.simulation_results = None
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    
    with tab1:
        st.header("Your Financial Profile")
        
        # Collect user information
        with st.form("user_info_form"):
            st.subheader("Personal Information")
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name")
                income = st.number_input("Annual Income (INR)", min_value=0.0, format="%.2f")
            
            with col2:
                savings = st.number_input("Total Savings (INR)", min_value=0.0, format="%.2f")
                target_return = st.slider("Target Annual Return (%)", min_value=1, max_value=20, value=8) / 100
            
            st.subheader("Investment Goals")
            available_goals = ["Retirement", "Education", "Home Purchase", "Vacation",  "Wealth Building"]
            
            # Display goals as multiple checkboxes
            selected_goals = []
            goal_cols = st.columns(3)
            for i, goal in enumerate(available_goals):
                col_idx = i % 3
                with goal_cols[col_idx]:
                    if st.checkbox(goal):
                        selected_goals.append(goal)
            
            # Risk assessment questionnaire
            risk_score = risk_assessment()
            
            # Submit button
            submit_button = st.form_submit_button("Submit")
            
            if submit_button:
                if not name:
                    st.error("Please enter your name.")
                elif not selected_goals:
                    st.error("Please select at least one investment goal.")
                else:
                    # Store user data in session state
                    st.session_state.user_data = {
                        "name": name,
                        "income": income,
                        "savings": savings,
                        "risk_score":float(risk_score),
                        "target_return": target_return,
                        "investment_goals": selected_goals
                    }
                    
                    st.success("Financial profile submitted successfully!")
                    # Provide navigation instruction
                    st.info("Please proceed to the 'Portfolio Analysis' tab to view your recommended portfolio.")
    
    with tab2:
        st.header("Portfolio Analysis")
        
        if st.session_state.user_data:
            st.write(f"Hello, {st.session_state.user_data['name']}! Let's create your investment portfolio.")
            
            # Investment amount input
            investment_amount = st.slider(
                "Investment Amount (INR)",
                min_value=0,
                max_value=int(st.session_state.user_data["savings"]),
                value=min(10000, int(st.session_state.user_data["savings"] / 2)),
                step=500
            )
            
            # Generate recommended allocation
            allocation = recommend_allocation(assets, st.session_state.user_data["risk_score"])
            
            # Store portfolio data in session state
            st.session_state.portfolio_data = {
                "allocation": allocation,
                "initial_investment": investment_amount
            }
            
            # Display allocation
            st.subheader("Recommended Asset Allocation")
            
            # Create a DataFrame for better display
            allocation_data = []
            for asset_name, alloc_pct in allocation.items():
                asset_info = next((a for a in assets if a["name"] == asset_name), None)
                if asset_info:
                    amount = investment_amount * alloc_pct
                    expected_annual_return = asset_info["return"] * amount
                    allocation_data.append({
                        "Asset": asset_name,
                        "Type": asset_info["type"].capitalize(),
                        "Allocation (%)": f"{alloc_pct * 100:.2f}%",
                        "Amount (Rs.)": f"Rs.{amount:.2f}",
                        "Expected Annual Return": f"Rs.{expected_annual_return:.2f} ({asset_info['return'] * 100:.2f}%)"
                    })
            
            allocation_df = pd.DataFrame(allocation_data)
            st.dataframe(allocation_df)
            
            # Calculate expected return
            expected_return = sum(asset["return"] * allocation.get(asset["name"], 0) for asset in assets)
            st.write(f"Expected Annual Return: {expected_return * 100:.2f}%")
            
            # Portfolio simulation
            st.subheader("Portfolio Growth Simulation")
            years = st.slider("Simulation Years", min_value=1, max_value=15, value=5)
            
            if st.button("Run Simulation"):
                with st.spinner("Running simulation..."):
                    simulation_results = simulate_growth(
                        investment_amount,
                        allocation,
                        assets,
                        years=years,
                    )
                    
                    st.session_state.simulation_results = simulation_results
                    
                    # Create visualizations
                    fig = create_portfolio_visualizations(
                        st.session_state.portfolio_data,
                        simulation_results
                    )
                    
                    if fig:
                        st.pyplot(fig)
                    
                    # Generate recommendations
                    recommendations = generate_recommendations(
                        st.session_state.user_data,
                        st.session_state.portfolio_data,
                        assets,
                        simulation_results
                    )
                    
                    st.session_state.recommendations = recommendations
                    
                    # Navigation instruction
                    st.info("Please visit the 'Recommendations' tab to view your personalized financial insights.")
            
            # Display sample message if simulation hasn't been run
            if st.session_state.simulation_results is None:
                st.write("Click 'Run Simulation' to see how your portfolio might grow over time.")
        else:
            st.warning("Please complete your financial profile in the 'User Profile' tab first.")
    
    with tab3:
        st.header("Personalized Recommendations")
        
        if st.session_state.recommendations:
            save_user_portfolio(st.session_state.user_data,st.session_state.portfolio_data)
            for i, rec in enumerate(st.session_state.recommendations, 1):
                st.write(f"{i}. {rec}")
    
    with tab4:
        st.header("Presentation")
        st.markdown(
        """
        <iframe src="https://docs.google.com/presentation/d/e/2PACX-1vTc3oqEbDQsRpJ1nJY7H-9R85Yo5vHHdYPwUp7Q5ZEKjZFyMXK7a3ftndk8yAtq4w/embed?start=true&loop=false&delayms=60000" 
        frameborder="0" width="1000" height="360" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>""",
        unsafe_allow_html=True
        )
main() 

# Run this code using "streamlit run main.py" in terminal of VS CODE