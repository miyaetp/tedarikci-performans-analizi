import io
import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa Yapılandırması
st.set_page_config(page_title="Tedarikçi Performans Analizi", layout="wide")

st.title("📊 Yapay Zekâ Destekli Tedarikçi Performans Dashboard'u")
st.caption("Veri Destekli Satın Alma ve Kalite Değerlendirme Sistemi")

# 1. Kenar Çubuğu: Dinamik Ağırlıklar ve Veri Yönetimi
st.sidebar.header("⚙️ Değerlendirme Ağırlıkları (%)")
w_ret = st.sidebar.slider("Ret Oranı Ağırlığı", 0, 100, 30, step=5)
w_belge = st.sidebar.slider("Belge Eksikliği Ağırlığı", 0, 100, 25, step=5)
w_uyg = st.sidebar.slider("Uygunsuzluk Ağırlığı", 0, 100, 25, step=5)
w_teslim = st.sidebar.slider("Teslim Süresi Ağırlığı", 0, 100, 20, step=5)

total_weight = w_ret + w_belge + w_uyg + w_teslim
if total_weight != 100:
    st.sidebar.warning(f"Toplam ağırlık %{total_weight}. Puanlama için otomatik %100'e normalize edilecektir.")
    norm_factor = 100 / total_weight if total_weight > 0 else 1
else:
    norm_factor = 1

st.sidebar.divider()
st.sidebar.header("📁 Veri Kaynağı")
data_source = st.sidebar.radio("Kaynak Seçin:", ["Örnek ERP Verisi Kullan", "Excel/CSV Yükle"])

# 2. Veri Yükleme
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
    uploaded_file = st.sidebar.file_uploader("Dosya Seç", type=["xlsx", "csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    else:
        st.info("Lütfen bir dosya yükleyin veya örnek veriyi kullanın.")
        st.stop()
else:
    df = get_sample_data()

# 3. Puanlama Motoru
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

# 4. Yapay Zekâ / Kural Tabanlı Aksiyon Motoru
def generate_ai_insight(row):
    reasons = []
    if row["Ret Oranı (%)"] >= 4.0:
        reasons.append("Yüksek ret oranı")
    if row["Ortalama Teslim Gecikmesi (Gün)"] >= 3.5:
        reasons.append("Teslim gecikmesi")
    if row["Uygunsuzluk Sayısı"] >= 5:
        reasons.append("Sık kalite uygunsuzluğu")
    if row["Belge Eksikliği (%)"] >= 3.0:
        reasons.append("Belge eksikliği")

    if row["Performans Skoru"] >= 85:
        return "🟢 Onaylı Tedarikçi: Satın alma hacmi artırılabilir, öncelikli tercih edilmeli."
    elif row["Performans Skoru"] >= 65:
        detail = ", ".join(reasons) if reasons else "Belirli parametrelerde dalgalanma"
        return f"🟡 İzleme Listesi: {detail} nedeniyle performans takibi yapılmalı."
    else:
        detail = ", ".join(reasons) if reasons else "Kritik kalite limitleri aşıldı"
        return f"🔴 Riskli / Aksiyon Gerekli: {detail}. Düzeltici faaliyet (DÖF) talep edilmeli veya alternatif tedarikçiye geçilmeli."

analyzed_df["YZ Karar Destek & Öneri"] = analyzed_df.apply(generate_ai_insight, axis=1)

# 5. KPI Metrik Kartları
col1, col2, col3, col4 = st.columns(4)
col1.metric("Genel Performans Ort.", f"{analyzed_df['Performans Skoru'].mean():.1f} / 100")
col2.metric("Ort. Ret Oranı", f"%{analyzed_df['Ret Oranı (%)'].mean():.1f}")
col3.metric("Ort. Belge Eksikliği", f"%{analyzed_df['Belge Eksikliği (%)'].mean():.1f}")
col4.metric("Ort. Teslim Süresi", f"{analyzed_df['Ortalama Teslim Gecikmesi (Gün)'].mean():.1f} gün")

st.divider()

# 6. Grafikler ve Kriter Dağılımı
left_col, right_col = st.columns([3, 2])

with left_col:
    st.subheader("Tedarikçi Puanları")
    sorted_df = analyzed_df.sort_values(by="Performans Skoru", ascending=True)
    fig = px.bar(
        sorted_df,
        x="Performans Skoru",
        y="Tedarikçi",
        orientation="h",
        text="Performans Skoru",
        color="Performans Skoru",
        color_continuous_scale="Blues",
        range_x=[0, 100]
    )
    fig.update_layout(showlegend=False, height=350, margin=dict(l=0, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader("Aktif Kriter Dağılımı")
    fig_pie = px.pie(
        names=["Ret Oranı", "Belge Eksikliği", "Uygunsuzluk", "Teslim Süresi"],
        values=[w_ret, w_belge, w_uyg, w_teslim],
        hole=0.4
    )
    fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# 7. Detaylı Tablo ve Excel Rapor İndirme
st.subheader("📋 Tedarikçi Değerlendirme & Satın Alma Karar Tablosu")

display_df = analyzed_df.sort_values(by="Performans Skoru", ascending=False)
st.dataframe(display_df, use_container_width=True)

# Excel Çıktısı Hazırlama
output = io.BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    display_df.to_excel(writer, index=False, sheet_name='Performans_Analizi')
excel_data = output.getvalue()

st.download_button(
    label="📥 Analiz Raporunu Excel Olarak İndir",
    data=excel_data,
    file_name="Tedarikci_Performans_Raporu.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
