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
    page_title="Kalite Güvence & Proses Kontrol Sistemi | miyaetp",
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
                <p style='color: gray; font-size: 14px;'>Parfüm Kalite Kontrol & Güvence Platformu</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.text_input("Giriş Şifresi:", type="password", key="password_input", on_change=check_password)
        st.button("Giriş Yap", on_click=check_password, use_container_width=True)
        st.caption("⚡ Developed by **miyaetp**")
    st.stop()

# --- 3. NUMUNE VE KALİTE HAFIZASI ---
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

# Kusur Dağılımı Verisi (Pareto için)
if "kusurlar" not in st.session_state:
    st.session_state["kusurlar"] = pd.DataFrame({
        "Kusur Türü": [
            "Sızdırmazlık / Pompa Kaçağı",
            "Organoleptik Koku Sapması",
            "Eksik / Hatalı Etiketleme",
            "Cam Şişede Çizik / Deformasyon",
            "Eksik CoA Analiz Sertifikası",
            "Dansite / Kırılma Sapması",
            "Ambalaj Koli Hasarı"
        ],
        "Hata Sayısı": [42, 28, 18, 12, 9, 5, 2]
    })

# --- SOL MENÜ (SIDEBAR) ---
if st.sidebar.button("🚪 Güvenli Çıkış Yap"):
    st.session_state["authenticated"] = False
    st.rerun()

st.sidebar.title("📌 Kalite Yönetim Menüsü")
secilen_sayfa = st.sidebar.radio(
    "Gitmek İstediğiniz Sayfayı Seçin:",
    [
        "🧪 Canlı Numune & Hammadde Takip",
        "🔬 Parfüm Laboratuvar Doğrulama (IFRA/Fizikokimya)",
        "⚙️ Proses Kalite: Sızdırmazlık, Krimp & Tork",
        "📊 Kalite İstatistikleri: SPC & Pareto Analizi",
        "🧫 Hijyen, Mikrobiyoloji & Stabilite Testi",
        "🏷️ Depo Etiket Basıcı & Lot Pasaportu"
    ]
)
st.sidebar.divider()

# ==============================================================================
# MODÜL 1: CANLI NUMUNE & HAMMADDE TAKİP
# ==============================================================================
if secilen_sayfa == "🧪 Canlı Numune & Hammadde Takip":
    st.title("🧪 Canlı Numune & Hammadde Kalite Takip Sistemi")
    st.caption("Giriş Kalite Kontrol Kayıtları, Kabul/Red Kararları ve Raf Ömrü (SKT) Uyarıları")

    s_df = st.session_state["numuneler"].copy()

    # SKT Kontrolü
    today = datetime.date.today()
    alerts = []
    for idx, r in s_df.iterrows():
        try:
            skt = datetime.datetime.strptime(str(r.get("SKT (SON KULLANMA)", "")).strip(), "%Y-%m-%d").date()
            diff = (skt - today).days
            if diff < 0:
                alerts.append(f"🔴 **{r['HAMMADDE ADI']} ({r['LOT NO']})** SKT'si {abs(diff)} gün önce DOLDU!")
            elif diff <= 60:
                alerts.append(f"🟡 **{r['HAMMADDE ADI']} ({r['LOT NO']})** SKT yaklaşıyor: {diff} gün kaldı.")
        except:
            pass

    if alerts:
        with st.expander("⚠️ DİKKAT: Raf Ömrü & Re-Test Alarmları", expanded=True):
            for a in alerts:
                st.markdown(a)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Toplam Kayıt", f"{len(s_df)} Adet")
    col_m2.metric("✅ KABUL", f"{len(s_df[s_df['KABUL - RED'] == 'KABUL'])} Adet")
    col_m3.metric("🔴 RED", f"{len(s_df[s_df['KABUL - RED'] == 'RED'])} Adet")
    col_m4.metric("⏳ BEKLİYOR", f"{len(s_df[s_df['KABUL - RED'] == 'BEKLİYOR'])} Adet")

    st.divider()

    karar_f = st.radio("Kabul / Red Filtresi:", ["Tümü", "KABUL", "RED", "BEKLİYOR"], horizontal=True)
    gosterim_df = s_df if karar_f == "Tümü" else s_df[s_df["KABUL - RED"] == karar_f]
    st.dataframe(gosterim_df, use_container_width=True)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        s_df.to_excel(writer, index=False, sheet_name='Kalite_Kontrol')
    st.download_button("📥 Tabloyu Excel Olarak İndir", buf.getvalue(), "Kalite_Kontrol_Listesi.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ==============================================================================
# MODÜL 2: PARFÜM LABORATUVAR DOĞRULAMA (IFRA & FİZİKOKİMYA)
# ==============================================================================
elif secilen_sayfa == "🔬 Parfüm Laboratuvar Doğrulama (IFRA/Fizikokimya)":
    st.title("🔬 Parfüm & Kozmetik Laboratuvar Doğrulama")
    st.caption("Fizikokimyasal Cihaz Ölçümleri, Organoleptik Testler ve IFRA Standart Kontrolü")

    with st.form("lab_dogrulama_form"):
        col1, col2 = st.columns(2)
        with col1:
            h_tur = st.selectbox("Hammadde Türü:", ["Esans / Koku Yağı", "Kozmetik Alkol (%96)"])
            h_ad = st.text_input("Hammadde & Lot No:", value="Bergamot & Amber Esansı - LOT-2026-112")
            h_koku = st.selectbox("Organoleptik (Koku Testi):", [
                "Standart Şahit Numune ile Birebir Uyumlu",
                "Hafif Nüans Farkı (Tolerans İçi)",
                "Belirgin Yabancı Koku / Okside (Ret)"
            ])
            h_renk = st.selectbox("Görünüm & Tortu:", ["Berrak / Tortusuz", "Bulanık / Çökeltili (Ret)"])
        with col2:
            refrak = st.number_input("Kırılma İndisi (Refraktometre 20°C):", min_value=1.300, max_value=1.600, value=1.492, step=0.001, format="%.3f")
            dan = st.number_input("Dansite / Bağıl Yoğunluk (d20/20):", min_value=0.700, max_value=1.300, value=0.985, step=0.001, format="%.3f")
            alkol_deg = st.number_input("Alkol Derecesi (% Vol 20°C):", min_value=80.0, max_value=100.0, value=96.4, step=0.1) if h_tur == "Kozmetik Alkol (%96)" else 0.0
            ifra_ok = st.checkbox("IFRA 51. Amendment Kategori 4 Uygunluk Sertifikası Var", value=True)
            coa_ok = st.checkbox("İmzalı Üretici Analiz Sertifikası (CoA) Mevcut", value=True)

        onay_btn = st.form_submit_button("⚡ Kalite Uygunluğunu Değerlendir")

    if onay_btn:
        hatalar = []
        if h_tur == "Esans / Koku Yağı":
            if not (1.450 <= refrak <= 1.520):
                hatalar.append(f"Kırılma indisi ({refrak}) tolerans dışı! (1.450 - 1.520 olmalı)")
            if not (0.850 <= dan <= 1.080):
                hatalar.append(f"Dansite ({dan}) tolerans dışı! (0.850 - 1.080 olmalı)")
        elif h_tur == "Kozmetik Alkol (%96)":
            if alkol_deg < 96.0:
                hatalar.append(f"Alkol derecesi (%{alkol_deg}) kozmetik limitin altındadır! (Min %96.0)")

        if "Ret" in h_koku:
            hatalar.append("Organoleptik: Koku profilinde yabancı solvent veya oksidasyon sapması!")
        if "Bulanık" in h_renk:
            hatalar.append("Fiziksel: Üründe çökelti veya tortu saptandı!")
        if not ifra_ok:
            hatalar.append("Mevzuat: IFRA 51 sertifikası eksik!")
        if not coa_ok:
            hatalar.append("Belge: Analiz Sertifikası (CoA) bulunamadı!")

        if not hatalar:
            st.success("🟢 **SONUÇ: TAM KALİTE ONAYI (KABUL)** — Fizikokimyasal ve mevzuat kriterleri uygundur.")
        else:
            st.error("🔴 **SONUÇ: UYGUNSUZLUK TESPİT EDİLDİ (RED)**")
            for h in hatalar:
                st.write(f"- ❌ {h}")

# ==============================================================================
# MODÜL 3: PROSES KALİTE: SIZDIRMAZLIK, KRİMP & TORK TESTİ
# ==============================================================================
elif secilen_sayfa == "⚙️ Proses Kalite: Sızdırmazlık, Krimp & Tork":
    st.title("⚙️ Proses Kalite: Şişe Sızdırmazlık, Krimp & Tork Kontrolü")
    st.caption("Dolum Hattı İçi Vakum Desikatör Kaçak Testi, Krimp Boğaz Kumpas Ölçümü ve Kapak Tork Değerleri")

    tab_vakum, tab_krimp, tab_tork = st.tabs([
        "💨 Vakum Desikatör Sızdırmazlık Testi",
        "📐 Krimp Yüksekliği & Çap Kumpas Kontrolü",
        "🔩 Kapak Açma / Kapama Tork Ölçümü"
    ])

    with tab_vakum:
        st.subheader("💨 Vakum Kaçak Testi (Vakum Desikatörü)")
        st.caption("Numuneler su dolu desikatör tankına daldırılır ve negatif basınç altında hava kabarcığı izlenir.")

        col_v1, col_v2 = st.columns(2)
        with col_v1:
            vakum_basinc = st.slider("Uygulanan Negatif Basınç (Bar):", -1.0, 0.0, -0.6, 0.05)
            test_suresi = st.slider("Vakumda Tutma Süresi (Dakika):", 1, 10, 3)
            test_adet = st.number_input("Test Edilen Numune Adedi:", min_value=1, value=20)
            sizdiran_adet = st.number_input("Hava Kabarcığı / Kaçak Çıkaran Numune Adedi:", min_value=0, value=0)

        with col_v2:
            st.markdown("#### Test Değerlendirmesi:")
            if sizdiran_adet == 0:
                st.success(f"🟢 **SIZDIRMAZLIK ONAYLANDI:** {test_adet} adet numunenin hiçbirinde {vakum_basinc} bar basınç altında mikro kaçak tespit edilmedi.")
            else:
                fire_orani = (sizdiran_adet / test_adet) * 100
                st.error(f"🔴 **SIZDIRMAZLIK RET:** {sizdiran_adet} adet şişede kaçak tespit edildi! (Hata Oranı: %{fire_orani:.1f})")
                st.warning("Öneri: Valf krimp çenesi basıncını ve şişe boğaz conta oturmasını kontrol edin.")

    with tab_krimp:
        st.subheader("📐 FEA 15 / FEA 20 Krimp Ölçüm Doğrulama")
        st.caption("Sprey pompanın şişe boğazına krimp edilme çapı ve yüksekliği kumpasla doğrulanır.")

        col_k1, col_k2 = st.columns(2)
        with col_k1:
            valf_tipi = st.selectbox("Valf Tipi:", ["FEA 15 (Standart Parfüm)", "FEA 20 (Geniş Boğaz)"])
            olculen_cap = st.number_input("Ölçülen Krimp Dış Çapı (mm):", min_value=14.0, max_value=22.0, value=15.35, step=0.01, format="%.2f")
            olculen_yukseklik = st.number_input("Ölçülen Krimp Yüksekliği (mm):", min_value=6.0, max_value=10.0, value=7.20, step=0.01, format="%.2f")

        with col_k2:
            st.markdown("#### Tolerans Doğrulaması:")
            # FEA 15 Toleransları: Çap 15.25 - 15.45 mm, Yükseklik 7.00 - 7.30 mm
            cap_ok = (15.25 <= olculen_cap <= 15.45) if "15" in valf_tipi else (19.80 <= olculen_cap <= 20.10)
            yuk_ok = (7.00 <= olculen_yukseklik <= 7.35)

            if cap_ok and yuk_ok:
                st.success("🟢 **ÖLÇÜMLER UYGUN:** Krimp çapı ve yüksekliği teknik çizim toleransı içindedir.")
            else:
                if not cap_ok:
                    st.error(f"❌ Krimp çapı ({olculen_cap} mm) tolerans dışı!")
                if not yuk_ok:
                    st.error(f"❌ Krimp yüksekliği ({olculen_yukseklik} mm) tolerans dışı!")

    with tab_tork:
        st.subheader("🔩 Vidalı / Manyetik Kapak Tork Kontrolü")
        st.caption("Kapakların gevşek kalmaması ve tüketici tarafından kolay açılabilmesi için torkmetre ölçümü.")

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            hedef_tork = st.slider("Hedef Sıkma Torku (Nm):", 0.5, 3.0, 1.5, 0.1)
            olculen_tork = st.number_input("Torkmetreden Okunan Değer (Nm):", min_value=0.0, max_value=5.0, value=1.45, step=0.05)

        with col_t2:
            fark = abs(olculen_tork - hedef_tork)
            if fark <= 0.25:
                st.success(f"🟢 **TORK UYGUN:** Ölçülen {olculen_tork} Nm değeri hedef aralık içindedir.")
            elif olculen_tork < hedef_tork:
                st.warning(f"🟡 **GEVŞEK KAPAK:** {olculen_tork} Nm (Sızıntı riski var, sıkma kuvvetini artırın).")
            else:
                st.error(f"🔴 **AŞIRI SIKILMIŞ:** {olculen_tork} Nm (Kapak kırma veya diş atlatma riski).")

# ==============================================================================
# MODÜL 4: KALİTE İSTATİSTİKLERİ: SPC & PARETO ANALİZİ
# ==============================================================================
elif secilen_sayfa == "📊 Kalite İstatistikleri: SPC & Pareto Analizi":
    st.title("📊 İstatistiksel Proses Kontrol (SPC) & Pareto Analizi")
    st.caption("Parti Bazlı Süreç Değişkenliği (Shewhart Kontrol Kartı) ve En Sık Karşılaşılan Kalite Hataları")

    tab_spc, tab_pareto = st.tabs(["📈 Shewhart X-bar Kontrol Kartı (SPC)", "📊 Pareto Kusur Analizi (80/20 Kuralı)"])

    with tab_spc:
        st.subheader("📈 Kritik Parametre Değişkenlik Takibi (Dansite Örneği)")
        st.caption("Son 10 partide gelen esansın dansite değerlerinin Üst/Alt Kontrol Limitleri (UCL/LCL) içindeki kararlılığı.")

        parti_no = [f"Parti {i+1}" for i in range(10)]
        dansite_degerleri = [0.985, 0.988, 0.983, 0.990, 0.986, 0.992, 0.984, 0.987, 0.989, 0.986]

        ort_d = np.mean(dansite_degerleri)
        ucl = ort_d + 0.015  # Üst Limit
        lcl = ort_d - 0.015  # Alt Limit

        fig_spc = go.Figure()
        fig_spc.add_trace(go.Scatter(x=parti_no, y=dansite_degerleri, mode='lines+markers', name='Ölçülen Dansite', line=dict(color='#00CC96', width=2)))
        fig_spc.add_trace(go.Scatter(x=parti_no, y=[ucl]*10, mode='lines', name='Üst Kontrol Limiti (UCL)', line=dict(color='red', dash='dash')))
        fig_spc.add_trace(go.Scatter(x=parti_no, y=[ort_d]*10, mode='lines', name='Proses Ortalaması', line=dict(color='yellow', dash='dot')))
        fig_spc.add_trace(go.Scatter(x=parti_no, y=[lcl]*10, mode='lines', name='Alt Kontrol Limiti (LCL)', line=dict(color='red', dash='dash')))

        fig_spc.update_layout(height=400, yaxis_title="Dansite (g/ml)", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_spc, use_container_width=True)
        st.info("💡 **SPC Yorumu:** Tüm partiler kontrol limitleri içerisindedir. Süreç kararlıdır ve rastgele sapmalar dışı özel nedenli bir hata eğilimi gözlenmemektedir.")

    with tab_pareto:
        st.subheader("📊 Pareto Kusur Analizi (En Çok Hata Veren %20)")
        k_df = st.session_state["kusurlar"].sort_values(by="Hata Sayısı", ascending=False)
        k_df["Kümülatif"] = k_df["Hata Sayısı"].cumsum()
        k_df["Kümülatif Yüzde"] = (k_df["Kümülatif"] / k_df["Hata Sayısı"].sum()) * 100

        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(x=k_df["Kusur Türü"], y=k_df["Hata Sayısı"], name="Kusur Sayısı", marker_color="#FF4B4B"))
        fig_pareto.add_trace(go.Scatter(x=k_df["Kusur Türü"], y=k_df["Kümülatif Yüzde"], name="Kümülatif %", yaxis="y2", line=dict(color="#00CC96", width=2)))

        fig_pareto.update_layout(
            height=400,
            yaxis=dict(title="Kusur Frekansı (Adet)"),
            yaxis2=dict(title="Kümülatif %", overlaying="y", side="right", range=[0, 105]),
            legend=dict(x=0.7, y=1.1, orientation="h"),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_pareto, use_container_width=True)
        st.warning("⚠️ **Kalite Aksiyon Tavsiyesi:** Toplam hataların %60'ından fazlası **'Sızdırmazlık'** ve **'Koku Sapması'** kaynaklıdır. DÖF çalışmalarının bu iki konuya odaklanması fabrikanın fire maliyetini doğrudan düşürecektir.")

# ==============================================================================
# MODÜL 5: HİJYEN, MİKROBİYOLOJİ & STABİLİTE TESTİ
# ==============================================================================
elif secilen_sayfa == "🧫 Hijyen, Mikrobiyoloji & Stabilite Testi":
    st.title("🧫 Mikrobiyoloji, Hat Sanitasyonu & Hızlandırılmış Stabilite")
    st.caption("ISO 22716 GMP Gereklilikleri: Hat Temizliği Doğrulama ve Etüv İçi Hızlandırılmış Stabilite Takibi")

    tab_mikro, tab_stab = st.tabs(["🧽 Hat Sanitasyonu & Mikrobiyoloji", "🔥 Hızlandırılmış Stabilite (40°C Etüv)"])

    with tab_mikro:
        st.subheader("🧽 Dolum Hattı & Kazan Sanitasyon Doğrulama (ATP Swab)")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            hat_adi = st.selectbox("Denetlenen Hat / Ekipman:", ["Hat 1 - 50ml Dolum Nozulu", "Hat 2 - 100ml Otomatik Krimp Başlığı", "Kazan A - 1000L Paslanmaz Çelik Karıştırıcı"])
            olculen_atp = st.number_input("Yüzeyden Okunan ATP Değeri (RLU):", min_value=0, max_value=2000, value=22)
            mikro_cfu = st.number_input("Durulama Suyu Canlı Sayımı (CFU/ml):", min_value=0, max_value=500, value=0)

        with col_m2:
            st.markdown("#### Sanitasyon Onay Kararı:")
            # Standart: ATP < 30 RLU Temiz, TVC < 10 CFU/ml Temiz
            atp_ok = olculen_atp < 30
            mikro_ok = mikro_cfu < 10

            if atp_ok and mikro_ok:
                st.success(f"🟢 **HİJYEN ONAYLANDI:** {hat_adi} mikrobiyolojik ve organik kirleticilerden arındırılmıştır. Dolum başlayabilir.")
            else:
                st.error("🔴 **HİJYEN YETERSİZ (BLOKE):**")
                if not atp_ok:
                    st.write(f"- ❌ Yüzey ATP değeri ({olculen_atp} RLU) sınırın (30 RLU) üzerinde!")
                if not mikro_ok:
                    st.write(f"- ❌ Mikrobiyolojik yük ({mikro_cfu} CFU/ml) tespit edildi!")
                st.warning("Aksiyon: CIP (Clean-in-Place) sıcak su ve alkol ile dezenfeksiyon işlemini tekrarlayın.")

    with tab_stab:
        st.subheader("🔥 Hızlandırılmış Yaşlandırma & Stabilite Takibi (40°C & UV)")
        st.caption("Parfümün 3 yıllık raf ömrünü simüle etmek için etüvde bekletilen şahit numunelerin fiziksel kontrolü.")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            stab_lot = st.text_input("Stabilite Takip Numunesi:", value="Summer Breeze EDP - STB-01")
            etuv_sure = st.selectbox("Etüvde Kalma Süresi (40°C):", ["1. Ay Kontrolü (1 Yıla Eşdeğer)", "2. Ay Kontrolü (2 Yıla Eşdeğer)", "3. Ay Kontrolü (3 Yıla Eşdeğer)"])
            ayrisma = st.checkbox("Faz Ayrışması / Yağ Ayrılması Var mı?", value=False)
            renk_donme = st.checkbox("Belirgin Renk Dönmesi / Kararma Var mı?", value=False)
            koku_degisim = st.checkbox("Koku Bozulması / Ekşime Saptandı mı?", value=False)

        with col_s2:
            st.markdown("#### Stabilite Raporu:")
            if not (ayrisma or renk_donme or koku_degisim):
                st.success(f"🟢 **STABİL:** {stab_lot} için {etuv_sure} başarıyla tamamlanmıştır. Formülasyon fiziksel ve kimyasal olarak kararlıdır.")
            else:
                st.error(f"🔴 **STABİLİTE BOZULMASI:** {stab_lot} formülasyonunda sapma saptandı!")
                if ayrisma:
                    st.write("- ❌ Çözünürlük problemi / faz ayrışması tespit edildi (Solubilizer oranını artırın).")
                if renk_donme:
                    st.write("- ❌ Işık veya sıcaklık etkisiyle renk bozulması var (UV filtresi / BHT antioksidan gerekebilir).")
                if koku_degisim:
                    st.write("- ❌ Koku moleküllerinde oksidasyon saptandı.")

# ==============================================================================
# MODÜL 6: DEPO ETİKET BASICI & LOT PASAPORTU
# ==============================================================================
elif secilen_sayfa == "🏷️ Depo Etiket Basıcı & Lot Pasaportu":
    st.title("🏷️ Depo Giriş Etiketi & Akıllı Lot Pasaportu")
    s_df = st.session_state["numuneler"]
    sec_lot = st.selectbox("İşlem Yapılacak Lot:", s_df["LOT NO"].unique())
    ld = s_df[s_df["LOT NO"] == sec_lot].iloc[0]

    col_e1, col_e2 = st.columns([1.2, 1])
    with col_e1:
        st.markdown("### 📋 Dijital Kalite Pasaportu")
        k_renk = "#00b894" if ld["KABUL - RED"] == "KABUL" else ("#d63031" if ld["KABUL - RED"] == "RED" else "#fdcb6e")
        st.markdown(
            f"""
            <div style='background: rgba(128,128,128,0.08); border-left: 6px solid {k_renk}; padding: 20px; border-radius: 8px;'>
                <h3>{ld['HAMMADDE ADI']}</h3>
                <p>Lot No: <b>{ld['LOT NO']}</b> | Üretici: <b>{ld['FİRMA İSMİ']}</b></p>
                <p>Giriş: {ld['TARİH']} &nbsp;|&nbsp; SKT: {ld.get('SKT (SON KULLANMA)', '-')}</p>
                <p>Kontrol Eden: {ld['SERTİFİKA KONTROLÜ / ANALİZ YAPAN']}</p>
                <p>IFRA: {ld.get('IFRA UYGUNLUK', '-')}</p>
                <p>Mevcut Durum: <b style='color:{k_renk}; font-size:18px;'>{ld['KABUL - RED']}</b></p>
            </div>
            """, unsafe_allow_html=True
        )

    with col_e2:
        st.markdown("### 🖨️ Yazıcı Uyumlu Depo Termal Etiketi")
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
                <p style='text-align: center; margin: 0; font-size: 11px;'>MİYAETP KALİTE GÜVENCE DİREKTÖRLÜĞÜ</p>
            </div>
            """, unsafe_allow_html=True
        )

# --- İMZA ALANI (SIDEBAR ALT) ---
st.sidebar.markdown(
    """
    <div style='background-color: rgba(128, 128, 128, 0.1); padding: 12px; border-radius: 8px; text-align: center; margin-top: 20px;'>
        <p style='margin: 0; font-size: 13px; font-weight: bold;'>Developed by</p>
        <p style='margin: 0; font-size: 18px; color: #FF4B4B; font-weight: 800;'>⚡ miyaetp</p>
        <p style='margin: 0; font-size: 11px; opacity: 0.7;'>v7.0.0 • Total Quality Control Edition</p>
    </div>
    """,
    unsafe_allow_html=True
)

