import streamlit as st
import back

def main():
    st.title("Stock Analysis Tool")
    start_date = st.sidebar.date_input("Select Start Date:", format='DD-MM-YYYY').strftime("%d-%m-%Y")
    end_date = st.sidebar.date_input("Select End Date:", format='DD-MM-YYYY').strftime("%d-%m-%Y")

    if 'btn_clicked' not in st.session_state:
        st.session_state['btn_clicked'] = False


    def callback():
    # change state value
        st.session_state['btn_clicked'] = True


    if st.button('Get Symbol', on_click=callback) or st.session_state['btn_clicked']:
        
        if 'symbols' not in st.session_state:
            st.session_state.symbols = back.get_options_after_ema(start_date, end_date)
        st.session_state.symbol = st.sidebar.selectbox("Enter Symbol", st.session_state['symbols'])

    if st.button("Calculate"):
        percentage, avg, curr_price = back.calculate_percentage(st.session_state.symbol, start_date, end_date)
        difference, dates, close_value = back.calculate_difference()
        ema = back.calculate_ema(close_value)

        if percentage is not None:
            st.sidebar.write(f"Current Price: {curr_price:.2f}")
            st.sidebar.write(f"Percentage Change: {percentage:.2f}%")
            st.sidebar.write(f"Pivot for date range: {avg:.2f}")
            st.sidebar.write(f"EMA: {ema.iloc[-1]:.2f}")

        if difference is not None:
            # Add tabs
             with st.expander("Plot", expanded=True):
                back.plot_close_three(dates,close_value,ema,avg)

if __name__=="__main__":
    main()