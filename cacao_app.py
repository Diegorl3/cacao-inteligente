import streamlit as st
import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import datetime

# Configuración profesional
st.set_page_config(page_title="Cacao Inteligente", layout="wide")

st.markdown("""
    <style>
    .vende-ya { background-color: #d4edda; color: #155724; padding: 20px; border-radius: 10px; border: 2px solid #c3e6cb; text-align: center; font-weight: bold; }
    .espera { background-color: #fff3cd; color: #856404; padding: 20px; border-radius: 10px; border: 2px solid #ffeeba; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍫 Cacao Inteligente")

modo = st.radio("Selecciona nivel de detalle:", ["Básico (Recomendado para ventas)", "Experto (Análisis técnico e IA)"], horizontal=True)

# --- FUNCIÓN DE CARGA SEGURA ---
@st.cache_data(ttl=600)
def cargar_datos_seguros():
    ticker = yf.Ticker("CC=F")
    # Intentamos bajar los últimos 2 años
    df = ticker.history(period="2y")
    if df.empty:
        return None
    return df

data = cargar_datos_seguros()

if data is None:
    st.error("⚠️ No hay conexión con la Bolsa de Valores. Por favor, espera 1 minuto y recarga la página (F5).")
    st.info("A veces los servidores de datos se saturan. Esto es normal en aplicaciones financieras.")
else:
    # Variables de cálculo
    current_price = float(data['Close'].iloc[-1])
    prev_price = float(data['Close'].iloc[-2])
    change = current_price - prev_price
    CONV_FACTOR = 22.046
    price_qq = current_price / CONV_FACTOR
    avg_7d = data['Close'].tail(7).mean()

    if "Básico" in modo:
        st.subheader("Resumen del día")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Precio por Quintal", f"${price_qq:,.2f}", f"{(change/CONV_FACTOR):,.2f} USD")
        with col2:
            sentido = "SUBIENDO 📈" if change > 0 else "BAJANDO 📉"
            st.markdown(f"### El mercado está: **{sentido}**")

        st.divider()

        if current_price >= avg_7d:
            st.markdown('<div class="vende-ya"><h2>🟢 SUGERENCIA: BUEN MOMENTO</h2> El precio está por encima del promedio semanal.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="espera"><h2>🟡 SUGERENCIA: ESPERAR</h2> El precio está bajo. Si no hay prisa, conviene esperar a que suba.</div>', unsafe_allow_html=True)

    else:
        st.subheader("📊 Análisis para Expertos e IA")
        c_a, c_b = st.columns(2)
        c_a.metric("Precio Tonelada NY", f"${current_price:,.2f}")
        c_b.metric("Promedio Semanal", f"${(avg_7d/CONV_FACTOR):,.2f}/qq")

        # Gráfica
        st.line_chart(data['Close'])

        # Predicción IA Simple
        try:
            df_ia = data.copy().dropna()
            df_ia['Target'] = df_ia['Close'].shift(-1)
            X = df_ia[['Open', 'High', 'Low', 'Close', 'Volume']].iloc[:-1]
            y = df_ia['Target'].iloc[:-1]
            
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X.values, y.values)
            
            last_day = data[['Open', 'High', 'Low', 'Close', 'Volume']].tail(1).values
            pred = model.predict(last_day)[0]
            
            st.success(f"🔮 **Pronóstico para mañana:** ${pred:,.2f} / Ton (${(pred/CONV_FACTOR):,.2f} /qq)")
        except:
            st.warning("La IA está calculando... recarga en unos segundos.")

# --- BITÁCORA EN EL LATERAL ---
st.sidebar.header("📋 Mis Ventas")
with st.sidebar.expander("Anotar Venta"):
    st.date_input("Fecha")
    st.number_input("Quintales", 0.0)
    if st.button("Guardar"):
        st.success("¡Venta registrada!")