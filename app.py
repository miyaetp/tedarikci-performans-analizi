import io
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Tedarikçi Analiz Sistemi | miyaetp",
    page_icon="⚡",
    layout="wide"
)

# Üst Başlık
st.title("📊 Yapay Zekâ Destekli Tedarikçi Performans Dashboard'u")
st.caption("Veri Destekli Tedarikçi Değerlendirme ve Satın Alma Karar Sistemi")

# --- SOL MENÜ (SIDEBAR) ---
st.sidebar.header("⚙️ Değerlendirme Ağırlıkları (%)")
w_ret = st.sidebar.slider("Ret Oranı Ağırlığı", 0, 100, 30, step=5)
w_belge = st.sidebar.slider("Belge Eksikliği Ağırlığı", 0, 100, 25, step=5)
w_uyg = st.sidebar.slider("Uygunsuzluk Ağırlığı", 0, 100, 25, step=5)
w_teslim = st.sidebar.slider("Teslim Süresi Ağırlığı", 0, 100, 20, step=5)

total_weight = w_ret + w_belge + w_uyg + w_teslim
if total_weight != 100:
    st.sidebar.warning(f"Toplam: %{total_weight}. Puanlar %100'e normalize ediliyor.")
    norm_factor = 100 / total_weight if total_weight > 0 else 1
else:
    norm_factor = 1

st.sidebar.divider()
st.sidebar.header("📁 Veri Kaynağı")
data_source = st.sidebar.radio("Kaynak Seçimi:", ["Örnek ERP Verisi Kullan", "Excel/CSV Yükle"])

# Örnek Veri Seti
@st.cache_data
def get_sample_data():
    return pd.DataFrame({
        "Tedarikçi": ["Tedarikçi A", "Tedarikçi B", "Tedarikçi C", "Tedarikçi D", "Tedarikçi E"],
        "Ret Oranı (%)": [1.2, 2.4, 3.5, 5.0, 8.2],
        "Belge Eksikliği (%)": [0.5, 1.8, 2.2, 4.0, 6.5],
        "Uygunsuzluk Sayısı": [1, 2, 4, 6, 9],
        "Ortalama Teslim Gecikmesi (Gün)": [1.1, 2.6, 3.2, 4.5, 6.0]
    })

if data_source == "Excel/CSV Yükle":
    uploaded_file = st.sidebar.file_uploader("Excel veya CSV Seç", type=["xlsx", "csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    else:
        st.info("Lütfen bir veri dosyası yükleyin veya sol menüden örnek veriye geçin.")
        st.stop()
else:
    df = get_sample_data()

# Örnek Şablon İndirme Butonu (Sidebar)
template_io = io.BytesIO()
with pd.ExcelWriter(template_io, engine='openpyxl') as writer:
    get_sample_data().to_excel(writer, index=False, sheet_name='Sablon')
st.sidebar.download_button(
    label="📄 Örnek Excel Şablonunu İndir",
    data=template_io.getvalue(),
    file_name="Tedarikci_Sablonu.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- İMZA ALANI (miyaetp) ---
st.sidebar.divider()
st.sidebar.markdown(
    """
    <div style='background-color: rgba(128, 128, 128, 0.1); padding: 12px; border-radius: 8px; text-align: center;'>
        <p style='margin: 0; font-size: 13px; font-weight: bold;'>Developed by</p>
        <p style='margin: 0; font-size: 18px; color: #FF4B4B; font-weight: 800;'>⚡ miyaetp</p>
        <p style='margin: 0; font-size: 11px; opacity: 0.7;'>v1.2.0 • AI Decision System</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- PUANLAMA MOTORU ---
def calculate_scores(dataframe):
    temp_df = dataframe.copy()
    def normalize_inverse(series):
        if series.max() == series.min():
            return pd.Series(100, index=series.index)
        return 100 * (1 - (series - series.min()) / (series.max() - series.min() + 1e-5))

    ret_score = normalize_inverse(temp_df["Ret Oranı (%)"])
    belge_score = normalize_inverse(temp_df["Belge Eksikliği (%)"])
    uygunsuzluk_score = normalize_inverse(temp_df["Uygunsuzluk Sayısı"])
    teslim_score = normalize_inverse(temp_df["Ortalama Teslim Gecikmesi (Gün)"])

    temp_df["Performans Skoru"] = (
        (ret_score * (w_ret * norm_factor / 100)) +
        (belge_score * (w_belge * norm_factor / 100)) +
        (uygunsuzluk_score * (w_uyg * norm_factor / 100)) +
        (teslim_score * (w_teslim * norm_factor / 100))
    ).round(1)
    return temp_df

analyzed_df = calculate_scores(df)

# Yapay Zeka Karar Motoru
def generate_ai_insight(row):
    reasons = []
    if row["Ret Oranı (%)"] >= 4.0: reasons.append("Yüksek ret oranı")
    if row["Ortalama Teslim Gecikmesi (Gün)"] >= 3.5: reasons.append("Teslim gecikmesi")
    if row["Uygunsuzluk Sayısı"] >= 5: reasons.append("Sık uygunsuzluk")
    if row["Belge Eksikliği (%)"] >= 3.0: reasons.append("Belge eksikliği")

    if row["Performans Skoru"] >= 85:
        return "🟢 Onaylı: Sipariş hacmi artırılabilir, öncelikli tercih edilmeli."
    elif row["Performans Skoru"] >= 65:
        detail = ", ".join(reasons) if reasons else "Parametrelerde dalgalanma"
        return f"🟡 İzleme: {detail} nedeniyle performans takibi yapılmalı."
    else:
        detail = ", ".join(reasons) if reasons else "Kritik limitler aşıldı"
        return f"🔴 Riskli: {detail}. Acil DÖF açılmalı veya alternatif firma değerlendirilmeli."

analyzed_df["YZ Karar Destek"] = analyzed_df.apply(generate_ai_insight, axis=1)

# KPI Kartları
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ortalama Skor", f"{analyzed_df['Performans Skoru'].mean():.1f} / 100")
col2.metric("Ort. Ret Oranı", f"%{analyzed_df['Ret Oranı (%)'].mean():.1f}")
col3.metric("Ort. Belge Eksikliği", f"%{analyzed_df['Belge Eksikliği (%)'].mean():.1f}")
col4.metric("Ort. Gecikme", f"{analyzed_df['Ortalama Teslim Gecikmesi (Gün)'].mean():.1f} Gün")

st.divider()

# Grafikler
tab1, tab2 = st.tabs(["📊 Genel Sıralama & Ağırlıklar", "🎯 Tedarikçi Radar Analizi"])

with tab1:
    col_chart, col_pie = st.columns([3, 2])
    with col_chart:
        sorted_df = analyzed_df.sort_values(by="Performans Skoru", ascending=True)
        fig_bar = px.bar(
            sorted_df, x="Performans Skoru", y="Tedarikçi", orientation="h",
            text="Performans Skoru", color="Performans Skoru", color_continuous_scale="Viridis", range_x=[0, 100]
        )
        fig_bar.update_layout(height=350, margin=dict(l=0, r=20, t=20, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)
    with col_pie:
        fig_pie = px.pie(
            names=["Ret Oranı", "Belge Eksikliği", "Uygunsuzluk", "Teslim Süresi"],
            values=[w_ret, w_belge, w_uyg, w_teslim], hole=0.4
        )
        fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    selected_supplier = st.selectbox("Radar Grafiği İçin Tedarikçi Seç:", analyzed_df["Tedarikçi"].unique())
    sup_data = analyzed_df[analyzed_df["Tedarikçi"] == selected_supplier].iloc[0]
    
    categories = ['Düşük Ret Başarısı', 'Belge Tamlığı', 'Kalite Uygunluğu', 'Zamanında Teslim']
    # 0-100 normalizasyonu
    values = [
        100 - min(sup_data['Ret Oranı (%)'] * 10, 100),
        100 - min(sup_data['Belge Eksikliği (%)'] * 15, 100),
        100 - min(sup_data['Uygunsuzluk Sayısı'] * 10, 100),
        100 - min(sup_data['Ortalama Teslim Gecikmesi (Gün)'] * 15, 100)
    ]
    
    fig_radar = go.Figure(data=go.Scatterpolar(
        r=values, theta=categories, fill='toself', line_color='#FF4B4B'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False, height=350, margin=dict(l=40, r=40, t=20, b=20)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# Tablo ve Çıktı
st.subheader("📋 Detaylı Analiz & Karar Tablosu")
display_df = analyzed_df.sort_values(by="Performans Skoru", ascending=False)
st.dataframe(display_df, use_container_width=True)

excel_out = io.BytesIO()
with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
    display_df.to_excel(writer, index=False, sheet_name='Analiz')

st.download_button(
    label="📥 Tam Analiz Raporunu Excel İndir",
    data=excel_out.getvalue(),
    file_name="Tedarikci_Analiz_Raporu.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
