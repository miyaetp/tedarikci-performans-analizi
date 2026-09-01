import io
import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Sayfa Yapılandırması
st.set_page_config(
    page_title="Tedarikçi Analiz Sistemi | miyaetp",
    page_icon="⚡",
    layout="wide"
)

# --- 2. GÜVENLİK VE GİRİŞ EKRANI (AUTHENTICATION) ---
SISTEM_SIFRESI = "miya123"  # İstediğin şifreyi buraya yazabilirsin

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_password():
    if st.session_state["password_input"] == SISTEM_SIFRESI:
        st.session_state["authenticated"] = True
        del st.session_state["password_input"]
    else:
        st.error("❌ Hatalı şifre girdiniz. Lütfen tekrar deneyin.")

if not st.session_state["authenticated"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        st.markdown(
            """
            <div style='background-color: rgba(128, 128, 128, 0.08); padding: 30px; border-radius: 12px; text-align: center; border: 1px solid rgba(128, 128, 128, 0.2);'>
                <h2 style='margin-bottom: 5px;'>🔒 Yetkili Girişi</h2>
                <p style='color: gray; font-size: 14px;'>Tedarikçi Performans ve Karar Destek Paneli</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.text_input("Giriş Şifresi:", type="password", key="password_input", on_change=check_password)
        st.button("Giriş Yap", on_click=check_password, use_container_width=True)
        st.caption("⚡ Developed by **miyaetp**")
    st.stop()  # Şifre doğru girilene kadar alt kısımları çalıştırma

# --- 3. ANA DASHBOARD (ŞİFRE DOĞRUYSA AÇILIR) ---

# Çıkış Yap Butonu (Sidebar)
if st.sidebar.button("🚪 Güvenli Çıkış Yap"):
    st.session_state["authenticated"] = False
    st.rerun()

st.title("📊 Yapay Zekâ Destekli Tedarikçi Performans Dashboard'u")
st.caption("Veri Destekli Satın Alma, Kalite Değerlendirme ve Aksiyon Yönetim Sistemi")

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
        <p style='margin: 0; font-size: 11px; opacity: 0.7;'>v1.4.0 • Secure AI System</p>
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

# --- SEKMELER (TABS) ---
tab1, tab2, tab3 = st.tabs([
    "📊 Genel Sıralama & Ağırlıklar",
    "⚔️ İki Tedarikçi Karşılaştırması",
    "📄 Otomatik DÖF & İhtar Mektubu"
])

# SEKME 1: GENEL SIRALAMA
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

# SEKME 2: İKİ TEDARİKÇİ KIYASLAMA
with tab2:
    st.subheader("⚔️ Birebir Yetkinlik Kıyaslaması (Head-to-Head)")
    supplier_list = list(analyzed_df["Tedarikçi"].unique())
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        s1 = st.selectbox("1. Tedarikçiyi Seçin:", supplier_list, index=0)
    with col_s2:
        s2 = st.selectbox("2. Tedarikçiyi Seçin:", supplier_list, index=min(1, len(supplier_list)-1))

    if s1 and s2:
        row1 = analyzed_df[analyzed_df["Tedarikçi"] == s1].iloc[0]
        row2 = analyzed_df[analyzed_df["Tedarikçi"] == s2].iloc[0]

        categories = ['Düşük Ret Oranı', 'Belge Eksiksizliği', 'Kalite Uygunluğu', 'Zamanında Teslim']
        
        val1 = [
            max(0, 100 - row1['Ret Oranı (%)'] * 10),
            max(0, 100 - row1['Belge Eksikliği (%)'] * 15),
            max(0, 100 - row1['Uygunsuzluk Sayısı'] * 10),
            max(0, 100 - row1['Ortalama Teslim Gecikmesi (Gün)'] * 15)
        ]
        val2 = [
            max(0, 100 - row2['Ret Oranı (%)'] * 10),
            max(0, 100 - row2['Belge Eksikliği (%)'] * 15),
            max(0, 100 - row2['Uygunsuzluk Sayısı'] * 10),
            max(0, 100 - row2['Ortalama Teslim Gecikmesi (Gün)'] * 15)
        ]

        fig_compare = go.Figure()
        fig_compare.add_trace(go.Scatterpolar(
            r=val1, theta=categories, fill='toself', name=s1, line=dict(color='#00CC96')
        ))
        fig_compare.add_trace(go.Scatterpolar(
            r=val2, theta=categories, fill='toself', name=s2, line=dict(color='#EF553B')
        ))
        fig_compare.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            height=380, margin=dict(l=40, r=40, t=30, b=30)
        )
        st.plotly_chart(fig_compare, use_container_width=True)

        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.info(f"**{s1}** — Toplam Skor: **{row1['Performans Skoru']} / 100**\n\n{row1['YZ Karar Destek']}")
        with col_res2:
            st.info(f"**{s2}** — Toplam Skor: **{row2['Performans Skoru']} / 100**\n\n{row2['YZ Karar Destek']}")

# SEKME 3: OTOMATİK DÖF VE İHTAR MEKTUBU
with tab3:
    st.subheader("📄 Düzeltici Önleyici Faaliyet (DÖF) & İhtar Mektubu Üretici")
    st.caption("Performansı hedefin altında kalan firmalara resmi kalite mektubu oluşturun.")
    
    selected_for_dof = st.selectbox("İhtar/DÖF Hazırlanacak Firma:", supplier_list)
    dof_row = analyzed_df[analyzed_df["Tedarikçi"] == selected_for_dof].iloc[0]
    
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    
    letter_text = f"""SAYIN {selected_for_dof.upper()} YETKİLİSİ,

Tarih: {today_str}
Konu: Dönemsel Tedarikçi Performans Değerlendirmesi ve Kalite İyileştirme Talebi

Kalite Güvence ve Satın Alma Departmanlarımız tarafından yapılan dönemsel performans analizleri neticesinde firmanızın genel performans skoru 100 üzerinden {dof_row['Performans Skoru']} olarak belirlenmiştir.

Değerlendirme sonucunda tespit edilen kritik kalite ve lojistik uygunsuzluklar aşağıda bilginize sunulmuştur:
- Ret Oranı: %{dof_row['Ret Oranı (%)']} (Kritik Eşik: <%2.0)
- Belge Eksikliği Oranı: %{dof_row['Belge Eksikliği (%)']} (Kritik Eşik: <%1.0)
- Kayıtlı Kalite Uygunsuzluk Sayısı: {int(dof_row['Uygunsuzluk Sayısı'])} Adet
- Ortalama Teslimat Gecikmesi: {dof_row['Ortalama Teslim Gecikmesi (Gün)']} Gün

Mevcut aksaklıkların giderilmesi, kök neden analizinin yapılması ve 8D formatında hazırlanacak Düzeltici ve Önleyici Faaliyet (DÖF) planının 5 (beş) iş günü içerisinde tarafımıza iletilmesini rica ederiz. 

Gerekli iyileştirmelerin sağlanamaması durumunda satın alma kotalarında kısıtlamaya gidilebileceğini bilgilerinize sunar, iş birliğiniz için teşekkür ederiz.

Saygılarımızla,
Kalite Güvence & Satın Alma Yönetimi
miyaetp Kalite Karar Destek Sistemi
"""
    st.text_area("Oluşturulan Resmi Bildirim Metni:", letter_text, height=280)
    
    st.download_button(
        label="📥 DÖF Mektubunu İndir (.txt)",
        data=letter_text,
        file_name=f"DOF_Talebi_{selected_for_dof}.txt",
        mime="text/plain"
    )

st.divider()

# --- TABLO VE ÇIKTI ---
st.subheader("📋 Detaylı Analiz & Karar Tablosu")
display_df = analyzed_df.sort_values(by="Performans Skoru", ascending=False)
st.dataframe(display_df, use_container_width=True)

excel_out = io.BytesIO()
with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
    display_df.to_excel(writer, index=False, sheet_name='Analiz')

st.download_button(
    label="📥 Tam Analiz Raporunu Excel Olarak İndir",
    data=excel_out.getvalue(),
    file_name="Tedarikci_Analiz_Raporu.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
