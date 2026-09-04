import io
import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. Sayfa Yapılandırması (Sol Menü Daima Açık Başlar)
st.set_page_config(
    page_title="Kalite & Numune Yönetim Sistemi | miyaetp",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SOL MENÜ AÇMA BUTONUNU EKRANA ÇAKAN VE ASLA KAYBETMEYEN CSS ---
sidebar_fix_css = """
    <style>
    /* Reklam ve gereksiz Streamlit öğelerini gizle */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .viewerBadge_container__1QSob,
    .viewerBadge_link__1S137,
    [data-testid="stStatusWidget"],
    [data-testid="manage-app-button"] {
        display: none !important;
    }

    /* Header'ı yok etme, şeffaf yap ki sol menü açma oku yok olmasın! */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 10000 !important;
    }

    /* Sol menü açma okunu ekranda parlayan kırmızı şık bir butona çevir */
    [data-testid="stSidebarCollapseButton"], 
    button[data-testid="baseButton-headerNoPadding"],
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: flex !important;
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        z-index: 999999 !important;
        background: #FF4B4B !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.7) !important;
        width: 38px !important;
        height: 38px !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
    }
    
    [data-testid="stSidebarCollapseButton"] svg, 
    [data-testid="collapsedControl"] svg {
        fill: white !important;
        stroke: white !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
"""
st.markdown(sidebar_fix_css, unsafe_allow_html=True)

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
                <p style='color: gray; font-size: 14px;'>Tedarikçi Kalite & Dijital Numune Yönetim Paneli</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.text_input("Giriş Şifresi:", type="password", key="password_input", on_change=check_password)
        st.button("Giriş Yap", on_click=check_password, use_container_width=True)
        st.caption("⚡ Developed by **miyaetp**")
    st.stop()

# --- 3. FABRİKA KALİTE NUMUNE ŞABLON YAPISI (15 SÜTUN) ---
KALITE_KOLONLARI = [
    "HAMMADDE ADI",
    "FİRMA İSMİ",
    "LOT NO",
    "TARİH",
    "SERTİFİKA KONTROLÜ / ANALİZ YAPAN",
    "AMBALAJ TEMİZLİĞİ",
    "ETİKET UYGUNLUK",
    "KABUL - RED",
    "MENŞEİ (ÜRETİM YERİ)",
    "RUBY ANALİZ DURUMU",
    "COA",
    "RUBY TDS",
    "RUBY SDS",
    "ORJİN (KAYNAK)",
    "DOĞAL / REACH NO"
]

if "numuneler" not in st.session_state:
    st.session_state["numuneler"] = pd.DataFrame([
        {
            "HAMMADDE ADI": "Oud Wood Esans",
            "FİRMA İSMİ": "Grasse Fragrance Ltd.",
            "LOT NO": "LOT-2026-088",
            "TARİH": "2026-08-28",
            "SERTİFİKA KONTROLÜ / ANALİZ YAPAN": "Uygun / Ahmet K.",
            "AMBALAJ TEMİZLİĞİ": "Temiz - Uygun",
            "ETİKET UYGUNLUK": "Uygun",
            "KABUL - RED": "KABUL",
            "MENŞEİ (ÜRETİM YERİ)": "Fransa",
            "RUBY ANALİZ DURUMU": "Tamamlandı",
            "COA": "Var",
            "RUBY TDS": "Mevcut",
            "RUBY SDS": "Mevcut",
            "ORJİN (KAYNAK)": "Sentetik/Doğal Karışım",
            "DOĞAL / REACH NO": "REACH-092831"
        },
        {
            "HAMMADDE ADI": "Kozmetik Denatüre Alkol %96",
            "FİRMA İSMİ": "Etanol Kimya Sanayi",
            "LOT NO": "LOT-2026-104",
            "TARİH": "2026-08-30",
            "SERTİFİKA KONTROLÜ / ANALİZ YAPAN": "GC-MS Testi / Mehmet A.",
            "AMBALAJ TEMİZLİĞİ": "Varil Temiz",
            "ETİKET UYGUNLUK": "Uygun",
            "KABUL - RED": "KABUL",
            "MENŞEİ (ÜRETİM YERİ)": "Türkiye",
            "RUBY ANALİZ DURUMU": "Onaylandı",
            "COA": "Var",
            "RUBY TDS": "Mevcut",
            "RUBY SDS": "Mevcut",
            "ORJİN (KAYNAK)": "Tarımsal Etanol",
            "DOĞAL / REACH NO": "REACH-883102"
        },
        {
            "HAMMADDE ADI": "100ml Lüks Cam Şişe",
            "FİRMA İSMİ": "Vetro Ambalaj A.Ş.",
            "LOT NO": "LOT-2026-310",
            "TARİH": "2026-09-01",
            "SERTİFİKA KONTROLÜ / ANALİZ YAPAN": "Sızdırmazlık / Selin Y.",
            "AMBALAJ TEMİZLİĞİ": "Koli Deforme",
            "ETİKET UYGUNLUK": "Eksik Lot Yazısı",
            "KABUL - RED": "RED",
            "MENŞEİ (ÜRETİM YERİ)": "İtalya",
            "RUBY ANALİZ DURUMU": "Kaçak Tespit Edildi",
            "COA": "Yok",
            "RUBY TDS": "Eksik",
            "RUBY SDS": "Mevcut Değil",
            "ORJİN (KAYNAK)": "Cam",
            "DOĞAL / REACH NO": "-"
        }
    ])

# --- 4. TEDARİKÇİ ERP VERİLERİ ---
@st.cache_data
def get_sample_data():
    return pd.DataFrame({
        "Tedarikçi": ["Grasse Fragrance Ltd.", "Etanol Kimya Sanayi", "Vetro Ambalaj A.Ş.", "AeroSpray Valf", "Zamak Manyetik Kapak", "Prestige Kutu"],
        "Yıllık Harcama (Bin TL)": [9500, 3800, 5200, 2100, 2800, 1650],
        "Ret Oranı (%)": [0.8, 1.5, 3.8, 4.5, 1.2, 2.0],
        "Belge Eksikliği (%)": [0.2, 0.5, 2.1, 3.2, 0.9, 1.1],
        "Uygunsuzluk Sayısı": [1, 1, 5, 6, 2, 2],
        "Ortalama Teslim Gecikmesi (Gün)": [1.0, 1.2, 3.5, 4.0, 1.8, 2.0]
    })

# --- SOL MENÜ (SIDEBAR) ---
if st.sidebar.button("🚪 Güvenli Çıkış Yap"):
    st.session_state["authenticated"] = False
    st.rerun()

st.sidebar.title("📌 Modül / Sayfa Seçimi")
secilen_sayfa = st.sidebar.radio(
    "Gitmek İstediğiniz Sayfayı Seçin:",
    ["📊 Tedarikçi Kalite & Karar Paneli", "🧪 Canlı Numune Takip Sistemi"]
)
st.sidebar.divider()

# ==============================================================================
# SAYFA 1: TEDARİKÇİ KALİTE & KARAR PANELİ
# ==============================================================================
if secilen_sayfa == "📊 Tedarikçi Kalite & Karar Paneli":
    st.sidebar.header("⚙️ Değerlendirme Ağırlıkları (%)")
    w_ret = st.sidebar.slider("Ret Oranı Ağırlığı", 0, 100, 35, step=5)
    w_belge = st.sidebar.slider("Belge / Sertifika Eksikliği Ağırlığı", 0, 100, 25, step=5)
    w_uyg = st.sidebar.slider("Uygunsuzluk Sayısı Ağırlığı", 0, 100, 25, step=5)
    w_teslim = st.sidebar.slider("Teslimat Gecikmesi Ağırlığı", 0, 100, 15, step=5)

    total_weight = w_ret + w_belge + w_uyg + w_teslim
    norm_factor = 100 / total_weight if total_weight > 0 else 1

    st.sidebar.divider()
    st.sidebar.header("📁 Veri Kaynağı")
    data_source = st.sidebar.radio("Kaynak Seçimi:", ["Örnek ERP Verisi Kullan", "Excel/CSV Yükle"])

    if data_source == "Excel/CSV Yükle":
        uploaded_file = st.sidebar.file_uploader("Tedarikçi Analiz Dosyası Seç (xlsx/csv)", type=["xlsx", "csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        else:
            st.info("Lütfen bir tedarikçi veri dosyası yükleyin.")
            st.stop()
    else:
        df = get_sample_data()

    template_io = io.BytesIO()
    with pd.ExcelWriter(template_io, engine='openpyxl') as writer:
        get_sample_data().to_excel(writer, index=False, sheet_name='Sablon')

    st.sidebar.download_button(
        label="📄 Örnek Excel Şablonunu İndir",
        data=template_io.getvalue(),
        file_name="Tedarikci_Sablonu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

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

    def generate_ai_insight(row):
        reasons = []
        if row["Ret Oranı (%)"] >= 3.0: reasons.append("Yüksek ret oranı")
        if row["Ortalama Teslim Gecikmesi (Gün)"] >= 3.0: reasons.append("Teslim gecikmesi")
        if row["Uygunsuzluk Sayısı"] >= 4: reasons.append("Sık uygunsuzluk")
        if row["Belge Eksikliği (%)"] >= 2.0: reasons.append("Belge eksikliği")

        if row["Performans Skoru"] >= 85:
            return "🟢 Onaylı Tedarikçi: Kalite kararlılığı yüksek, öncelikli tercih edilmeli."
        elif row["Performans Skoru"] >= 65:
            detail = ", ".join(reasons) if reasons else "Parametrelerde dalgalanma"
            return f"🟡 Sıkı Takip: {detail} nedeniyle performans takibi yapılmalı."
        else:
            detail = ", ".join(reasons) if reasons else "Kritik limitler aşıldı"
            return f"🔴 Riskli Tedarikçi: {detail}. Acil 8D DÖF talep edilmeli veya alternatif firma değerlendirilmeli."

    analyzed_df["YZ Karar Destek"] = analyzed_df.apply(generate_ai_insight, axis=1)

    st.title("📊 Tedarikçi Kalite & Performans Karar Sistemi")
    st.caption("Veri Odaklı Kalite Kontrol, Satın Alma Stratejisi ve Aksiyon Yönetimi")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Genel Kalite Skoru", f"{analyzed_df['Performans Skoru'].mean():.1f} / 100")
    col2.metric("Ortalama Ret Oranı", f"%{analyzed_df['Ret Oranı (%)'].mean():.1f}")
    col3.metric("Ort. Belge Eksikliği", f"%{analyzed_df['Belge Eksikliği (%)'].mean():.1f}")
    col4.metric("Ort. Teslim Gecikmesi", f"{analyzed_df['Ortalama Teslim Gecikmesi (Gün)'].mean():.1f} Gün")

    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Genel Kalite Sıralaması",
        "🎯 Harcama & Risk Matrisi",
        "🔮 What-If İyileştirme Simülatörü",
        "⚔️ İki Tedarikçi Kıyaslama",
        "📈 6 Aylık Trend & Karne",
        "📄 Resmi DÖF & İhtar Mektubu"
    ])

    with tab1:
        col_chart, col_pie = st.columns([3, 2])
        with col_chart:
            sorted_df = analyzed_df.sort_values(by="Performans Skoru", ascending=True)
            fig_bar = px.bar(
                sorted_df, x="Performans Skoru", y="Tedarikçi", orientation="h",
                text="Performans Skoru", color="Performans Skoru", color_continuous_scale="Tealgrn", range_x=[0, 100]
            )
            fig_bar.update_layout(height=350, margin=dict(l=0, r=20, t=20, b=20))
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_pie:
            fig_pie = px.pie(
                names=["Ret Oranı", "Belge/Sertifika", "Uygunsuzluk", "Teslim Süresi"],
                values=[w_ret, w_belge, w_uyg, w_teslim], hole=0.4
            )
            fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

    with tab2:
        st.subheader("🎯 Harcama ve Kalite Risk Matrisi")
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
            fig_scatter.add_vline(x=70, line_dash="dash", line_color="gray", annotation_text="Kritik Kalite Eşiği (70 Puan)")
            fig_scatter.update_traces(textposition='top center')
            fig_scatter.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_scatter, use_container_width=True)

    with tab3:
        st.subheader("🔮 'What-If' Kalite İyileştirme Simülatörü")
        sim_supplier = st.selectbox("Simüle Edilecek Tedarikçi:", analyzed_df["Tedarikçi"].unique())
        sim_row = analyzed_df[analyzed_df["Tedarikçi"] == sim_supplier].iloc[0]
        
        col_w1, col_w2, col_w3, col_w4 = st.columns(4)
        new_ret = col_w1.slider("Hedef Ret Oranı (%)", 0.0, 8.0, float(sim_row["Ret Oranı (%)"]), 0.1)
        new_belge = col_w2.slider("Hedef Belge Eksikliği (%)", 0.0, 8.0, float(sim_row["Belge Eksikliği (%)"]), 0.1)
        new_uyg = col_w3.slider("Hedef Uygunsuzluk Sayısı", 0, 10, int(sim_row["Uygunsuzluk Sayısı"]), 1)
        new_teslim = col_w4.slider("Hedef Gecikme (Gün)", 0.0, 8.0, float(sim_row["Ortalama Teslim Gecikmesi (Gün)"]), 0.1)
        
        sim_df = analyzed_df.copy()
        sim_df.loc[sim_df["Tedarikçi"] == sim_supplier, "Ret Oranı (%)"] = new_ret
        sim_df.loc[sim_df["Tedarikçi"] == sim_supplier, "Belge Eksikliği (%)"] = new_belge
        sim_df.loc[sim_df["Tedarikçi"] == sim_supplier, "Uygunsuzluk Sayısı"] = new_uyg
        sim_df.loc[sim_df["Tedarikçi"] == sim_supplier, "Ortalama Teslim Gecikmesi (Gün)"] = new_teslim
        
        recalc_df = calculate_scores(sim_df)
        new_score = recalc_df[recalc_df["Tedarikçi"] == sim_supplier]["Performans Skoru"].iloc[0]
        old_score = sim_row["Performans Skoru"]
        delta_score = round(new_score - old_score, 1)
        
        col_res_a, col_res_b = st.columns(2)
        col_res_a.metric("Mevcut Kalite Skoru", f"{old_score} / 100")
        col_res_b.metric("Simüle Edilen Yeni Skor", f"{new_score} / 100", delta=f"{delta_score} Puan Değişimi")

    with tab4:
        st.subheader("⚔️ İki Tedarikçi Birebir Kıyaslaması (Radar Analizi)")
        supplier_list = list(analyzed_df["Tedarikçi"].unique())
        col_s1, col_s2 = st.columns(2)
        with col_s1: s1 = st.selectbox("1. Tedarikçi:", supplier_list, index=0)
        with col_s2: s2 = st.selectbox("2. Tedarikçi:", supplier_list, index=min(1, len(supplier_list)-1))

        if s1 and s2:
            row1 = analyzed_df[analyzed_df["Tedarikçi"] == s1].iloc[0]
            row2 = analyzed_df[analyzed_df["Tedarikçi"] == s2].iloc[0]

            categories = ['Düşük Ret Başarısı', 'Belge/Sertifika Tamlığı', 'Kalite Uygunluğu', 'Termin Sadakati']
            val1 = [max(0, 100 - row1['Ret Oranı (%)'] * 12), max(0, 100 - row1['Belge Eksikliği (%)'] * 18), max(0, 100 - row1['Uygunsuzluk Sayısı'] * 12), max(0, 100 - row1['Ortalama Teslim Gecikmesi (Gün)'] * 15)]
            val2 = [max(0, 100 - row2['Ret Oranı (%)'] * 12), max(0, 100 - row2['Belge Eksikliği (%)'] * 18), max(0, 100 - row2['Uygunsuzluk Sayısı'] * 12), max(0, 100 - row2['Ortalama Teslim Gecikmesi (Gün)'] * 15)]

            fig_compare = go.Figure()
            fig_compare.add_trace(go.Scatterpolar(r=val1, theta=categories, fill='toself', name=s1, line=dict(color='#00CC96')))
            fig_compare.add_trace(go.Scatterpolar(r=val2, theta=categories, fill='toself', name=s2, line=dict(color='#EF553B')))
            fig_compare.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=360, margin=dict(l=40, r=40, t=30, b=30))
            st.plotly_chart(fig_compare, use_container_width=True)

    with tab5:
        st.subheader("📈 Tedarikçi 6 Aylık Kalite Trendi")
        trend_supplier = st.selectbox("Trend İncelemesi İçin Tedarikçi:", supplier_list)
        months = ["Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos"]
        base_score = analyzed_df[analyzed_df["Tedarikçi"] == trend_supplier]["Performans Skoru"].iloc[0]
        np.random.seed(abs(hash(trend_supplier)) % 10000)
        fluctuation = np.random.uniform(-6, 6, size=5)
        monthly_scores = [np.clip(base_score + f, 30, 100) for f in fluctuation] + [base_score]
        trend_df = pd.DataFrame({"Ay": months, "Performans Skoru": monthly_scores})
        fig_trend = px.line(trend_df, x="Ay", y="Performans Skoru", markers=True, range_y=[0, 105], title=f"{trend_supplier} - 6 Aylık Kalite Gelişimi")
        fig_trend.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_trend, use_container_width=True)

    with tab6:
        st.subheader("📄 Resmi Kalite DÖF / İhtar Mektubu Üretici")
        selected_for_dof = st.selectbox("İhtar Gönderilecek Firma:", supplier_list, key="dof_select")
        dof_row = analyzed_df[analyzed_df["Tedarikçi"] == selected_for_dof].iloc[0]
        today_str = datetime.date.today().strftime("%d.%m.%Y")
        
        letter_text = f"""SAYIN {selected_for_dof.upper()} KALİTE GÜVENCE MÜDÜRLÜĞÜNE,\nTarih: {today_str}\nKonu: Tedarikçi Kalite Uygunsuzluğu ve 8D DÖF Talebi\n\nGenel kalite skoru 100 üzerinden {dof_row['Performans Skoru']} olarak ölçülmüştür.\n- Ret Oranı: %{dof_row['Ret Oranı (%)']}\n- Belge/Sertifika Eksikliği: %{dof_row['Belge Eksikliği (%)']}\n- Uygunsuzluk Sayısı: {int(dof_row['Uygunsuzluk Sayısı'])} Adet\n- Gecikme: {dof_row['Ortalama Teslim Gecikmesi (Gün)']} Gün\n\n5 iş günü içinde DÖF planı talep edilmektedir.\n\nKalite Güvence Direktörlüğü | miyaetp Quality Intelligence"""
        st.text_area("Oluşturulan Mektup Metni:", letter_text, height=220)
        st.download_button("📥 DÖF Mektubunu İndir (.txt)", letter_text, file_name=f"DOF_{selected_for_dof}.txt", mime="text/plain")

    st.divider()
    st.subheader("📋 Detaylı Tedarikçi Kalite Değerlendirme Tablosu")
    display_df = analyzed_df.sort_values(by="Performans Skoru", ascending=False)
    st.dataframe(display_df, use_container_width=True)

    excel_out = io.BytesIO()
    with pd.ExcelWriter(excel_out, engine='openpyxl') as writer:
        display_df.to_excel(writer, index=False, sheet_name='Kalite_Analizi')
    st.download_button("📥 Kalite Raporunu Excel Olarak İndir", excel_out.getvalue(), "Tedarikci_Kalite_Raporu.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ==============================================================================
# SAYFA 2: CANLI NUMUNE TAKİP SİSTEMİ (15 SÜTUNLU FABRİKA FORMATI)
# ==============================================================================
else:
    st.title("🧪 Canlı Numune & Hammadde Kalite Takip Sistemi")
    st.caption("Fabrika Giriş Kalite Kontrol Şablonuna Uygun Numune Kabul, Analiz ve Kabul/Red Yönetimi")

    # --- ESNEK VE TAM EŞLEŞTİRMELİ EXCEL YÜKLEME ALANI ---
    with st.expander("📥 Kalite Kontrol Excel Listesini İçe Aktar", expanded=False):
        col_up1, col_up2 = st.columns([2, 1])
        with col_up1:
            uploaded_samples = st.file_uploader("Numune Excel Dosyası Seç (.xlsx veya .csv)", type=["xlsx", "csv"], key="numune_uploader")
            if uploaded_samples:
                try:
                    raw_df = pd.read_csv(uploaded_samples) if uploaded_samples.name.endswith(".csv") else pd.read_excel(uploaded_samples)
                    raw_df = raw_df.dropna(how='all').reset_index(drop=True)
                    
                    if len(raw_df) == 0:
                        st.warning("Yüklenen dosya boş!")
                    else:
                        processed_df = pd.DataFrame()
                        bugun = datetime.date.today().strftime("%Y-%m-%d")

                        def find_column(patterns):
                            for col in raw_df.columns:
                                col_clean = str(col).upper().replace("İ", "I").replace("I", "I").strip()
                                for p in patterns:
                                    p_clean = p.upper().replace("İ", "I").replace("I", "I").strip()
                                    if p_clean in col_clean:
                                        return col
                            return None

                        # 1. HAMMADDE ADI
                        col = find_column(["HAMMADDE", "URUN", "MALZEME", "NUMUNE ADI", "NAME"])
                        processed_df["HAMMADDE ADI"] = raw_df[col].fillna("Genel Hammadde").astype(str) if col else "Genel Hammadde"

                        # 2. FİRMA İSMİ
                        col = find_column(["FIRMA", "TEDARIK", "URETICI", "SUPPLIER", "VENDOR"])
                        processed_df["FİRMA İSMİ"] = raw_df[col].fillna("Bilinmeyen Firma").astype(str) if col else "Bilinmeyen Firma"

                        # 3. LOT NO
                        col = find_column(["LOT", "SARJ", "BATCH", "PARTI"])
                        processed_df["LOT NO"] = raw_df[col].fillna("-").astype(str) if col else "-"

                        # 4. TARİH
                        col = find_column(["TARIH", "DATE", "GIRIS", "KABUL TARIHI"])
                        processed_df["TARİH"] = raw_df[col].fillna(bugun).astype(str) if col else bugun

                        # 5. SERTİFİKA KONTROLÜ / ANALİZ YAPAN
                        col = find_column(["SERTIFIKA KONTROLU", "ANALIZ YAPAN", "SERTIFIKA", "ANALIZ"])
                        processed_df["SERTİFİKA KONTROLÜ / ANALİZ YAPAN"] = raw_df[col].fillna("-").astype(str) if col else "-"

                        # 6. AMBALAJ TEMİZLİĞİ / ORTAK ANALİZ
                        col = find_column(["AMBALAJ TEMIZLIGI", "AMBALAJ", "ORTAK ANALIZ"])
                        processed_df["AMBALAJ TEMİZLİĞİ"] = raw_df[col].fillna("-").astype(str) if col else "-"

                        # 7. ETİKET UYGUNLUK
                        col = find_column(["ETIKET", "LABEL", "ETIKET UYGUNLUK"])
                        processed_df["ETİKET UYGUNLUK"] = raw_df[col].fillna("-").astype(str) if col else "-"

                        # 8. KABUL - RED (OTOMATİK NORMALİZASYON)
                        col = find_column(["KABUL - RED", "KABUL", "RED", "DURUM", "SONUC", "KARAR", "STATUS"])
                        def parse_kabul_red(val):
                            v = str(val).upper().replace("İ", "I").strip()
                            if any(k in v for k in ["KABUL", "ONAY", "UYGUN", "PASS", "OK"]):
                                return "KABUL"
                            elif any(k in v for k in ["RED", "RET", "UYGUNSUZ", "FAIL", "NOK"]):
                                return "RED"
                            else:
                                return "BEKLİYOR"

                        processed_df["KABUL - RED"] = raw_df[col].apply(parse_kabul_red) if col else "BEKLİYOR"

                        # 9. MENŞEİ (ÜRETİM YERİ)
                        col = find_column(["MENSEI", "URETIM YERI", "ULKE", "ORIGIN"])
                        processed_df["MENŞEİ (ÜRETİM YERİ)"] = raw_df[col].fillna("-").astype(str) if col else "-"

                        # 10. RUBY ANALİZ DURUMU
                        col = find_column(["RUBY ANALIZ", "LAB DURUMU", "ANALIZ DURUMU"])
                        processed_df["RUBY ANALİZ DURUMU"] = raw_df[col].fillna("-").astype(str) if col else "-"

                        # 11. COA
                        col = find_column(["COA", "ANALIZ SERTIFIKASI"])
                        processed_df["COA"] = raw_df[col].fillna("-").astype(str) if col else "-"

                        # 12. RUBY TDS
                        col = find_column(["TDS", "RUBY TDS", "TEKNIK DOKUMAN"])
                        processed_df["RUBY TDS"] = raw_df[col].fillna("-").astype(str) if col else "-"

                        # 13. RUBY SDS
                        col = find_column(["SDS", "MSDS", "RUBY SDS", "GUVENLIK"])
                        processed_df["RUBY SDS"] = raw_df[col].fillna("-").astype(str) if col else "-"

                        # 14. ORJİN (KAYNAK)
                        col = find_column(["ORJIN", "KAYNAK", "SOURCE"])
                        processed_df["ORJİN (KAYNAK)"] = raw_df[col].fillna("-").astype(str) if col else "-"

                        # 15. DOĞAL / REACH NO
                        col = find_column(["REACH", "DOGAL", "REACH NO"])
                        processed_df["DOĞAL / REACH NO"] = raw_df[col].fillna("-").astype(str) if col else "-"

                        final_df = processed_df[KALITE_KOLONLARI]

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("🔄 Tabloyu Bu Excel İle Sıfırla & Yükle"):
                                st.session_state["numuneler"] = final_df
                                st.success(f"Başarılı! {len(final_df)} adet kayıt 15 sütunluk şablona tam oturtuldu.")
                                st.rerun()
                        with col_btn2:
                            if st.button("➕ Mevcut Listenin Altına Ekle"):
                                st.session_state["numuneler"] = pd.concat([st.session_state["numuneler"], final_df], ignore_index=True)
                                st.success(f"{len(final_df)} adet yeni satır listenin altına eklendi!")
                                st.rerun()

                except Exception as e:
                    st.error(f"Dosya işlenirken hata oluştu: {e}")

        with col_up2:
            st.markdown("**15 Sütunluk Orijinal Excel Şablonu:**")
            st.caption("Resimdeki başlıkların tam birebir şablonudur.")
            sample_template_io = io.BytesIO()
            with pd.ExcelWriter(sample_template_io, engine='openpyxl') as writer:
                st.session_state["numuneler"].to_excel(writer, index=False, sheet_name='Kalite_Takip_Sablonu')
            st.download_button(
                label="📄 Kalite Kontrol Şablonunu İndir",
                data=sample_template_io.getvalue(),
                file_name="Kalite_Kontrol_Numune_Sablonu.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    s_df = st.session_state["numuneler"]

    # Canlı Durum Metrik Kartları
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Toplam Kayıt", f"{len(s_df)} Adet")
    col_m2.metric("✅ KABUL Edilen", f"{len(s_df[s_df['KABUL - RED'] == 'KABUL'])} Adet")
    col_m3.metric("🔴 RED Edilen", f"{len(s_df[s_df['KABUL - RED'] == 'RED'])} Adet")
    col_m4.metric("⏳ BEKLİYOR", f"{len(s_df[s_df['KABUL - RED'] == 'BEKLİYOR'])} Adet")

    st.divider()

    # --- YENİ KAYIT & HIZLI KARAR GÜNCELLEME ---
    col_left, col_right = st.columns([1.1, 1.2])

    with col_left:
        st.markdown("### ➕ Manuel Numune Girişi")
        with st.form("manuel_numune_form", clear_on_submit=True):
            f_hammadde = st.text_input("Hammadde Adı:", placeholder="Örn: Bergamot Esansı")
            f_firma = st.text_input("Firma İsmi:", placeholder="Örn: Grasse Fragrance Ltd.")
            f_lot = st.text_input("Lot No:", placeholder="Örn: LOT-9941")
            f_tarih = st.date_input("Kabul Tarihi:", datetime.date.today())
            f_karar = st.selectbox("Kabul / Red Durumu:", ["BEKLİYOR", "KABUL", "RED"])
            f_analiz = st.text_input("Analiz Yapan / Not:", placeholder="Örn: Ahmet K. / Koku testi yapıldı")
            
            ekle_btn = st.form_submit_button("✅ Sisteme Kaydet")
            if ekle_btn and f_hammadde and f_firma:
                yeni_satir = pd.DataFrame([{
                    "HAMMADDE ADI": f_hammadde,
                    "FİRMA İSMİ": f_firma,
                    "LOT NO": f_lot if f_lot else "-",
                    "TARİH": f_tarih.strftime("%Y-%m-%d"),
                    "SERTİFİKA KONTROLÜ / ANALİZ YAPAN": f_analiz if f_analiz else "-",
                    "AMBALAJ TEMİZLİĞİ": "Uygun",
                    "ETİKET UYGUNLUK": "Uygun",
                    "KABUL - RED": f_karar,
                    "MENŞEİ (ÜRETİM YERİ)": "-",
                    "RUBY ANALİZ DURUMU": "-",
                    "COA": "-",
                    "RUBY TDS": "-",
                    "RUBY SDS": "-",
                    "ORJİN (KAYNAK)": "-",
                    "DOĞAL / REACH NO": "-"
                }])
                st.session_state["numuneler"] = pd.concat([yeni_satir, st.session_state["numuneler"]], ignore_index=True)
                st.success(f"{f_hammadde} ({f_karar}) olarak sisteme kaydedildi!")
                st.rerun()

    with col_right:
        st.markdown("### ⚡ Karar & Durum Güncelle")
        if len(st.session_state["numuneler"]) > 0:
            hammadde_listesi = [f"{i}: {row['HAMMADDE ADI']} ({row['FİRMA İSMİ']}) - {row['LOT NO']}" for i, row in st.session_state["numuneler"].iterrows()]
            secilen_idx_str = st.selectbox("İşlem Yapılacak Satırı Seçin:", hammadde_listesi)
            secilen_index = int(secilen_idx_str.split(":")[0])
            secili_satir = st.session_state["numuneler"].loc[secilen_index]

            st.info(f"**Hammadde:** {secili_satir['HAMMADDE ADI']} | **Firma:** {secili_satir['FİRMA İSMİ']} | **Tarih:** {secili_satir['TARİH']}")
            
            col_k1, col_k2 = st.columns(2)
            with col_k1:
                yeni_karar = st.selectbox(
                    "KABUL - RED Durumu:",
                    ["BEKLİYOR", "KABUL", "RED"],
                    index=["BEKLİYOR", "KABUL", "RED"].index(secili_satir["KABUL - RED"]) if secili_satir["KABUL - RED"] in ["BEKLİYOR", "KABUL", "RED"] else 0
                )
            with col_k2:
                yeni_analiz_durum = st.text_input("Ruby Analiz Durumu:", value=str(secili_satir["RUBY ANALİZ DURUMU"]))

            guncel_analiz_yapan = st.text_input("Analiz Yapan / Açıklama:", value=str(secili_satir["SERTİFİKA KONTROLÜ / ANALİZ YAPAN"]))

            if st.button("💾 Değişiklikleri Kaydet", use_container_width=True):
                st.session_state["numuneler"].at[secilen_index, "KABUL - RED"] = yeni_karar
                st.session_state["numuneler"].at[secilen_index, "RUBY ANALİZ DURUMU"] = yeni_analiz_durum
                st.session_state["numuneler"].at[secilen_index, "SERTİFİKA KONTROLÜ / ANALİZ YAPAN"] = guncel_analiz_yapan
                st.success("Kayıt başarıyla güncellendi!")
                st.rerun()

    st.divider()

    # --- CANLI TABLO & FİLTRELEME ALANI ---
    st.subheader("📋 Canlı Numune & Hammadde Takip Tablosu")
    
    col_f1, col_f2 = st.columns([1.5, 2])
    with col_f1:
        karar_filtresi = st.radio("Kabul/Red Filtresi:", ["Tümü", "KABUL", "RED", "BEKLİYOR"], horizontal=True)
    with col_f2:
        firma_ara = st.text_input("🔍 Firma veya Hammadde Ara:", placeholder="Örn: Grasse veya Etanol...")

    tablo_df = st.session_state["numuneler"].copy()
    if karar_filtresi != "Tümü":
        tablo_df = tablo_df[tablo_df["KABUL - RED"] == karar_filtresi]
    
    if firma_ara:
        tablo_df = tablo_df[
            tablo_df["HAMMADDE ADI"].str.contains(firma_ara, case=False, na=False) |
            tablo_df["FİRMA İSMİ"].str.contains(firma_ara, case=False, na=False) |
            tablo_df["LOT NO"].str.contains(firma_ara, case=False, na=False)
        ]

    st.dataframe(tablo_df, use_container_width=True)

    numune_out_io = io.BytesIO()
    with pd.ExcelWriter(numune_out_io, engine='openpyxl') as writer:
        st.session_state["numuneler"].to_excel(writer, index=False, sheet_name='Kalite_Kontrol_Listesi')

    st.download_button(
        label="📥 Güncel Tabloyu Fabrika Formatında Excel Olarak İndir",
        data=numune_out_io.getvalue(),
        file_name="Kalite_Kontrol_Numune_Listesi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- İMZA ALANI (SIDEBAR ALT) ---
st.sidebar.markdown(
    """
    <div style='background-color: rgba(128, 128, 128, 0.1); padding: 12px; border-radius: 8px; text-align: center; margin-top: 20px;'>
        <p style='margin: 0; font-size: 13px; font-weight: bold;'>Developed by</p>
        <p style='margin: 0; font-size: 18px; color: #FF4B4B; font-weight: 800;'>⚡ miyaetp</p>
        <p style='margin: 0; font-size: 11px; opacity: 0.7;'>v4.2.0 • Fixed Header Edition</p>
    </div>
    """,
    unsafe_allow_html=True
)
