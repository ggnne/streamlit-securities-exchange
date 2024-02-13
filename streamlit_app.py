from io import StringIO
import json
import logging.config
import pathlib

import streamlit as st
from securities_exchange import SecuritiesExchange, Order, OrderType, MarketSide

st.set_page_config(layout="wide")
st.title("Securities Exchange App")
st.markdown("```'allow_market_queue' is set to False, Market Orders will be filled given the available liquidity and then leave the exchange.```")

if "exchange" not in st.session_state:
    st.session_state.exchange = SecuritiesExchange(verbose=True)

if "log_stream" not in st.session_state:
    config_file = pathlib.Path("logging_config/config.json")
    with open(config_file) as f:
        config = json.load(f)
    st.session_state.log_stream = StringIO()
    config["handlers"]["io_stream"]["stream"] = st.session_state.log_stream
    logging.config.dictConfig(config=config)

if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "Submit Order"

if st.session_state.selected_tab == "Submit Order":

    st.header("Order Form")

    columns = st.columns(5)
    ticker = columns[0].text_input("Ticker", placeholder="MSFT").upper()
    order_type = columns[1].radio("Order Type", ["LIMIT", "MARKET"])
    side = columns[2].radio("Side", ["BUY", "SELL"])
    size = columns[3].number_input("Size", min_value=1, step=1)
    price = columns[4].number_input("Price", min_value=0.01, step=0.01) if order_type == "LIMIT" else None

    if st.button("Submit Order"):
        if order_type == "MARKET":
            order = Order(ticker, OrderType.MARKET, MarketSide.BUY if side == "BUY" else MarketSide.SELL, size)
        else:
            order = Order(ticker, OrderType.LIMIT, MarketSide.BUY if side == "BUY" else MarketSide.SELL, size, price)
        response = st.session_state.exchange.submit_order(order)

    st.write("")

elif st.session_state.selected_tab == 'Order Lookup':
    st.header("Order Lookup")

    order_id = st.text_input("Enter Order ID:")

    if st.button("Lookup Order"):
        order = st.session_state.exchange.get_order(order_id)
        
        if order:
            msg = (
                f"**Order Details:**\n\n"
                f"- **Order Status:** {order.status.name}\n"
                f"- **Order ID:** {order.id}\n"
                f"- **Ticker:** {order.ticker}\n"
                f"- **Order Type:** {order.type.name}\n"
                f"- **Side:** {order.side.name}\n"
                f"- **Size:** {order.size}\n"
                f"- **Price:** {order.price}\n"
                f"- **Residual size:** {order.residual_size}\n"
                f"- **Avg. Fill Price:** {order.avg_fill_price:.2f}\n"
                f"- **Matches:** {order.matches}"
            )

            st.markdown(msg, unsafe_allow_html=True)
        else:
            st.write("Order not found.")

    st.write("")

logs = st.session_state.log_stream.getvalue().splitlines()
st.text_area("Logs", "\n".join(logs), height=400)

st.sidebar.markdown("### Navigation")
tabs = ['Submit Order', 'Order Lookup']
new_tab = st.sidebar.radio("Select Tab", tabs, index=tabs.index(st.session_state.selected_tab))

if new_tab != st.session_state.selected_tab:
    st.session_state.selected_tab = new_tab
    st.rerun()
