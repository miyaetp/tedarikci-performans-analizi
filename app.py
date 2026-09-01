import io
import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. Sayfa Yapılandırması
st.set_page_config(
    page_title="Tedarikçi Analiz Sistemi | miyaetp",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TÜM STREAMLIT & GITHUB REKLAMLARINI VE MENÜLERİNİ GİZLEME ---
hide_streamlit_elements = """
    <style>
    #MainMenu {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    footer {visibility: hidden; display: none !important;}
    .viewerBadge_container__1QSob,
    .viewerBadge_link__1S137,
    [data-testid="stStatusWidget"],
    [data-testid="stToolbar"],
    [data-testid="manage-app-button"] {
        visibility: hidden !important;
        display: none !important;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
"""
st.markdown(hide_streamlit_elements, unsafe_allow_html=True)

# --- 2. GÜVENLİK VE GİRİŞ EKRANI (AUTHENTICATION) ---
SISTEM_SIFRESI = "miya123"

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
                <p style='color: gray; font-size: 14px;'>Tedarikçi Performans ve Stratejik Karar Destek Platformu</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.text_input("Giriş Şifresi:", type="password", key="password_input", on_change=check_password)
        st.button("Giriş Yap", on_click=check_password, use_container_width=True)
        st.caption("⚡ Developed by **miyaetp**")
    st.stop()

# --- 3. VERİ YÖNETİMİ ---
@st.cache_data
def get_sample_data():
    return pd.DataFrame({
        "Tedarikçi": ["Tedarikçi A", "Tedarikçi B", "Tedarikçi C", "Tedarikçi D", "Tedarikçi E", "Tedarikçi F"],
        "Kategori": ["Hammadde", "Ambalaj", "Hammadde", "Yedek Parça", "Lojistik", "Ambalaj"],
        "Yıllık Harcama (Bin TL)": [4500, 1200, 7800, 850, 3200, 1950],
        "Ret Oranı (%)": [1.2, 2.4, 3.5, 5.0, 8.2, 2.1],
        "Belge Eksikliği (%)": [0.5, 1.8, 2.2, 4.0, 6.5, 1.2],
        "Uygunsuzluk Sayısı": [1, 2, 4, 6, 9, 2],
        "Ortalama Teslim Gecikmesi (Gün)": [1.1, 2.6, 3.2, 4.5, 6.0, 1.8]
    })

# --- SOL MENÜ (SIDEBAR) ---
if st.sidebar.button("🚪 Güvenli Çıkış Yap"):
    st.session_state["authenticated"] = False
    st.rerun()

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

if data_source == "Excel/CSV Yükle":
    uploaded_file = st.sidebar.file_uploader("Excel veya CSV Seç", type=["xlsx", "csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    else:
        st.info("Lütfen bir veri dosyası yükleyin veya sol menüden örnek veriye geçin.")
        st.stop()
else:
    df = get_sample_data()

# Kategori Filtresi
if "Kategori" in df.columns:
    categories_list = ["Tümü"] + list(df["Kategori"].unique())
    selected_cat = st.sidebar.selectbox("🏷️ Kategori Filtresi:", categories_list)
    if selected_cat != "Tümü":
        df = df[df["Kategori"] == selected_cat].reset_index(drop=True)

# Örnek Şablon İndirme Butonu
template_io = io.BytesIO()
with pd.ExcelWriter(template_io, engine='openpyxl') as writer:
    get_sample_data().to_excel(writer, index=False, sheet_name='Sablon')

st.sidebar.download_button(
    label="📄 Örnek Excel Şablonunu İndir",
    data=template_io.getvalue(),
    file_name="Tedarikci_Sablonu.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# İmza
st.sidebar.divider()
st.sidebar.markdown(
    """
    <div style='background-color: rgba(128, 128, 128, 0.1); padding: 12px; border-radius: 8px; text-align: center;'>
        <p style='margin: 0; font-size: 13px; font-weight: bold;'>Developed by</p>
        <p style='margin: 0; font-size: 18px; color: #FF4B4B; font-weight: 800;'>⚡ miyaetp</p>
        <p style='margin: 0; font-size: 11px; opacity: 0.7;'>v2.0.0 • Enterprise Suite</p>
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
    if row["Ret Oranı (%)"] >= 4.0: reasons.append("Yüksek ret")
    if row["Ortalama Teslim Gecikmesi (Gün)"] >= 3.5: reasons.append("Gecikme")
    if row["Uygunsuzluk Sayısı"] >= 5: reasons.append("Sık uygunsuzluk")
    if row["Belge Eksikliği (%)"] >= 3.0: reasons.append("Belge eksikliği")

    if row["Performans Skoru"] >= 85:
        return "🟢 Onaylı: Hacim artırılabilir, öncelikli tercih."
    elif row["Performans Skoru"] >= 65:
        detail = ", ".join(reasons) if reasons else "Dalgalı performans"
        return f"🟡 İzleme: {detail} nedeniyle takip edilmeli."
    else:
        detail = ", ".join(reasons) if reasons else "Limitler aşıldı"
        return f"🔴 Riskli: {detail}. Acil DÖF açılmalı!"

analyzed_df["YZ Karar Destek"] = analyzed_df.apply(generate_ai_insight, axis=1)

# ÜST BAŞLIK VE METRİKLER
st.title("📊 Kurumsal Tedarikçi Performans & Karar Destek Sistemi")
st.caption("Veri Odaklı Kalite Kontrol, Satın Alma Stratejisi ve Aksiyon Yönetimi")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ortalama Tedarikçi Skoru", f"{analyzed_df['Performans Skoru'].mean():.1f} / 100")
col2.metric("Ortalama Ret Oranı", f"%{analyzed_df['Ret Oranı (%)'].mean():.1f}")
col3.metric("Ort. Belge Eksikliği", f"%{analyzed_df['Belge Eksikliği (%)'].mean():.1f}")
col4.metric("Ort. Teslim Gecikmesi", f"{analyzed_df['Ortalama Teslim Gecikmesi (Gün)'].mean():.1f} Gün")

st.divider()

# --- TÜM SEKMELER (TABS) ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Genel Sıralama & Ağırlıklar",
    "🎯 Harcama & Risk Matrisi (Kraljic)",
    "🔮 What-If İyileştirme Simülatörü",
    "⚔️ İki Tedarikçi Kıyaslama",
    "📈 6 Aylık Trend & Karne",
    "🤖 YZ Asistanı & DÖF Mektubu"
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

# SEKME 2: KRALJIC / HARCAMA VS RISK MATRİSİ
with tab2:
    st.subheader("🎯 Harcama ve Performans Dağılım Matrisi")
    st.caption("Yüksek harcama yapılan riskli firmaları belirleyip stratejik tedarikçileri ayırın.")
    if "Yıllık Harcama (Bin TL)" in analyzed_df.columns:
        fig_scatter = px.scatter(
            analyzed_df,
            x="Performans Skoru",
            y="Yıllık Harcama (Bin TL)",
            text="Tedarikçi",
            size="Yıllık Harcama (Bin TL)",
            color="Performans Skoru",
            color_continuous_scale="RdYlGn",
            range_x=[0, 105]
        )
        fig_scatter.add_vline(x=70, line_dash="dash", line_color="gray", annotation_text="Kritik Kalite Eşiği (70)")
        fig_scatter.update_traces(textposition='top center')
        fig_scatter.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Bu matris için veri setinizde 'Yıllık Harcama (Bin TL)' sütunu bulunmalıdır.")

# SEKME 3: WHAT-IF SİMÜLATÖRÜ
with tab3:
    st.subheader("🔮 'What-If' İyileştirme & Pazarlık Simülatörü")
    st.caption("Tedarikçi performans kriterlerini iyileştirdiğinde puanının ve statüsünün nasıl değişeceğini simüle edin.")
    
    sim_supplier = st.selectbox("Simüle Edilecek Tedarikçiyi Seçin:", analyzed_df["Tedarikçi"].unique())
    sim_row = analyzed_df[analyzed_df["Tedarikçi"] == sim_supplier].iloc[0]
    
    col_w1, col_w2, col_w3, col_w4 = st.columns(4)
    new_ret = col_w1.slider("Hedef Ret Oranı (%)", 0.0, 10.0, float(sim_row["Ret Oranı (%)"]), 0.1)
    new_belge = col_w2.slider("Hedef Belge Eksikliği (%)", 0.0, 10.0, float(sim_row["Belge Eksikliği (%)"]), 0.1)
    new_uyg = col_w3.slider("Hedef Uygunsuzluk Sayısı", 0, 15, int(sim_row["Uygunsuzluk Sayısı"]), 1)
    new_teslim = col_w4.slider("Hedef Gecikme (Gün)", 0.0, 10.0, float(sim_row["Ortalama Teslim Gecikmesi (Gün)"]), 0.1)
    
    # Simülasyon Hesaplama
    sim_df = analyzed_df.copy()
    sim_df.loc[sim_df["Tedarikçi"] == sim_supplier, "Ret Oranı (%)"] = new_ret
    sim_df.loc[sim_df["Tedarikçi"] == sim_supplier, "Belge Eksikliği (%)"] = new_belge
    sim_df.loc[sim_df["Tedarikçi"] == sim_supplier, "Uygunsuzluk Sayısı"] = new_uyg
    sim_df.loc[sim_df["Tedarikçi"] == sim_supplier, "Ortalama Teslim Gecikmesi (Gün)"] = new_teslim
    
    recalc_df = calculate_scores(sim_df)
    new_score = recalc_df[recalc_df["Tedarikçi"] == sim_supplier]["Performans Skoru"].iloc[0]
    old_score = sim_row["Performans Skoru"]
    delta_score = round(new_score - old_score, 1)
    
    st.markdown("#### Simülasyon Sonucu:")
    col_res_a, col_res_b = st.columns(2)
    col_res_a.metric("Mevcut Skor", f"{old_score} / 100")
    col_res_b.metric("Simüle Edilen Yeni Skor", f"{new_score} / 100", delta=f"{delta_score} Puan Değişimi")

# SEKME 4: İKİ TEDARİKÇİ KIYASLAMA
with tab4:
    st.subheader("⚔️ Birebir Yetkinlik Kıyaslaması (Head-to-Head)")
    supplier_list = list(analyzed_df["Tedarikçi"].unique())
    col_s1, col_s2 = st.columns(2)
    with col_s1: s1 = st.selectbox("1. Tedarikçi:", supplier_list, index=0)
    with col_s2: s2 = st.selectbox("2. Tedarikçi:", supplier_list, index=min(1, len(supplier_list)-1))

    if s1 and s2:
        row1 = analyzed_df[analyzed_df["Tedarikçi"] == s1].iloc[0]
        row2 = analyzed_df[analyzed_df["Tedarikçi"] == s2].iloc[0]

        categories = ['Düşük Ret Oranı', 'Belge Eksiksizliği', 'Kalite Uygunluğu', 'Zamanında Teslim']
        val1 = [max(0, 100 - row1['Ret Oranı (%)'] * 10), max(0, 100 - row1['Belge Eksikliği (%)'] * 15), max(0, 100 - row1['Uygunsuzluk Sayısı'] * 10), max(0, 100 - row1['Ortalama Teslim Gecikmesi (Gün)'] * 15)]
        val2 = [max(0, 100 - row2['Ret Oranı (%)'] * 10), max(0, 100 - row2['Belge Eksikliği (%)'] * 15), max(0, 100 - row2['Uygunsuzluk Sayısı'] * 10), max(0, 100 - row2['Ortalama Teslim Gecikmesi (Gün)'] * 15)]

        fig_compare = go.Figure()
        fig_compare.add_trace(go.Scatterpolar(r=val1, theta=categories, fill='toself', name=s1, line=dict(color='#00CC96')))
        fig_compare.add_trace(go.Scatterpolar(r=val2, theta=categories, fill='toself', name=s2, line=dict(color='#EF553B')))
        fig_compare.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=360, margin=dict(l=40, r=40, t=30, b=30))
        st.plotly_chart(fig_compare, use_container_width=True)

# SEKME 5: 6 AYLIK TREND ANALİZİ
with tab5:
    st.subheader("📈 Tedarikçi 6 Aylık Performans Trendi")
    trend_supplier = st.selectbox("Trend İncelemesi İçin Tedarikçi:", supplier_list)
    
    months = ["Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos"]
    base_score = analyzed_df[analyzed_df["Tedarikçi"] == trend_supplier]["Performans Skoru"].iloc[0]
    np.random.seed(abs(hash(trend_supplier)) % 10000)
    fluctuation = np.random.uniform(-8, 8, size=5)
    monthly_scores = [np.clip(base_score + f, 30, 100) for f in fluctuation] + [base_score]
    
    trend_df = pd.DataFrame({"Ay": months, "Performans Skoru": monthly_scores})
    fig_trend = px.line(trend_df, x="Ay", y="Performans Skoru", markers=True, range_y=[0, 105], title=f"{trend_supplier} - 6 Aylık Kalite Skoru Gelişimi")
    fig_trend.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_trend, use_container_width=True)

# SEKME 6: YZ ASİSTANI & DÖF MEKTUBU
with tab6:
    col_bot, col_dof = st.columns([1, 1])
    with col_bot:
        st.subheader("🤖 Doğal Dil Tedarikçi Asistanı")
        st.caption("Sistemdeki verileri analiz etmek için soru sorun.")
        user_query = st.text_input("Örn: En çok geciken firma hangisi? / En iyi tedarikçi kim?", key="bot_input")
        if user_query:
            q = user_query.lower()
            if "en iyi" in q or "lider" in q or "başarılı" in q:
                best = analyzed_df.sort_values(by="Performans Skoru", ascending=False).iloc[0]
                st.success(f"🏆 En başarılı firma: **{best['Tedarikçi']}** (Skor: {best['Performans Skoru']}/100)")
            elif "gecikme" in q or "geç" in q or "teslim" in q:
                worst_delay = analyzed_df.sort_values(by="Ortalama Teslim Gecikmesi (Gün)", ascending=False).iloc[0]
                st.warning(f"⏳ En çok geciken firma: **{worst_delay['Tedarikçi']}** ({worst_delay['Ortalama Teslim Gecikmesi (Gün)']} gün ortalama gecikme)")
            elif "ret" in q or "kalitesiz" in q or "bozuk" in q:
                worst_ret = analyzed_df.sort_values(by="Ret Oranı (%)", ascending=False).iloc[0]
                st.error(f"⚠️ En yüksek ret oranına sahip firma: **{worst_ret['Tedarikçi']}** (%{worst_ret['Ret Oranı (%)']} ret)")
            elif "risk" in q or "döf" in q:
                risky = analyzed_df[analyzed_df["Performans Skoru"] < 65]
                if len(risky) > 0:
                    st.error(f"🚨 Riskli firmalar: {', '.join(risky['Tedarikçi'].tolist())}")
                else:
                    st.success("Tüm firmalar güvenli eşiklerin üzerinde!")
            else:
                st.info("💡 Asistan ipucu: 'En iyi firma', 'en çok geciken', 'en yüksek ret oranı' veya 'riskli firmalar' şeklinde sorabilirsiniz.")
                
    with col_dof:
        st.subheader("📄 Resmi DÖF / İhtar Mektubu")
        selected_for_dof = st.selectbox("İhtar/DÖF Hazırlanacak Firma:", supplier_list, key="dof_select")
        dof_row = analyzed_df[analyzed_df["Tedarikçi"] == selected_for_dof].iloc[0]
        today_str = datetime.date.today().strftime("%d.%m.%Y")
        letter_text = f"SAYIN {selected_for_dof.upper()} YETKİLİSİ,\nTarih: {today_str}\nKonu: Kalite İyileştirme ve DÖF Talebi\n\nPerformans skoru 100 üzerinden {dof_row['Performans Skoru']} olarak tespit edilmiştir.\n- Ret Oranı: %{dof_row['Ret Oranı (%)']}\n- Belge Eksikliği: %{dof_row['Belge Eksikliği (%)']}\n- Uygunsuzluk: {int(dof_row['Uygunsuzluk Sayısı'])} Adet\n- Ortalama Gecikme: {dof_row['Ortalama Teslim Gecikmesi (Gün)']} Gün\n\n5 iş günü içinde DÖF planı talep edilmektedir.\n\nKalite Güvence Yönetimi | miyaetp Decision AI"
        st.text_area("Taslak:", letter_text, height=160)
        st.download_button("📥 DÖF İndir (.txt)", letter_text, file_name=f"DOF_{selected_for_dof}.txt", mime="text/plain")

st.divider()

# --- TABLO VE DIŞA AKTARMA ---
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
