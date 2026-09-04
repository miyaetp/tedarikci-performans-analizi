from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'elso-kimya-qc-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kalite_kontrol.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- VERİTABANI MODELİ ---
class AnalizKaydi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tarih = db.Column(db.DateTime, default=datetime.utcnow)
    urun_kodu = db.Column(db.String(50), nullable=False)
    urun_adi = db.Column(db.String(100), nullable=False)
    lot_no = db.Column(db.String(50), nullable=False)
    analiz_turu = db.Column(db.String(50), nullable=False)  # Hammadde, Proses, Bitmiş Ürün
    
    # Kimyasal / Fiziksel Parametreler
    ph_degeri = db.Column(db.Float, nullable=True)
    yogunluk = db.Column(db.Float, nullable=True)          # g/cm³
    kirilma_indisi = db.Column(db.Float, nullable=True)    # Refraktometre (nD)
    viskozite = db.Column(db.Float, nullable=True)         # cP
    renk_gorunus = db.Column(db.String(100), nullable=True)
    
    # Değerlendirme & Takip
    durum = db.Column(db.String(20), default='Şartlı Kabul') # Onaylandı, Reddedildi, Şartlı Kabul
    aciklama = db.Column(db.Text, nullable=True)
    teknisyen = db.Column(db.String(50), nullable=False)

# Tabloları oluştur
with app.app_context():
    db.create_all()

# --- ROTALAR ---

@app.route('/')
def index():
    # En son eklenen analizler en üstte listelenir
    kayitlar = AnalizKaydi.query.order_by(AnalizKaydi.tarih.desc()).all()
    return render_template('index.html', kayitlar=kayitlar)

@app.route('/kayit-ekle', methods=['GET', 'POST'])
def kayit_ekle():
    if request.method == 'POST':
        try:
            yeni_kayit = AnalizKaydi(
                urun_kodu=request.form.get('urun_kodu'),
                urun_adi=request.form.get('urun_adi'),
                lot_no=request.form.get('lot_no'),
                analiz_turu=request.form.get('analiz_turu'),
                ph_degeri=float(request.form.get('ph_degeri')) if request.form.get('ph_degeri') else None,
                yogunluk=float(request.form.get('yogunluk')) if request.form.get('yogunluk') else None,
                kirilma_indisi=float(request.form.get('kirilma_indisi')) if request.form.get('kirilma_indisi') else None,
                viskozite=float(request.form.get('viskozite')) if request.form.get('viskozite') else None,
                renk_gorunus=request.form.get('renk_gorunus'),
                durum=request.form.get('durum'),
                aciklama=request.form.get('aciklama'),
                teknisyen=request.form.get('teknisyen')
            )
            db.session.add(yeni_kayit)
            db.session.commit()
            flash('Analiz kaydı başarıyla eklendi.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Kayıt eklenirken bir hata oluştu: {str(e)}', 'danger')
            return redirect(url_for('kayit_ekle'))
            
    return render_template('kayit_ekle.html')

@app.route('/kayit-sil/<int:id>', methods=['POST'])
def kayit_sil(id):
    kayit = AnalizKaydi.query.get_or_404(id)
    try:
        db.session.delete(kayit)
        db.session.commit()
        flash('Kayıt silindi.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('Silme işlemi başarısız.', 'danger')
    return redirect(url_for('index'))

@app.route('/kayit-detay/<int:id>')
def kayit_detay(id):
    kayit = AnalizKaydi.query.get_or_404(id)
    return render_template('detay.html', kayit=kayit)

if __name__ == '__main__':
    app.run(debug=True)
