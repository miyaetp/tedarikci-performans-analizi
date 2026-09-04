import io
import datetime
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. Sayfa Yapılandırması
st.set_page_config(
    page_title="Kalite & Numune Yönetim Sistemi | miyaetp",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SOL MENÜ AÇMA BUTONUNU EKRANA ÇAKAN VE ASLA KAYBETMEYEN CSS ---
sidebar_fix_css = """
    <style>
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .viewerBadge_container__1QSob,
    .viewerBadge_link__1S137,
    [data-testid="stStatusWidget"],
    [data-testid="manage-app-button"] {
        display: none !important;
    }

    header[data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 10000 !important;
    }

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
    "DOĞAL / REACH NO",
    "SKT (SON KULLANMA)",
    "IFRA UYGUNLUK"
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
            "DOĞAL / REACH NO": "REACH-092831",
            "SKT (SON KULLANMA)": "2027-08-28",
            "IFRA UYGUNLUK": "IFRA 51 - Onaylı (%12 Kat. 4)"
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
            "DOĞAL / REACH NO": "REACH-883102",
            "SKT (SON KULLANMA)": "2028-08-30",
            "IFRA UYGUNLUK": "Muaf (Çözücü)"
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
            "DOĞAL / REACH NO": "-",
            "SKT (SON KULLANMA)": "2030-01-01",
            "IFRA UYGUNLUK": "Muaf (Ambalaj)"
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
    [
        "📊 Tedarikçi Kalite & Karar Paneli",
        "🧪 Canlı Numune & Hammadde Takip",
        "🔬 Parfüm Laboratuvar Doğrulama (IFRA/Fizikokimya)",
        "🏷️ Depo Etiket Basıcı & Lot Pasaportu"
    ]
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

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Genel Kalite Sıralaması",
        "🎯 Harcama & Risk Matrisi",
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

    with tab4:
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

    with tab5:
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

# ==============================================================================
# SAYFA 2: CANLI NUMUNE & HAMMADDE TAKİP SİSTEMİ (SKT & ALARM DESTEKLİ)
# ==============================================================================
elif secilen_sayfa == "🧪 Canlı Numune & Hammadde Takip":
    st.title("🧪 Canlı Numune & Hammadde Kalite Takip Sistemi")
    st.caption("15+ Sütunlu Fabrika Formatı, Raf Ömrü (SKT) Alarmları ve Arşiv Yönetimi")

    s_df = st.session_state["numuneler"].copy()

    # SKT & Raf Ömrü Kontrolü (Alarm Motoru)
    today = datetime.date.today()
    expiring_soon = []
    for idx, r in s_df.iterrows():
        try:
            skt_date = datetime.datetime.strptime(str(r.get("SKT (SON KULLANMA)", "")).strip(), "%Y-%m-%d").date()
            diff_days = (skt_date - today).days
            if diff_days < 0:
                expiring_soon.append(f"🔴 **{r['HAMMADDE ADI']} ({r['LOT NO']})** süresi geçmiş! ({abs(diff_days)} gün önce doldu)")
            elif diff_days <= 60:
                expiring_soon.append(f"🟡 **{r['HAMMADDE ADI']} ({r['LOT NO']})** SKT yaklaşıyor: {diff_days} gün kaldı.")
        except:
            pass

    if expiring_soon:
        with st.expander("⚠️ DİKKAT: Raf Ömrü & Re-Test Alarmları", expanded=True):
            for alert in expiring_soon:
                st.markdown(alert)

    # Durum Metrikleri
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Toplam Kayıt", f"{len(s_df)} Adet")
    col_m2.metric("✅ KABUL Edilen", f"{len(s_df[s_df['KABUL - RED'] == 'KABUL'])} Adet")
    col_m3.metric("🔴 RED Edilen", f"{len(s_df[s_df['KABUL - RED'] == 'RED'])} Adet")
    col_m4.metric("⏳ BEKLİYOR", f"{len(s_df[s_df['KABUL - RED'] == 'BEKLİYOR'])} Adet")

    st.divider()

    # Dosya Yükleme & Excel İçe Aktarma
    with st.expander("📥 Kalite Kontrol Excel Listesini İçe Aktar", expanded=False):
        uploaded_samples = st.file_uploader("Numune Excel Dosyası Seç (.xlsx veya .csv)", type=["xlsx", "csv"], key="numune_uploader")
        if uploaded_samples:
            try:
                raw_df = pd.read_csv(uploaded_samples) if uploaded_samples.name.endswith(".csv") else pd.read_excel(uploaded_samples)
                raw_df = raw_df.dropna(how='all').reset_index(drop=True)
                if len(raw_df) > 0:
                    st.session_state["numuneler"] = raw_df
                    st.success("Veriler başarıyla yüklendi!")
                    st.rerun()
            except Exception as e:
                st.error(f"Hata: {e}")

    # Canlı Tablo ve Filtreleme
    st.subheader("📋 Canlı Numune & Hammadde Takip Tablosu")
    col_f1, col_f2 = st.columns([1.5, 2])
    with col_f1:
        karar_filtresi = st.radio("Kabul/Red Filtresi:", ["Tümü", "KABUL", "RED", "BEKLİYOR"], horizontal=True)
    with col_f2:
        firma_ara = st.text_input("🔍 Firma, Lot No veya Hammadde Ara:", placeholder="Örn: Grasse veya LOT-2026...")

    tablo_df = s_df.copy()
    if karar_filtresi != "Tümü":
        tablo_df = tablo_df[tablo_df["KABUL - RED"] == karar_filtresi]
    if firma_ara:
        tablo_df = tablo_df[
            tablo_df["HAMMADDE ADI"].astype(str).str.contains(firma_ara, case=False, na=False) |
            tablo_df["FİRMA İSMİ"].astype(str).str.contains(firma_ara, case=False, na=False) |
            tablo_df["LOT NO"].astype(str).str.contains(firma_ara, case=False, na=False)
        ]

    st.dataframe(tablo_df, use_container_width=True)

    numune_out_io = io.BytesIO()
    with pd.ExcelWriter(numune_out_io, engine='openpyxl') as writer:
        s_df.to_excel(writer, index=False, sheet_name='Kalite_Kontrol_Listesi')

    st.download_button(
        label="📥 Güncel Tabloyu Excel Olarak İndir",
        data=numune_out_io.getvalue(),
        file_name="Kalite_Kontrol_Numune_Listesi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==============================================================================
# SAYFA 3: PARFÜM LABORATUVAR DOĞRULAMA (IFRA / FİZİKOKİMYA)
# ==============================================================================
elif secilen_sayfa == "🔬 Parfüm Laboratuvar Doğrulama (IFRA/Fizikokimya)":
    st.title("🔬 Parfüm & Kozmetik Kalite Doğrulama Motoru")
    st.caption("Fizikokimyasal Analizler (Dansite, Refraktometre, Alkolmetre), Organoleptik Testler ve IFRA Uygunluğu")

    st.markdown("### 🧪 Yeni Giriş Testi & Standart Uygunluk Kontrolü")
    
    with st.form("parfum_dogrulama_form"):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            test_urun_tipi = st.selectbox("Hammadde Türü:", ["Esans / Parfüm Yağı", "Kozmetik Alkol (%96)", "Solvent / Taşıyıcı"])
            test_hammadde = st.text_input("Hammadde Adı & Lot No:", placeholder="Örn: Rose & Amber Esansı - LOT-881")
            test_koku = st.selectbox("Organoleptik (Koku Profili):", ["Standart Numune ile Birebir Uyumlu", "Hafif Nüans Farkı Var (Kabul Edilebilir)", "Belirgin Yabancı Koku / Okside (Ret)"])
            test_renk = st.selectbox("Görünüm ve Renk:", ["Berrak / Tortusuz", "Bulanık / Tortulu (Ret)"])
        
        with col_t2:
            st.markdown("**Fizikokimyasal Cihaz Ölçümleri:**")
            if test_urun_tipi == "Esans / Parfüm Yağı":
                refraksiyon = st.number_input("Kırılma İndisi (Refraktometre 20°C):", min_value=1.300, max_value=1.600, value=1.492, step=0.001, format="%.3f")
                dansite = st.number_input("Bağıl Dansite / Yoğunluk (d20/20):", min_value=0.700, max_value=1.300, value=0.985, step=0.001, format="%.3f")
                alkol_derece = 0.0
            else:
                alkol_derece = st.number_input("Alkolmetre Derecesi (% Vol 20°C):", min_value=80.0, max_value=100.0, value=96.4, step=0.1)
                refraksiyon = 1.360
                dansite = 0.805

        st.markdown("---")
        st.markdown("**📋 IFRA & Mevzuat Doküman Doğrulaması:**")
        col_doc1, col_doc2, col_doc3 = st.columns(3)
        with col_doc1:
            ifra_var = st.checkbox("IFRA 51. Amendment Uygunluk Belgesi Mevcut mu?", value=True)
        with col_doc2:
            coa_var = st.checkbox("Analiz Sertifikası (CoA) İmzalı Mevcut mu?", value=True)
        with col_doc3:
            reach_var = st.checkbox("REACH Kaydı / Güvenlik Bilgi Formu (SDS) Uygun mu?", value=True)

        dogrula_btn = st.form_submit_button("⚡ Kalite Uygunluğunu Değerlendir")

    if dogrula_btn:
        st.markdown("### 📊 Otomatik Kalite Değerlendirme Raporu")
        hatalar = []

        if test_urun_tipi == "Esans / Parfüm Yağı":
            if not (1.450 <= refraksiyon <= 1.520):
                hatalar.append(f"Kırılma indisi ({refraksiyon}) referans tolerans (1.450 - 1.520) dışındadır!")
            if not (0.850 <= dansite <= 1.080):
                hatalar.append(f"Dansite değeri ({dansite}) referans aralık (0.850 - 1.080) dışındadır!")
        elif test_urun_tipi == "Kozmetik Alkol (%96)":
            if alkol_derece < 96.0:
                hatalar.append(f"Alkol derecesi (%{alkol_derece}) kozmetik standart limitin (%96.0) altındadır!")

        if "Ret" in test_koku:
            hatalar.append("Organoleptik test: Koku profilinde yabancı solvent veya oksidasyon sapması!")
        if "Bulanık" in test_renk:
            hatalar.append("Fiziksel kontrol: Üründe çökelti veya tortu tespit edildi!")
        if not ifra_var:
            hatalar.append("Mevzuat: IFRA 51 sertifikası eksik; üretime verilemez!")
        if not coa_var:
            hatalar.append("Belge: Tedarikçi CoA analiz sertifikası bulunamadı!")

        if not hatalar:
            st.success("🟢 **SONUÇ: TAM KALİTE ONAYI (KABUL)** — Tüm fizikokimyasal parametreler, organoleptik testler ve IFRA mevzuat belgeleri eksiksiz.")
            st.balloons()
        else:
            st.error("🔴 **SONUÇ: UYGUNSUZLUK TESPİT EDİLDİ (RED / BLOKE)**")
            for h in hatalar:
                st.write(f"- ❌ {h}")

# ==============================================================================
# SAYFA 4: DEPO ETİKET BASICI & LOT PASAPORTU
# ==============================================================================
elif secilen_sayfa == "🏷️ Depo Etiket Basıcı & Lot Pasaportu":
    st.title("🏷️ Depo Giriş Etiketi & Akıllı Lot Pasaportu")
    st.caption("Palet/Varil Termal Etiket Çıktıları ve Geriye Dönük Ürün İzlenebilirlik Kartı")

    s_df = st.session_state["numuneler"]

    if len(s_df) > 0:
        secilen_lot = st.selectbox("İncelemek / Etiket Basmak İstediğiniz Lotu Seçin:", s_df["LOT NO"].unique())
        lot_data = s_df[s_df["LOT NO"] == secilen_lot].iloc[0]

        col_p1, col_p2 = st.columns([1.2, 1])

        # LOT PASAPORTU KARTI
        with col_p1:
            st.markdown("### 📋 Dijital Lot Pasaportu (Kimlik Kartı)")
            karar_renk = "#00b894" if lot_data["KABUL - RED"] == "KABUL" else ("#d63031" if lot_data["KABUL - RED"] == "RED" else "#fdcb6e")
            
            st.markdown(
                f"""
                <div style='background: rgba(128,128,128,0.08); border-left: 6px solid {karar_renk}; padding: 20px; border-radius: 8px;'>
                    <h2 style='margin:0 0 5px 0;'>{lot_data['HAMMADDE ADI']}</h2>
                    <p style='color: gray; margin: 0;'>Parti / Lot: <b>{lot_data['LOT NO']}</b> | Üretici: <b>{lot_data['FİRMA İSMİ']}</b></p>
                    <hr style='margin: 12px 0; border: none; border-top: 1px solid rgba(128,128,128,0.2);'>
                    <p><b>Giriş Tarihi:</b> {lot_data['TARİH']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>SKT:</b> {lot_data.get('SKT (SON KULLANMA)', '-')}</p>
                    <p><b>Analiz Eden:</b> {lot_data['SERTİFİKA KONTROLÜ / ANALİZ YAPAN']}</p>
                    <p><b>Menşei:</b> {lot_data['MENŞEİ (ÜRETİM YERİ)']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Kaynak:</b> {lot_data['ORJİN (KAYNAK)']}</p>
                    <p><b>IFRA Durumu:</b> {lot_data.get('IFRA UYGUNLUK', '-')}</p>
                    <p><b>Mevcut Durum:</b> <span style='font-weight:bold; color: {karar_renk}; font-size: 18px;'>{lot_data['KABUL - RED']}</span></p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Doküman / CoA Yükleme
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 📎 Bu Lot İçin Analiz Sertifikası (CoA / SDS) Yükle")
            uploaded_doc = st.file_uploader("Sertifika PDF'i seçin", type=["pdf", "png", "jpg"], key="doc_uploader")
            if uploaded_doc:
                st.success(f"'{uploaded_doc.name}' dosyası {secilen_lot} partisine başarıyla arşivlendi!")

        # TERMAL DEPO ETİKETİ BASICI
        with col_p2:
            st.markdown("### 🖨️ Yazıcı Uyumlu Depo Etiketi")
            etiket_bg = "#27ae60" if lot_data["KABUL - RED"] == "KABUL" else ("#c0392b" if lot_data["KABUL - RED"] == "RED" else "#f39c12")
            etiket_baslik = "KABUL EDİLDİ - ÜRETİME UYGUNDUR" if lot_data["KABUL - RED"] == "KABUL" else ("RED - KULLANILAMAZ / İADE" if lot_data["KABUL - RED"] == "RED" else "KARANTİNA - TEST SÜRÜYOR")

            st.markdown(
                f"""
                <div style='background-color: white; color: black; padding: 25px; border-radius: 6px; border: 3px solid #333; box-shadow: 0 4px 15px rgba(0,0,0,0.3); font-family: monospace;'>
                    <div style='background-color: {etiket_bg}; color: white; text-align: center; padding: 8px; font-size: 16px; font-weight: 900; margin-bottom: 12px;'>
                        {etiket_baslik}
                    </div>
                    <p style='margin: 4px 0; font-size: 15px;'><b>ÜRÜN:</b> {lot_data['HAMMADDE ADI']}</p>
                    <p style='margin: 4px 0; font-size: 15px;'><b>LOT NO:</b> {lot_data['LOT NO']}</p>
                    <p style='margin: 4px 0; font-size: 13px;'><b>FİRMA:</b> {lot_data['FİRMA İSMİ']}</p>
                    <p style='margin: 4px 0; font-size: 13px;'><b>KONTROL TARİHİ:</b> {lot_data['TARİH']}</p>
                    <p style='margin: 4px 0; font-size: 13px;'><b>KONTROL EDEN:</b> {lot_data['SERTİFİKA KONTROLÜ / ANALİZ YAPAN']}</p>
                    <hr style='border: 1px dashed black; margin: 10px 0;'>
                    <p style='text-align: center; margin: 0; font-size: 11px;'>MİYAETP KALİTE GÜVENCE DİREKTÖRLÜĞÜ</p>
                </div>
                """,
                unsafe_allow_html=True
            )

# --- İMZA ALANI (SIDEBAR ALT) ---
st.sidebar.markdown(
    """
    <div style='background-color: rgba(128, 128, 128, 0.1); padding: 12px; border-radius: 8px; text-align: center; margin-top: 20px;'>
        <p style='margin: 0; font-size: 13px; font-weight: bold;'>Developed by</p>
        <p style='margin: 0; font-size: 18px; color: #FF4B4B; font-weight: 800;'>⚡ miyaetp</p>
        <p style='margin: 0; font-size: 11px; opacity: 0.7;'>v5.0.0 • Industrial Fragrance Suite</p>
    </div>
    """,
    unsafe_allow_html=True
)
