
import streamlit as st
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import qrcode

st.set_page_config(
    page_title="Elegant Leaf",
    page_icon="🍃",
    layout="wide"
)

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("elegant_leaf_products.csv")

# -----------------------------
# SESSION STATE
# -----------------------------
if "cart" not in st.session_state:
    st.session_state.cart = []

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
.main {
    background-color: #f7f4ed;
}

.hero {
    background: linear-gradient(135deg, #0f5132, #198754);
    padding: 35px;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 25px;
}

.product-card {
    background: white;
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}

.price-tag {
    font-size: 26px;
    color: #198754;
    font-weight: bold;
}

.small-text {
    color: gray;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HERO SECTION
# -----------------------------
st.markdown("""
<div class="hero">
    <h1>🍃 Elegant Leaf</h1>
    <h3>Premium Wellness Tea Collection</h3>
    <p>Natural Herbal Blends for Better Living</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("🔍 Explore")

search = st.sidebar.text_input("Search Product")

selected_category = st.sidebar.multiselect(
    "Category",
    df["Category"].unique()
)

price_range = st.sidebar.slider(
    "Price Range",
    int(df["Price"].min()),
    int(df["Price"].max()),
    (
        int(df["Price"].min()),
        int(df["Price"].max())
    )
)

# -----------------------------
# FILTERS
# -----------------------------
filtered_df = df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df["Product Name"].str.contains(search, case=False)
    ]

if selected_category:
    filtered_df = filtered_df[
        filtered_df["Category"].isin(selected_category)
    ]

filtered_df = filtered_df[
    (filtered_df["Price"] >= price_range[0]) &
    (filtered_df["Price"] <= price_range[1])
]

# -----------------------------
# PRODUCT GRID
# -----------------------------
st.subheader(f"🌿 Products Found: {len(filtered_df)}")

cols = st.columns(3)

for idx, row in filtered_df.iterrows():

    with cols[idx % 3]:

        st.markdown('<div class="product-card">', unsafe_allow_html=True)

        try:
            st.image(row["Image"], use_container_width=True)
        except:
            st.warning("Image not found")

        st.markdown(f"## {row['Product Name']}")
        st.markdown(f"<div class='price-tag'>₹{row['Price']}</div>", unsafe_allow_html=True)

        st.write(f"**Category:** {row['Category']}")
        st.write(f"**Weight:** {row['Weight']}")
        st.write(f"**Benefits:** {row['Benefits']}")

        quantity = st.number_input(
            f"Quantity_{idx}",
            min_value=1,
            max_value=10,
            value=1,
            label_visibility="collapsed"
        )

        if st.button(f"🛒 Add to Cart {idx}"):
            item = row.to_dict()
            item["Quantity"] = quantity
            item["Total"] = quantity * row["Price"]
            st.session_state.cart.append(item)
            st.success("Added to cart!")

        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# CART SECTION
# -----------------------------
st.markdown("---")
st.header("🛍️ Shopping Cart")

if st.session_state.cart:

    cart_df = pd.DataFrame(st.session_state.cart)

    st.dataframe(cart_df[[
        "Product Name",
        "Quantity",
        "Price",
        "Total"
    ]])

    grand_total = cart_df["Total"].sum()

    st.subheader(f"Grand Total: ₹{grand_total}")

    if st.button("🗑️ Clear Cart"):
        st.session_state.cart = []
        st.success("Cart Cleared")

else:
    st.info("Your cart is empty")

# -----------------------------
# CHECKOUT
# -----------------------------
st.markdown("---")
st.header("💳 Checkout")

if st.session_state.cart:

    invoice_df = pd.DataFrame(st.session_state.cart)

    grand_total = invoice_df["Total"].sum()

    # -----------------------------
    # CUSTOMER DETAILS
    # -----------------------------
    st.markdown("""
    <div class="product-card">
        <h3>🧾 Customer Information</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        customer_name = st.text_input(
            "👤 Full Name"
        )

        customer_phone = st.text_input(
            "📞 Phone Number"
        )

    with col2:

        customer_email = st.text_input(
            "📧 Email Address"
        )

        customer_address = st.text_area(
            "🏠 Delivery Address"
        )

    # -----------------------------
    # PAYMENT METHOD
    # -----------------------------
    payment_method = st.selectbox(
        "💰 Select Payment Method",
        [
            "Cash on Delivery",
            "UPI Payment"
        ]
    )

    # -----------------------------
    # UPI PAYMENT
    # -----------------------------
    if payment_method == "UPI Payment":

        st.subheader("📱 Pay Using UPI")

        upi_id = "bmukherjee2k7@oksbi"

        upi_link = (
            f"upi://pay?"
            f"pa={upi_id}"
            f"&pn=ElegantLeaf"
            f"&am={grand_total}"
            f"&cu=INR"
        )

        st.markdown(f"""
        <a href="{upi_link}">
            <button style="
                background-color:#198754;
                color:white;
                padding:14px 24px;
                border:none;
                border-radius:10px;
                font-size:18px;
                cursor:pointer;
                width:100%;
            ">
                Pay ₹{grand_total} via UPI
            </button>
        </a>
        """, unsafe_allow_html=True)

        # QR CODE
        qr = qrcode.make(upi_link)

        qr.save("upi_qr.png")

        st.image(
            "upi_qr.png",
            caption="Scan QR using Google Pay / PhonePe / Paytm",
            width=260
        )

        st.info(
            "After successful payment click Generate Invoice"
        )

    # -----------------------------
    # GENERATE INVOICE
    # -----------------------------
    if st.button("📄 Generate Invoice"):

        # VALIDATION
        if (
            customer_name == "" or
            customer_phone == "" or
            customer_email == "" or
            customer_address == ""
        ):

            st.error(
                "Please fill all customer details"
            )

            st.stop()

        pdf_file = "ElegantLeaf_Invoice.pdf"

        doc = SimpleDocTemplate(pdf_file)

        styles = getSampleStyleSheet()

        elements = []

        # TITLE
        elements.append(
            Paragraph(
                "Elegant Leaf Invoice",
                styles["Title"]
            )
        )

        elements.append(Spacer(1, 20))

        # CUSTOMER DETAILS
        elements.append(
            Paragraph(
                f"<b>Customer:</b> {customer_name}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"<b>Phone:</b> {customer_phone}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"<b>Email:</b> {customer_email}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"<b>Address:</b> {customer_address}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"<b>Payment Method:</b> {payment_method}",
                styles["Normal"]
            )
        )

        elements.append(Spacer(1, 20))

        # PRODUCT TABLE
        table_data = [[
            "Product",
            "Qty",
            "Price",
            "Total"
        ]]

        for _, r in invoice_df.iterrows():

            table_data.append([
                r["Product Name"],
                r["Quantity"],
                f"₹{r['Price']}",
                f"₹{r['Total']}"
            ])

        # GRAND TOTAL
        table_data.append([
            "",
            "",
            "Grand Total",
            f"₹{grand_total}"
        ])

        table = Table(table_data)

        table.setStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.darkgreen),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0,0), (-1,0), 10),
            ("BACKGROUND", (0,-1), (-1,-1), colors.lightgreen)
        ])

        elements.append(table)

        elements.append(Spacer(1, 25))

        # THANK YOU NOTE
        elements.append(
            Paragraph(
                "Thank you for shopping with Elegant Leaf 🌿",
                styles["Normal"]
            )
        )

        doc.build(elements)

        st.success(
            "✅ Invoice Generated Successfully!"
        )

        # DOWNLOAD BUTTON
        with open(pdf_file, "rb") as f:

            st.download_button(
                "⬇ Download Invoice",
                f,
                file_name="ElegantLeaf_Invoice.pdf"
            )
# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption("🍃 Elegant Leaf | Premium Herbal Wellness Store")
