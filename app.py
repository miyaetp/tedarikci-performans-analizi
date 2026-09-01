import io
import datetime
import streamlit as st
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

# --- 3. NUMUNE HAFIZASI (SESSION STATE) ---
if "numuneler" not in st.session_state:
    st.session_state["numuneler"] = pd.DataFrame({
        "Numune Kodu": ["NUM-2026-001", "NUM-2026-002", "NUM-2026-003", "NUM-2026-004"],
        "Tedarikçi": ["Tedarikçi A", "Tedarikçi C", "Tedarikçi B", "Tedarikçi D"],
        "Numune Tanımı": ["Yeni Lot Esans Numunesi", "Kozmetik Alkol Şarjı", "Cam Şişe Prototipi", "Sprey Pompa Revizyonu"],
        "Kabul Tarihi": ["2026-08-28", "2026-08-30", "2026-08-31", "2026-09-01"],
        "Mevcut Durum": ["Analizde", "Kalite Onaylandı", "Bekliyor", "Reddedildi"],
        "Laboratuvar Notu": ["GC-MS ve koku testi sürüyor", "Spektroskopi testleri uygun bulundu", "Giriş test kuyruğunda", "Sızdırmazlık testinde kaçak tespit edildi"]
    })

# --- 4. TEDARİKÇİ VERİLERİ ---
@st.cache_data
def get_sample_data():
    return pd.DataFrame({
        "Tedarikçi": ["Tedarikçi A", "Tedarikçi B", "Tedarikçi C", "Tedarikçi D", "Tedarikçi E", "Tedarikçi F"],
        "Yıllık Harcama (Bin TL)": [9500, 3800, 5200, 2100, 2800, 1650],
        "Ret Oranı (%)": [0.8, 1.5, 3.8, 4.5, 1.2, 2.0],
        "Belge Eksikliği (%)": [0.2, 0.5, 2.1, 3.2, 0.9, 1.1],
        "Uygunsuzluk Sayısı": [1, 1, 5, 6, 2, 2],
        "Ortalama Teslim Gecikmesi (Gün)": [1.0, 1.2, 3.5, 4.0, 1.8, 2.0]
    })

# --- SOL MENÜ (SIDEBAR) SAYFA NAVİGASYONU ---
if st.sidebar.button("🚪 Güvenli Çıkış Yap"):
    st.session_state["authenticated"] = False
    st.rerun()

st.sidebar.title("📌 Modül / Sayfa Seçimi")
secilen_sayfa = st.sidebar.radio(
    "Gitmek İstediğiniz Sayfayı Seçin:",
    ["📊 Tedarikçi Kalite & Karar Paneli", "🧪 Dijital Numune Takip Sistemi"]
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
# SAYFA 2: DİJİTAL NUMUNE TAKİP SİSTEMİ (ESNEK & BOŞLUKLARI TOLERE EDEN MOD)
# ==============================================================================
else:
    st.title("🧪 Dijital Numune Takip & Süreç Yönetim Sistemi")
    st.caption("Numuneleri doğrudan kaydedin, geçmiş Excel arşivini içe aktarın ve analiz süreçlerini yönetin.")

    # --- ESNEK NUMUNE İÇE AKTARMA MOTORU ---
    with st.expander("📥 Geçmiş Numune Arşivini Excel / CSV Olarak İçe Aktar", expanded=False):
        col_up1, col_up2 = st.columns([2, 1])
        with col_up1:
            uploaded_samples = st.file_uploader("Numune Listesi Dosyası Seç (.xlsx veya .csv)", type=["xlsx", "csv"], key="numune_uploader")
            if uploaded_samples:
                try:
                    loaded_df = pd.read_csv(uploaded_samples) if uploaded_samples.name.endswith(".csv") else pd.read_excel(uploaded_samples)
                    
                    # Tamamen boş satırları temizle
                    loaded_df = loaded_df.dropna(how='all').reset_index(drop=True)
                    
                    if len(loaded_df) == 0:
                        st.warning("Yüklenen dosya boş!")
                    else:
                        # Eksik başlıkları otomatik oluştur ve varsayılan değerleri bas
                        bugun = datetime.date.today().strftime("%Y-%m-%d")
                        
                        if "Tedarikçi" not in loaded_df.columns:
                            loaded_df["Tedarikçi"] = "Bilinmeyen Tedarikçi"
                        else:
                            loaded_df["Tedarikçi"] = loaded_df["Tedarikçi"].fillna("Bilinmeyen Tedarikçi").astype(str)

                        if "Numune Tanımı" not in loaded_df.columns:
                            loaded_df["Numune Tanımı"] = "Genel Numune"
                        else:
                            loaded_df["Numune Tanımı"] = loaded_df["Numune Tanımı"].fillna("Genel Numune").astype(str)

                        if "Kabul Tarihi" not in loaded_df.columns:
                            loaded_df["Kabul Tarihi"] = bugun
                        else:
                            loaded_df["Kabul Tarihi"] = loaded_df["Kabul Tarihi"].fillna(bugun).astype(str)

                        if "Mevcut Durum" not in loaded_df.columns:
                            loaded_df["Mevcut Durum"] = "Bekliyor"
                        else:
                            loaded_df["Mevcut Durum"] = loaded_df["Mevcut Durum"].fillna("Bekliyor").astype(str)

                        if "Laboratuvar Notu" not in loaded_df.columns:
                            loaded_df["Laboratuvar Notu"] = "Not girilmedi"
                        else:
                            loaded_df["Laboratuvar Notu"] = loaded_df["Laboratuvar Notu"].fillna("Not girilmedi").astype(str)

                        if "Numune Kodu" not in loaded_df.columns:
                            loaded_df["Numune Kodu"] = [f"NUM-2026-{i+1:03d}" for i in range(len(loaded_df))]
                        else:
                            # Boş olan kodlara otomatik kod üret
                            for idx, val in enumerate(loaded_df["Numune Kodu"]):
                                if pd.isna(val) or str(val).strip() == "":
                                    loaded_df.at[idx, "Numune Kodu"] = f"NUM-2026-{idx+1:03d}"
                            loaded_df["Numune Kodu"] = loaded_df["Numune Kodu"].astype(str)

                        # Standart sütun sırasına sok
                        standart_df = loaded_df[["Numune Kodu", "Tedarikçi", "Numune Tanımı", "Kabul Tarihi", "Mevcut Durum", "Laboratuvar Notu"]]
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("🔄 Tabloyu Bu Verilerle Değiştir (Sıfırla & Yükle)"):
                                st.session_state["numuneler"] = standart_df
                                st.success(f"{len(standart_df)} adet dolu kayıt başarıyla aktarıldı!")
                                st.rerun()
                        with col_btn2:
                            if st.button("➕ Mevcut Listenin Altına Ekle"):
                                st.session_state["numuneler"] = pd.concat([st.session_state["numuneler"], standart_df], ignore_index=True)
                                st.success(f"{len(standart_df)} yeni kayıt listenin altına eklendi!")
                                st.rerun()
                                
                except Exception as e:
                    st.error(f"Dosya okunurken bir hata oluştu: {e}")

        with col_up2:
            st.markdown("**Örnek Şablon:**")
            st.caption("İsterseniz boş bir şablon indirip kullanabilirsiniz.")
            sample_template_io = io.BytesIO()
            with pd.ExcelWriter(sample_template_io, engine='openpyxl') as writer:
                st.session_state["numuneler"].to_excel(writer, index=False, sheet_name='Numune_Sablon')
            st.download_button(
                label="📄 Numune Şablonunu İndir",
                data=sample_template_io.getvalue(),
                file_name="Numune_Sablonu.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    s_df = st.session_state["numuneler"]
    
    # Canlı Durum Kartları
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Toplam Numune", f"{len(s_df)} Adet")
    col_m2.metric("⏳ Beklemede", f"{len(s_df[s_df['Mevcut Durum'] == 'Bekliyor'])} Adet")
    col_m3.metric("🔬 Analizde", f"{len(s_df[s_df['Mevcut Durum'] == 'Analizde'])} Adet")
    col_m4.metric("✅ Kalite Onaylı", f"{len(s_df[s_df['Mevcut Durum'] == 'Kalite Onaylandı'])} Adet")

    st.divider()

    # Üst Bölüm: Numune Ekleme ve Durum Güncelleme
    col_sol, col_sag = st.columns([1, 1.2])

    with col_sol:
        st.markdown("### ➕ Yeni Numune Kabul Girişi")
        with st.form("yeni_numune_form", clear_on_submit=True):
            oto_kod = f"NUM-2026-{len(st.session_state['numuneler']) + 1:03d}"
            st.text_input("Numune Kodu:", value=oto_kod, disabled=True)
            tedarikci_sec = st.text_input("Tedarikçi Firma:", placeholder="Örn: Firma A")
            tanim_gir = st.text_input("Numune Tanımı / Lot Numarası:", placeholder="Örn: Yeni Formülasyon Esans Şarjı")
            not_gir = st.text_input("Başlangıç Test Amacı:", placeholder="Örn: GC-MS Saflık ve Koku Testi")
            kayit_butonu = st.form_submit_button("📥 Numuneyi Kaydet")

            if kayit_butonu and tanim_gir and tedarikci_sec:
                yeni_kayit = pd.DataFrame([{
                    "Numune Kodu": oto_kod,
                    "Tedarikçi": tedarikci_sec,
                    "Numune Tanımı": tanim_gir,
                    "Kabul Tarihi": datetime.date.today().strftime("%Y-%m-%d"),
                    "Mevcut Durum": "Bekliyor",
                    "Laboratuvar Notu": not_gir if not_gir else "Kabul edildi, test sırasında bekliyor"
                }])
                st.session_state["numuneler"] = pd.concat([yeni_kayit, st.session_state["numuneler"]], ignore_index=True)
                st.success(f"{oto_kod} sisteme başarıyla işlendi!")
                st.rerun()

    with col_sag:
        st.markdown("### ⚡ Hızlı Durum & Sonuç Güncelleme")
        if len(st.session_state["numuneler"]) > 0:
            secili_kod = st.selectbox("İşlem Yapılacak Numuneyi Seçin:", st.session_state["numuneler"]["Numune Kodu"].tolist())
            idx = st.session_state["numuneler"][st.session_state["numuneler"]["Numune Kodu"] == secili_kod].index[0]
            satir = st.session_state["numuneler"].loc[idx]

            st.info(f"**Tedarikçi:** {satir['Tedarikçi']} | **Tanım:** {satir['Numune Tanımı']} | **Giriş:** {satir['Kabul Tarihi']}")
            
            durum_secenekleri = ["Bekliyor", "Analizde", "Kalite Onaylandı", "Reddedildi"]
            varsayilan_idx = durum_secenekleri.index(satir["Mevcut Durum"]) if satir["Mevcut Durum"] in durum_secenekleri else 0
            
            yeni_durum_sec = st.selectbox("Numunenin Yeni Durumu:", durum_secenekleri, index=varsayilan_idx)
            guncel_not_gir = st.text_area("Laboratuvar / Test Değerlendirme Notu:", value=satir["Laboratuvar Notu"], height=80)
            
            if st.button("💾 Sonucu Sisteme Kaydet", use_container_width=True):
                st.session_state["numuneler"].at[idx, "Mevcut Durum"] = yeni_durum_sec
                st.session_state["numuneler"].at[idx, "Laboratuvar Notu"] = guncel_not_gir
                st.success(f"{secili_kod} güncellendi!")
                st.rerun()

    st.divider()

    # Alt Bölüm: Görsel Süreç Tablosu & Excel Dışa Aktarma
    st.subheader("📋 Canlı Numune Takip Listesi")
    
    filtre = st.radio("Listelenecek Durum:", ["Tümü", "Bekliyor", "Analizde", "Kalite Onaylandı", "Reddedildi"], horizontal=True)
    gosterilecek_df = st.session_state["numuneler"] if filtre == "Tümü" else st.session_state["numuneler"][st.session_state["numuneler"]["Mevcut Durum"] == filtre]
    
    st.dataframe(gosterilecek_df, use_container_width=True)

    numune_excel = io.BytesIO()
    with pd.ExcelWriter(numune_excel, engine='openpyxl') as writer:
        st.session_state["numuneler"].to_excel(writer, index=False, sheet_name='Numune_Listesi')
    st.download_button(
        label="📥 Güncel Numune Raporunu Excel Olarak İndir",
        data=numune_excel.getvalue(),
        file_name="Numune_Takip_Raporu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- İMZA ALANI (SIDEBAR ALT) ---
st.sidebar.markdown(
    """
    <div style='background-color: rgba(128, 128, 128, 0.1); padding: 12px; border-radius: 8px; text-align: center; margin-top: 20px;'>
        <p style='margin: 0; font-size: 13px; font-weight: bold;'>Developed by</p>
        <p style='margin: 0; font-size: 18px; color: #FF4B4B; font-weight: 800;'>⚡ miyaetp</p>
        <p style='margin: 0; font-size: 11px; opacity: 0.7;'>v3.3.0 • Smart Tolerant Loader</p>
    </div>
    """,
    unsafe_allow_html=True
)
