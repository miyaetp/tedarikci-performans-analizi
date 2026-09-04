import io
import math
import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. Sayfa Yapılandırması
st.set_page_config(
    page_title="Mega Kalite & Üretim Suite | miyaetp",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SOL MENÜ AÇMA BUTONUNU SABİT TUTAN VE REKLAMLARI GİZLEYEN CSS ---
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
                <p style='color: gray; font-size: 14px;'>Parfüm Kalite & Üretim Yönetim Sistemi</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.text_input("Giriş Şifresi:", type="password", key="password_input", on_change=check_password)
        st.button("Giriş Yap", on_click=check_password, use_container_width=True)
        st.caption("⚡ Developed by **miyaetp**")
    st.stop()

# --- 3. NUMUNE HAFIZASI (SESSION STATE) ---
KALITE_KOLONLARI = [
    "HAMMADDE ADI", "FİRMA İSMİ", "LOT NO", "TARİH", "SERTİFİKA KONTROLÜ / ANALİZ YAPAN",
    "AMBALAJ TEMİZLİĞİ", "ETİKET UYGUNLUK", "KABUL - RED", "MENŞEİ (ÜRETİM YERİ)",
    "RUBY ANALİZ DURUMU", "COA", "RUBY TDS", "RUBY SDS", "ORJİN (KAYNAK)",
    "DOĞAL / REACH NO", "SKT (SON KULLANMA)", "IFRA UYGUNLUK", "MİKTAR (Birim)", "BİRİM FİYAT (TL)"
]

if "numuneler" not in st.session_state:
    st.session_state["numuneler"] = pd.DataFrame([
        {
            "HAMMADDE ADI": "Oud Wood Esans", "FİRMA İSMİ": "Grasse Fragrance Ltd.", "LOT NO": "LOT-2026-088",
            "TARİH": "2026-08-28", "SERTİFİKA KONTROLÜ / ANALİZ YAPAN": "Uygun / Ahmet K.", "AMBALAJ TEMİZLİĞİ": "Temiz - Uygun",
            "ETİKET UYGUNLUK": "Uygun", "KABUL - RED": "KABUL", "MENŞEİ (ÜRETİM YERİ)": "Fransa",
            "RUBY ANALİZ DURUMU": "Tamamlandı", "COA": "Var", "RUBY TDS": "Mevcut", "RUBY SDS": "Mevcut",
            "ORJİN (KAYNAK)": "Sentetik/Doğal Karışım", "DOĞAL / REACH NO": "REACH-092831",
            "SKT (SON KULLANMA)": "2027-08-28", "IFRA UYGUNLUK": "IFRA 51 - Onaylı (%12 Kat. 4)",
            "MİKTAR (Birim)": 250, "BİRİM FİYAT (TL)": 1850
        },
        {
            "HAMMADDE ADI": "Kozmetik Denatüre Alkol %96", "FİRMA İSMİ": "Etanol Kimya Sanayi", "LOT NO": "LOT-2026-104",
            "TARİH": "2026-08-30", "SERTİFİKA KONTROLÜ / ANALİZ YAPAN": "GC-MS Testi / Mehmet A.", "AMBALAJ TEMİZLİĞİ": "Varil Temiz",
            "ETİKET UYGUNLUK": "Uygun", "KABUL - RED": "KABUL", "MENŞEİ (ÜRETİM YERİ)": "Türkiye",
            "RUBY ANALİZ DURUMU": "Onaylandı", "COA": "Var", "RUBY TDS": "Mevcut", "RUBY SDS": "Mevcut",
            "ORJİN (KAYNAK)": "Tarımsal Etanol", "DOĞAL / REACH NO": "REACH-883102",
            "SKT (SON KULLANMA)": "2028-08-30", "IFRA UYGUNLUK": "Muaf (Çözücü)",
            "MİKTAR (Birim)": 2000, "BİRİM FİYAT (TL)": 45
        },
        {
            "HAMMADDE ADI": "100ml Lüks Cam Şişe", "FİRMA İSMİ": "Vetro Ambalaj A.Ş.", "LOT NO": "LOT-2026-310",
            "TARİH": "2026-09-01", "SERTİFİKA KONTROLÜ / ANALİZ YAPAN": "Sızdırmazlık / Selin Y.", "AMBALAJ TEMİZLİĞİ": "Koli Deforme",
            "ETİKET UYGUNLUK": "Eksik Lot Yazısı", "KABUL - RED": "RED", "MENŞEİ (ÜRETİM YERİ)": "İtalya",
            "RUBY ANALİZ DURUMU": "Kaçak Tespit Edildi", "COA": "Yok", "RUBY TDS": "Eksik", "RUBY SDS": "Mevcut Değil",
            "ORJİN (KAYNAK)": "Cam", "DOĞAL / REACH NO": "-",
            "SKT (SON KULLANMA)": "2030-01-01", "IFRA UYGUNLUK": "Muaf (Ambalaj)",
            "MİKTAR (Birim)": 5000, "BİRİM FİYAT (TL)": 28
        }
    ])

# --- 4. TEDARİKÇİ VERİLERİ ---
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

st.sidebar.title("📌 Mega Modül Seçimi")
secilen_sayfa = st.sidebar.radio(
    "Gitmek İstediğiniz Sayfayı Seçin:",
    [
        "📊 Tedarikçi Kalite & Karar Paneli",
        "🧪 Canlı Numune & Hammadde Takip",
        "🔬 Parfüm Laboratuvar Doğrulama (IFRA/Fizikokimya)",
        "🏷️ Depo Etiket Basıcı & Lot Pasaportu",
        "💰 Finans, BOM & 8D Kalite Mühendisliği",
        "🏭 Parfüm Üretim & Saha Operasyonları Paketi"
    ]
)
st.sidebar.divider()

# ==============================================================================
# MODÜL 1: TEDARİKÇİ KALİTE & KARAR PANELİ
# ==============================================================================
if secilen_sayfa == "📊 Tedarikçi Kalite & Karar Paneli":
    st.sidebar.header("⚙️ Değerlendirme Ağırlıkları (%)")
    w_ret = st.sidebar.slider("Ret Oranı Ağırlığı", 0, 100, 35, step=5)
    w_belge = st.sidebar.slider("Belge / Sertifika Eksikliği Ağırlığı", 0, 100, 25, step=5)
    w_uyg = st.sidebar.slider("Uygunsuzluk Sayısı Ağırlığı", 0, 100, 25, step=5)
    w_teslim = st.sidebar.slider("Teslimat Gecikmesi Ağırlığı", 0, 100, 15, step=5)

    total_weight = w_ret + w_belge + w_uyg + w_teslim
    norm_factor = 100 / total_weight if total_weight > 0 else 1

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

    st.title("📊 Tedarikçi Kalite & Performans Karar Sistemi")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Genel Kalite Skoru", f"{analyzed_df['Performans Skoru'].mean():.1f} / 100")
    col2.metric("Ortalama Ret Oranı", f"%{analyzed_df['Ret Oranı (%)'].mean():.1f}")
    col3.metric("Ort. Belge Eksikliği", f"%{analyzed_df['Belge Eksikliği (%)'].mean():.1f}")
    col4.metric("Ort. Teslim Gecikmesi", f"{analyzed_df['Ortalama Teslim Gecikmesi (Gün)'].mean():.1f} Gün")

    st.divider()
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Genel Kalite Sıralaması", "🎯 Harcama & Risk Matrisi", "⚔️ İki Tedarikçi Kıyaslama", "📈 6 Aylık Trend & Karne", "📄 Resmi DÖF & İhtar Mektubu"])

    with tab1:
        sorted_df = analyzed_df.sort_values(by="Performans Skoru", ascending=True)
        fig_bar = px.bar(sorted_df, x="Performans Skoru", y="Tedarikçi", orientation="h", text="Performans Skoru", color="Performans Skoru", color_continuous_scale="Tealgrn", range_x=[0, 100])
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        fig_scatter = px.scatter(analyzed_df, x="Performans Skoru", y="Yıllık Harcama (Bin TL)", text="Tedarikçi", size="Yıllık Harcama (Bin TL)", color="Performans Skoru", color_continuous_scale="RdYlGn", range_x=[0, 105])
        fig_scatter.add_vline(x=70, line_dash="dash", line_color="gray", annotation_text="Kritik Eşik (70 Puan)")
        st.plotly_chart(fig_scatter, use_container_width=True)

    with tab3:
        s1 = st.selectbox("1. Tedarikçi:", analyzed_df["Tedarikçi"].unique(), index=0)
        s2 = st.selectbox("2. Tedarikçi:", analyzed_df["Tedarikçi"].unique(), index=1)
        r1, r2 = analyzed_df[analyzed_df["Tedarikçi"] == s1].iloc[0], analyzed_df[analyzed_df["Tedarikçi"] == s2].iloc[0]
        cats = ['Ret Başarısı', 'Belge Tamlığı', 'Kalite Uygunluğu', 'Termin Sadakati']
        v1 = [max(0, 100 - r1['Ret Oranı (%)'] * 12), max(0, 100 - r1['Belge Eksikliği (%)'] * 18), max(0, 100 - r1['Uygunsuzluk Sayısı'] * 12), max(0, 100 - r1['Ortalama Teslim Gecikmesi (Gün)'] * 15)]
        v2 = [max(0, 100 - r2['Ret Oranı (%)'] * 12), max(0, 100 - r2['Belge Eksikliği (%)'] * 18), max(0, 100 - r2['Uygunsuzluk Sayısı'] * 12), max(0, 100 - r2['Ortalama Teslim Gecikmesi (Gün)'] * 15)]
        fig_compare = go.Figure()
        fig_compare.add_trace(go.Scatterpolar(r=v1, theta=cats, fill='toself', name=s1, line=dict(color='#00CC96')))
        fig_compare.add_trace(go.Scatterpolar(r=v2, theta=cats, fill='toself', name=s2, line=dict(color='#EF553B')))
        st.plotly_chart(fig_compare, use_container_width=True)

    with tab4:
        st.subheader("📈 Tedarikçi 6 Aylık Kalite Trendi")
        trend_s = st.selectbox("Tedarikçi Seçin:", analyzed_df["Tedarikçi"].unique())
        base_s = analyzed_df[analyzed_df["Tedarikçi"] == trend_s]["Performans Skoru"].iloc[0]
        months = ["Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos"]
        np.random.seed(abs(hash(trend_s)) % 10000)
        m_scores = [np.clip(base_s + f, 30, 100) for f in np.random.uniform(-5, 5, size=5)] + [base_s]
        fig_trend = px.line(pd.DataFrame({"Ay": months, "Performans Skoru": m_scores}), x="Ay", y="Performans Skoru", markers=True, range_y=[0, 105])
        st.plotly_chart(fig_trend, use_container_width=True)

    with tab5:
        st.subheader("📄 Resmi DÖF / İhtar Mektubu")
        dof_s = st.selectbox("İhtar Gönderilecek Firma:", analyzed_df["Tedarikçi"].unique(), key="dof_s")
        dof_r = analyzed_df[analyzed_df["Tedarikçi"] == dof_s].iloc[0]
        let = f"SAYIN {dof_s.upper()} KALİTE GÜVENCE MÜDÜRLÜĞÜNE,\n\nFabrikamız giriş kalite analizlerinde genel kalite skorunuz 100 üzerinden {dof_r['Performans Skoru']} olarak ölçülmüştür.\n- Ret Oranı: %{dof_r['Ret Oranı (%)']}\n- Belge Eksikliği: %{dof_r['Belge Eksikliği (%)']}\n\n5 iş günü içinde 8D DÖF planınızı iletmenizi rica ederiz.\n\nKalite Güvence Direktörlüğü"
        st.text_area("Mektup:", let, height=200)
        st.download_button("📥 Mektubu İndir (.txt)", let, file_name=f"DOF_{dof_s}.txt")

# ==============================================================================
# MODÜL 2: CANLI NUMUNE & HAMMADDE TAKİP (SKT VE ALARM DESTEKLİ)
# ==============================================================================
elif secilen_sayfa == "🧪 Canlı Numune & Hammadde Takip":
    st.title("🧪 Canlı Numune & Hammadde Kalite Takip Sistemi")
    s_df = st.session_state["numuneler"].copy()

    # SKT Alarm Motoru
    today = datetime.date.today()
    alerts = []
    for idx, r in s_df.iterrows():
        try:
            skt = datetime.datetime.strptime(str(r.get("SKT (SON KULLANMA)", "")).strip(), "%Y-%m-%d").date()
            diff = (skt - today).days
            if diff < 0: alerts.append(f"🔴 **{r['HAMMADDE ADI']} ({r['LOT NO']})** SKT'si {abs(diff)} gün önce DOLMUŞTUR!")
            elif diff <= 60: alerts.append(f"🟡 **{r['HAMMADDE ADI']} ({r['LOT NO']})** SKT yaklaşıyor: {diff} gün kaldı.")
        except: pass

    if alerts:
        with st.expander("⚠️ DİKKAT: Raf Ömrü & Re-Test Alarmları", expanded=True):
            for a in alerts: st.markdown(a)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Toplam Kayıt", f"{len(s_df)} Adet")
    col_m2.metric("✅ KABUL", f"{len(s_df[s_df['KABUL - RED'] == 'KABUL'])} Adet")
    col_m3.metric("🔴 RED", f"{len(s_df[s_df['KABUL - RED'] == 'RED'])} Adet")
    col_m4.metric("⏳ BEKLİYOR", f"{len(s_df[s_df['KABUL - RED'] == 'BEKLİYOR'])} Adet")
    st.divider()

    st.subheader("📋 Canlı Numune & Hammadde Takip Tablosu")
    karar_f = st.radio("Filtre:", ["Tümü", "KABUL", "RED", "BEKLİYOR"], horizontal=True)
    gosterim_df = s_df if karar_f == "Tümü" else s_df[s_df["KABUL - RED"] == karar_f]
    st.dataframe(gosterim_df, use_container_width=True)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer: s_df.to_excel(writer, index=False, sheet_name='Numuneler')
    st.download_button("📥 Excel Olarak İndir", buf.getvalue(), "Numune_Listesi.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ==============================================================================
# MODÜL 3: PARFÜM LABORATUVAR DOĞRULAMA (IFRA / FİZİKOKİMYA)
# ==============================================================================
elif secilen_sayfa == "🔬 Parfüm Laboratuvar Doğrulama (IFRA/Fizikokimya)":
    st.title("🔬 Parfüm & Kozmetik Laboratuvar Doğrulama")
    st.caption("Fizikokimyasal Cihaz Kontrolleri, Organoleptik Testler ve IFRA Uygunluk Motoru")

    with st.form("parfum_lab_form"):
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            h_tur = st.selectbox("Hammadde Türü:", ["Esans / Koku Yağı", "Kozmetik Alkol (%96)"])
            h_ad = st.text_input("Hammadde & Lot:", value="Rose Damascena - LOT-2026-99")
            h_koku = st.selectbox("Organoleptik (Koku Testi):", ["Standart Numune ile Birebir Uyumlu", "Hafif Nüans Farkı (Tolerans İçi)", "Belirgin Yabancı Koku / Okside (Ret)"])
            h_renk = st.selectbox("Görünüm:", ["Berrak / Tortusuz", "Bulanık / Çökeltili (Ret)"])
        with col_l2:
            st.markdown("**Cihaz Ölçüm Değerleri:**")
            refrak = st.number_input("Kırılma İndisi (Refraktometre 20°C):", min_value=1.300, max_value=1.600, value=1.495, step=0.001, format="%.3f")
            dan = st.number_input("Dansite / Bağıl Yoğunluk (d20/20):", min_value=0.700, max_value=1.300, value=0.980, step=0.001, format="%.3f")
            alkol_deg = st.number_input("Alkol Derecesi (% Vol 20°C):", min_value=80.0, max_value=100.0, value=96.4, step=0.1) if h_tur == "Kozmetik Alkol (%96)" else 0.0
            ifra_check = st.checkbox("IFRA 51. Amendment Kategori 4 Uygunluk Sertifikası Var", value=True)
            coa_check = st.checkbox("İmzalı CoA Analiz Sertifikası Mevcut", value=True)

        lab_btn = st.form_submit_button("⚡ Kalite Uygunluğunu Değerlendir")

    if lab_btn:
        hatalar = []
        if h_tur == "Esans / Koku Yağı":
            if not (1.450 <= refrak <= 1.520): hatalar.append(f"Kırılma indisi ({refrak}) limitler (1.450-1.520) dışındadır!")
            if not (0.850 <= dan <= 1.080): hatalar.append(f"Dansite ({dan}) limitler (0.850-1.080) dışındadır!")
        elif h_tur == "Kozmetik Alkol (%96)":
            if alkol_deg < 96.0: hatalar.append(f"Alkol derecesi (%{alkol_deg}) kozmetik limitin (%96.0) altındadır!")
        if "Ret" in h_koku: hatalar.append("Organoleptik: Koku profilinde bariz yabancı koku sapması!")
        if "Bulanık" in h_renk: hatalar.append("Fiziksel: Üründe tortu veya çökelti mevcut!")
        if not ifra_check: hatalar.append("Mevzuat: IFRA 51 Uygunluk Belgesi eksik!")
        if not coa_check: hatalar.append("Belge: Üretici Analiz Sertifikası (CoA) eksik!")

        if not hatalar:
            st.success("🟢 **SONUÇ: TAM KALİTE ONAYI (KABUL)** — Tüm fizikokimyasal ve IFRA kriterleri uygundur.")
        else:
            st.error("🔴 **SONUÇ: UYGUNSUZLUK (RED / BLOKE)**")
            for h in hatalar: st.write(f"- ❌ {h}")

# ==============================================================================
# MODÜL 4: DEPO ETİKET BASICI & LOT PASAPORTU
# ==============================================================================
elif secilen_sayfa == "🏷️ Depo Etiket Basıcı & Lot Pasaportu":
    st.title("🏷️ Depo Giriş Etiketi & Akıllı Lot Pasaportu")
    s_df = st.session_state["numuneler"]
    sec_lot = st.selectbox("İşlem Yapılacak Lotu Seçin:", s_df["LOT NO"].unique())
    ld = s_df[s_df["LOT NO"] == sec_lot].iloc[0]

    col_e1, col_e2 = st.columns([1.2, 1])
    with col_e1:
        st.markdown("### 📋 Lot Pasaportu")
        k_renk = "#00b894" if ld["KABUL - RED"] == "KABUL" else ("#d63031" if ld["KABUL - RED"] == "RED" else "#fdcb6e")
        st.markdown(
            f"""
            <div style='background: rgba(128,128,128,0.08); border-left: 6px solid {k_renk}; padding: 20px; border-radius: 8px;'>
                <h3>{ld['HAMMADDE ADI']}</h3>
                <p>Lot: <b>{ld['LOT NO']}</b> | Üretici: <b>{ld['FİRMA İSMİ']}</b></p>
                <p>Giriş: {ld['TARİH']} | SKT: {ld.get('SKT (SON KULLANMA)', '-')}</p>
                <p>Analiz Eden: {ld['SERTİFİKA KONTROLÜ / ANALİZ YAPAN']}</p>
                <p>Durum: <b style='color:{k_renk}; font-size:18px;'>{ld['KABUL - RED']}</b></p>
            </div>
            """, unsafe_allow_html=True
        )

    with col_e2:
        st.markdown("### 🖨️ Yazıcı Uyumlu Depo Etiketi")
        bg = "#27ae60" if ld["KABUL - RED"] == "KABUL" else ("#c0392b" if ld["KABUL - RED"] == "RED" else "#f39c12")
        title = "KABUL EDİLDİ - ÜRETİME UYGUNDUR" if ld["KABUL - RED"] == "KABUL" else ("RED - KULLANILAMAZ" if ld["KABUL - RED"] == "RED" else "KARANTİNA")
        st.markdown(
            f"""
            <div style='background: white; color: black; padding: 20px; border-radius: 6px; border: 3px solid #333; font-family: monospace;'>
                <div style='background: {bg}; color: white; text-align: center; padding: 6px; font-weight: 900; margin-bottom: 10px;'>{title}</div>
                <p style='margin: 3px 0;'><b>ÜRÜN:</b> {ld['HAMMADDE ADI']}</p>
                <p style='margin: 3px 0;'><b>LOT:</b> {ld['LOT NO']}</p>
                <p style='margin: 3px 0;'><b>FİRMA:</b> {ld['FİRMA İSMİ']}</p>
                <p style='margin: 3px 0;'><b>TARİH:</b> {ld['TARİH']}</p>
                <hr style='border: 1px dashed black; margin: 8px 0;'>
                <p style='text-align: center; margin: 0; font-size: 11px;'>MİYAETP KALİTE DİREKTÖRLÜĞÜ</p>
            </div>
            """, unsafe_allow_html=True
        )

# ==============================================================================
# MODÜL 5: FİNANS, BOM & 8D KALİTE MÜHENDİSLİĞİ
# ==============================================================================
elif secilen_sayfa == "💰 Finans, BOM & 8D Kalite Mühendisliği":
    st.title("💰 Kalitesizlik Maliyeti, Reçete (BOM) Kilidi & 8D Analizi")
    st.caption("Finansal Kesinti Dekontları (Debit Note), Formülasyon Onay Kilidi ve Kök Neden Araştırması")

    tab_maliyet, tab_bom, tab_8d = st.tabs(["💸 Kalitesizlik Maliyeti & Debit Note", "🧴 Reçete / BOM Üretim Kilidi", "🔍 8D & Balık Kılçığı Analizi"])

    # 1. Maliyet & Debit Note
    with tab_maliyet:
        st.subheader("💸 Kalite Ret Maliyet Sayacı & Tedarikçi İade Dekontu")
        s_df = st.session_state["numuneler"]
        red_df = s_df[s_df["KABUL - RED"] == "RED"]
        
        toplam_zarar = (red_df["MİKTAR (Birim)"] * red_df["BİRİM FİYAT (TL)"]).sum()
        st.metric("🔥 Tedarikçi Hatalarından Kaynaklı Toplam İade Zararı", f"{toplam_zarar:,.2f} TL")

        st.markdown("---")
        st.markdown("#### 📄 Resmi Tedarikçi Fatura Kesinti Dekontu (Debit Note)")
        if len(red_df) > 0:
            sec_red = st.selectbox("İade Dekontu Düzenlenecek Reddedilen Lot:", red_df["LOT NO"].tolist())
            row_red = red_df[red_df["LOT NO"] == sec_red].iloc[0]
            maliyet = row_red["MİKTAR (Birim)"] * row_red["BİRİM FİYAT (TL)"]

            debit_text = f"""RESMİ FATURA KESİNTİ / İADE BİLDİRİMİ (DEBIT NOTE)
Tarih: {datetime.date.today().strftime('%d.%m.%Y')}
Muhatap Firma: {row_red['FİRMA İSMİ']}

Konu: Giriş Kalite Kontrol Ret İadesi ve Bedel Mahsubu

Sayın Yetkili,
Tesisimize teslim edilen {row_red['HAMMADDE ADI']} (Lot No: {row_red['LOT NO']}) giriş kalite kontrol testlerini geçememiş ve 'RED' edilmiştir.

İadeye Konu Bilgiler:
- Reddedilen Miktar: {row_red['MİKTAR (Birim)']} Adet/Kg
- Birim Fiyat: {row_red['BİRİM FİYAT (TL)']} TL
- TOPLAM MAHSUP EDİLECEK TUTAR: {maliyet:,.2f} TL

İlgili tutar cari hesabınızdan mahsup edilmiş olup, kusurlu ürünlerin 3 iş günü içinde depomuzdan teslim alınmasını rica ederiz.

miyaetp Kalite & Muhasebe Direktörlüğü"""
            st.text_area("Düzenlenen Dekont Metni:", debit_text, height=220)
            st.download_button("📥 Debit Note İndir (.txt)", debit_text, file_name=f"DebitNote_{sec_red}.txt")
        else:
            st.info("Kayıtlı 'RED' durumunda hammadde bulunmamaktadır.")

    # 2. Reçete (BOM) Kontrolü
    with tab_bom:
        st.subheader("🧴 Parfüm Formülü (BOM) Üretim Uygunluk Kilidi")
        st.caption("Dolum hattına girmeden önce reçetedeki tüm bileşenlerin 'KABUL' durumu denetlenir.")

        parfum_secim = st.selectbox("Üretime Alınacak Parfüm Reçetesi:", ["50ml EDP Summer Breeze", "100ml Extrait De Parfum Intense"])
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            sec_esans = st.selectbox("Kullanılacak Esans Lotu:", s_df[s_df["HAMMADDE ADI"].str.contains("Esans")]["LOT NO"].tolist())
            sec_alkol = st.selectbox("Kullanılacak Alkol Lotu:", s_df[s_df["HAMMADDE ADI"].str.contains("Alkol")]["LOT NO"].tolist())
        with col_b2:
            sec_sise = st.selectbox("Kullanılacak Şişe Lotu:", s_df[s_df["HAMMADDE ADI"].str.contains("Şişe")]["LOT NO"].tolist())

        esans_durum = s_df[s_df["LOT NO"] == sec_esans]["KABUL - RED"].values[0]
        alkol_durum = s_df[s_df["LOT NO"] == sec_alkol]["KABUL - RED"].values[0]
        sise_durum = s_df[s_df["LOT NO"] == sec_sise]["KABUL - RED"].values[0]

        st.markdown("#### Bileşen Kalite Kontrol Durumu:")
        st.write(f"- Esans ({sec_esans}): **{esans_durum}**")
        st.write(f"- Alkol ({sec_alkol}): **{alkol_durum}**")
        st.write(f"- Şişe ({sec_sise}): **{sise_durum}**")

        if esans_durum == "KABUL" and alkol_durum == "KABUL" and sise_durum == "KABUL":
            st.success("🟢 **ÜRETİM HATTI AÇIK:** Reçetedeki tüm bileşenler onaylıdır. Dolum başlatılabilir!")
        else:
            st.error("🔴 **ÜRETİM HATTI KİLİTLENDİ:** Reçetedeki onaylanmamış veya reddedilmiş bileşenler var! Hatalı üretime izin verilemez.")

    # 3. 8D & Balık Kılçığı
    with tab_8d:
        st.subheader("🔍 8D Kök Neden & Ishikawa (Balık Kılçığı) Analizi")
        col_8a, col_8b = st.columns(2)
        with col_8a:
            problem = st.text_input("Tespit Edilen Problem:", value="Cam şişe sprey krimp noktasından esans sızdırıyor")
            k_insan = st.text_input("1. İnsan Faktörü:", value="Operatör tork ayarını kontrol etmedi")
            k_makine = st.text_input("2. Makine / Ekipman:", value="Pnömatik sıkma başlığı kalibrasyondan çıkmış")
        with col_8b:
            k_metot = st.text_input("3. Metot / Yöntem:", value="Hat başı sızdırmazlık test sıklığı yetersiz")
            k_malzeme = st.text_input("4. Malzeme / Tolerans:", value="Şişe boğaz çapında +0.8mm sapma var")
            k_aksiyon = st.text_input("Önleyici Kalıcı Faaliyet (D3/D4):", value="Kalıp revizyonu yapıldı ve hat başı vakum testi zorunlu kılındı")

        st.info(f"**8D Kök Neden Özeti:** '{problem}' problemi için temel kök neden: '{k_malzeme}' olarak belirlenmiş, kalıcı önlem olarak '{k_aksiyon}' devreye alınmıştır.")

# ==============================================================================
# MODÜL 6: PARFÜM ÜRETİM & SAHA OPERASYONLARI PAKETİ
# ==============================================================================
elif secilen_sayfa == "🏭 Parfüm Üretim & Saha Operasyonları Paketi":
    st.title("🏭 Parfüm Üretim & Saha Operasyonları Paketi")
    st.caption("Maserasyon Takvimi, AQL Örneklem, ADR Kimyasal Güvenlik, Kör Koku Testi ve Lojistik İstifleme")

    tab_mase, tab_aql, tab_adr, tab_koku, tab_palet = st.tabs([
        "⏳ Maserasyon Takvimi",
        "🎯 AQL Örneklem (ISO 2859-1)",
        "🧯 ADR Kimyasal Depo Güvenliği",
        "👃 Kör Koku Testi (Panelist)",
        "📦 Palet & Koli Lojistik Planlayıcı"
    ])

    # 1. Maserasyon Takvimi
    with tab_mase:
        st.subheader("⏳ Parfüm Dinlendirme & Maserasyon Takip Takvimi")
        st.caption("Esans ve alkol birleştikten sonra koku profilinin oturması için dinlendirme süresi hesaplayıcı.")
        
        m_tarih = st.date_input("Karışımın Hazırlandığı Tarih:", datetime.date.today() - datetime.timedelta(days=12))
        m_tip = st.selectbox("Parfüm Konsantrasyonu:", ["Eau de Parfum (EDP - %18 Esans)", "Extrait de Parfum (%25 Esans)", "Eau de Toilette (EDT - %10 Esans)"])
        
        hedef_gun = 28 if "EDP" in m_tip else (42 if "Extrait" in m_tip else 18)
        gecen_gun = (datetime.date.today() - m_tarih).days
        kalan_gun = max(0, hedef_gun - gecen_gun)
        
        col_ms1, col_ms2 = st.columns(2)
        col_ms1.metric("Geçen Süre", f"{gecen_gun} Gün")
        col_ms2.metric("Maserasyon Tamamlanmasına", f"{kalan_gun} Gün Kaldı", delta=-kalan_gun)
        
        if kalan_gun == 0:
            st.success("🟢 **OLGUNLAŞTI:** Bu partinin maserasyon süresi tamamlandı. Filtreleme ve dolum hattına verilebilir!")
        else:
            st.warning(f"🟡 **DİNLENMEDE:** Koku piramidinin oturması için {kalan_gun} gün daha tankta bekletilmelidir.")

    # 2. ISO 2859-1 AQL Örneklem
    with tab_aql:
        st.subheader("🎯 AQL Örneklem ve Kabul Sınırı Hesaplayıcı (ISO 2859-1)")
        st.caption("Gelen parti büyüklüğüne göre kalite ekibinin kaç koli/numune açacağını belirler.")
        
        parti_adet = st.number_input("Gelen Parti Büyüklüğü (Adet):", min_value=100, max_value=500000, value=25000, step=1000)
        aql_seviye = st.selectbox("Kabul Edilebilir Kalite Limiti (AQL):", ["AQL 1.0 (Kritik - Şişe/Valf)", "AQL 2.5 (Standart - Etiket/Kutu)", "AQL 4.0 (Minör - Dış Koli)"])

        # Basitleştirilmiş ISO 2859-1 Tablo Mantığı
        if parti_adet <= 500: n_size = 50; max_ret = 1 if "1.0" in aql_seviye else 2
        elif parti_adet <= 3200: n_size = 125; max_ret = 3 if "1.0" in aql_seviye else 5
        elif parti_adet <= 35000: n_size = 315; max_ret = 7 if "1.0" in aql_seviye else 14
        else: n_size = 500; max_ret = 10 if "1.0" in aql_seviye else 21

        col_aq1, col_aq2 = st.columns(2)
        col_aq1.metric("Rastgele Seçilecek Numune", f"{n_size} Adet")
        col_aq2.metric("Maksimum İzin Verilen Kusur", f"{max_ret} Adet")
        st.info(f"**Karar Kuralı:** {n_size} adet numune incelenir. Kusurlu sayısı **{max_ret} veya daha az** ise partinin tamamı KABUL edilir. **{max_ret + 1}** kusur çıkarsa partinin tamamı REDDEDİLİR.")

    # 3. ADR Kimyasal Depo Güvenliği
    with tab_adr:
        st.subheader("🧯 ADR Kimyasal Birlikte Depolama Güvenlik Matrisi")
        st.caption("Yanıcı etanol, esans yağları ve asit/bazların yan yana konulma riskini denetler.")

        m1 = st.selectbox("1. Malzeme:", ["Etanol %96 (Sınıf 3 - Alevlenir Sıvı)", "Konsantre Esans Yağı (Sınıf 9 - Çevreye Zararlı)", "Hidrojen Peroksit (Sınıf 5.1 - Oksitleyici)"])
        m2 = st.selectbox("2. Malzeme:", ["Hidrojen Peroksit (Sınıf 5.1 - Oksitleyici)", "Etanol %96 (Sınıf 3 - Alevlenir Sıvı)", "Konsantre Esans Yağı (Sınıf 9 - Çevreye Zararlı)"])

        if ("Etanol" in m1 and "Oksitleyici" in m2) or ("Oksitleyici" in m1 and "Etanol" in m2):
            st.error("💥 **KRİTİK YANGIN / PATLAMA RİSKİ:** Alevlenir sıvılar ile güçlü oksitleyiciler ASLA aynı rafta veya odada depolanamaz! Yangına dayanıklı ayrı bölmelere taşıyın.")
        else:
            st.success("🟢 **GÜVENLİ DEPOLAMA:** Bu iki hammadde sınıfı genel depo kurallarına uyularak yan yana tutulabilir.")

    # 4. Kör Koku Testi (Blind Smell)
    with tab_koku:
        st.subheader("👃 Kör Koku Testi (Blind Mouillette Testi) & Radar Analizi")
        st.caption("Gelen yeni parti ile standart şahit numune arasındaki koku piramidi sapmasını ölçün.")

        col_kok1, col_kok2 = st.columns(2)
        with col_kok1:
            st.markdown("**Standart Şahit Numune Puanı (1-10):**")
            s_top = st.slider("Üst Nota (Narenciye/Uçucu):", 1, 10, 9, key="s_top")
            s_mid = st.slider("Kalp Nota (Çiçeksi/Baharat):", 1, 10, 8, key="s_mid")
            s_base = st.slider("Dip Nota (Odunsu/Amber):", 1, 10, 9, key="s_base")
            s_kalici = st.slider("Kalıcılık & Yayılım (Silaj):", 1, 10, 8, key="s_kal")
        with col_kok2:
            st.markdown("**Yeni Gelen Parti Puanı (1-10):**")
            p_top = st.slider("Üst Nota (Yeni Parti):", 1, 10, 8, key="p_top")
            p_mid = st.slider("Kalp Nota (Yeni Parti):", 1, 10, 8, key="p_mid")
            p_base = st.slider("Dip Nota (Yeni Parti):", 1, 10, 6, key="p_base")
            p_kalici = st.slider("Kalıcılık (Yeni Parti):", 1, 10, 6, key="p_kal")

        fig_smell = go.Figure()
        cats_k = ['Üst Nota', 'Kalp Nota', 'Dip Nota', 'Kalıcılık/Silaj']
        fig_smell.add_trace(go.Scatterpolar(r=[s_top, s_mid, s_base, s_kalici], theta=cats_k, fill='toself', name='Şahit Standart Numune', line=dict(color='#00CC96')))
        fig_smell.add_trace(go.Scatterpolar(r=[p_top, p_mid, p_base, p_kalici], theta=cats_k, fill='toself', name='Yeni Gelen Parti', line=dict(color='#EF553B')))
        st.plotly_chart(fig_smell, use_container_width=True)

    # 5. Palet ve İstifleme
    with tab_palet:
        st.subheader("📦 Euro Palet (80x120 cm) Koli & İstifleme Hesaplayıcı")
        col_pl1, col_pl2 = st.columns(2)
        with col_pl1:
            k_en = st.number_input("Koli Eni (cm):", value=30)
            k_boy = st.number_input("Koli Boyu (cm):", value=40)
            k_yuk = st.number_input("Koli Yüksekliği (cm):", value=25)
            k_agirlik = st.number_input("1 Koli Ağırlığı (kg):", value=12.0)
        with col_pl2:
            max_yuk = st.number_input("Maksimum Palet Yüksekliği (cm):", value=180)
            
            # Basit Koli Dizilim Mantığı
            kat_basi = math.floor((80 / k_en)) * math.floor((120 / k_boy))
            kat_sayisi = math.floor(max_yuk / k_yuk)
            toplam_koli = kat_basi * kat_sayisi
            toplam_agirlik = toplam_koli * k_agirlik

            st.metric("1 Katta Bulunan Koli", f"{kat_basi} Koli")
            st.metric("Maksimum İstif Katı", f"{kat_sayisi} Kat")
            st.metric("1 Palete Sığan Toplam Koli", f"{toplam_koli} Adet Koli")
            st.metric("Toplam Palet Ağırlığı", f"{toplam_agirlik:,.1f} Kg")

# --- İMZA ALANI (SIDEBAR ALT) ---
st.sidebar.markdown(
    """
    <div style='background-color: rgba(128, 128, 128, 0.1); padding: 12px; border-radius: 8px; text-align: center; margin-top: 20px;'>
        <p style='margin: 0; font-size: 13px; font-weight: bold;'>Developed by</p>
        <p style='margin: 0; font-size: 18px; color: #FF4B4B; font-weight: 800;'>⚡ miyaetp</p>
        <p style='margin: 0; font-size: 11px; opacity: 0.7;'>v6.0.0 • Industrial Factory Master Suite</p>
    </div>
    """,
    unsafe_allow_html=True
)
