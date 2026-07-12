import streamlit as st

def load_css():

    st.markdown("""
    <style>

    /* ==========================
       Main App
    ========================== */

    .stApp{
        background: #0F172A;
        color: #FFFFFF;
    }

    .main{
        padding: 2rem 3rem;
    }

    /* ==========================
       Hero Section
    ========================== */

    .hero{

        background: linear-gradient(
            135deg,
            #1E293B,
            #0F172A
        );

        border:1px solid #334155;

        border-radius:20px;

        padding:35px;

        text-align:center;

        margin-bottom:30px;

        box-shadow:0px 10px 30px rgba(0,0,0,.25);

    }

    .hero h1{

        font-size:52px;

        font-weight:700;

        color:white;

        margin-bottom:10px;

    }

    .hero h3{

        color:#60A5FA;

        font-size:24px;

        margin-bottom:15px;

        font-weight:500;

    }

    .hero p{

        color:#CBD5E1;

        font-size:18px;

        line-height:1.7;

        margin:0;

    }

    /* ==========================
       Select Box
    ========================== */

    .stSelectbox label{

        font-size:18px;

        font-weight:600;

        color:white;

    }

    div[data-baseweb="select"]{

        border-radius:12px;

    }

    /* ==========================
       Button
    ========================== */

    .stButton>button{

        width:100%;

        height:55px;

        border-radius:12px;

        border:none;

        background:#2563EB;

        color:white;

        font-size:18px;

        font-weight:600;

        transition:all .3s ease;

    }

    .stButton>button:hover{

        background:#1D4ED8;

        transform:translateY(-2px);

        box-shadow:0px 8px 20px rgba(37,99,235,.35);

    }

    /* ==========================
       Movie Card
    ========================== */

    .movie-card{

        background:#1E293B;

        border:1px solid #334155;

        border-radius:15px;

        padding:15px;

        text-align:center;

        transition:.3s;

        box-shadow:0px 5px 15px rgba(0,0,0,.25);

        height:100%;

    }

    .movie-card:hover{

        transform:translateY(-8px);

        box-shadow:0px 12px 30px rgba(0,0,0,.35);

    }

    .movie-title{

        color:white;

        font-size:17px;

        font-weight:600;

        margin-top:12px;

        min-height:45px;

    }

    /* ==========================
       Images
    ========================== */

    img{

        border-radius:12px;

    }

    /* ==========================
       Divider
    ========================== */

    hr{

        border:1px solid #334155;

        margin-top:30px;

        margin-bottom:30px;

    }

    /* ==========================
       Footer
    ========================== */

    .footer{

        text-align:center;

        color:#94A3B8;

        margin-top:50px;

        padding:15px;

        font-size:15px;

    }

    /* ==========================
       Metrics
    ========================== */

    div[data-testid="stMetric"]{

        background:#1E293B;

        border:1px solid #334155;

        border-radius:15px;

        padding:15px;

    }

    /* ==========================
       Scroll Bar
    ========================== */

    ::-webkit-scrollbar{

        width:10px;

    }

    ::-webkit-scrollbar-thumb{

        background:#334155;

        border-radius:20px;

    }

    ::-webkit-scrollbar-track{

        background:#0F172A;

    }

    </style>
    """, unsafe_allow_html=True)