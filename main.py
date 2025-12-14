import sqlite3

class Kutuphane:
    def __init__(self):
        self.baglanti_kur()

    def baglanti_kur(self):
        self.baglanti = sqlite3.connect("kutuphane.db")
        self.imlec = self.baglanti.cursor()
        
        # 1. KİTAPLAR TABLOSU
        # sahibi_id: Kitabı alan üyenin otomatik ID'si
        sorgu_kitap = """CREATE TABLE IF NOT EXISTS kitaplar (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            isim TEXT, 
            yazar TEXT, 
            yayinevi TEXT, 
            sayfa_sayisi INT, 
            sahibi_id INT
        )"""
        self.imlec.execute(sorgu_kitap)
        
        # 2. ÜYELER TABLOSU
        # Sadece ID, Ad, Soyad var. Numara yok, ID numara yerine geçiyor.
        sorgu_uye = """CREATE TABLE IF NOT EXISTS uyeler (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            ad TEXT, 
            soyad TEXT
        )"""
        self.imlec.execute(sorgu_uye)
        self.baglanti.commit()

    def baglantiyi_kes(self):
        self.baglanti.close()

    # --- LİSTELEME ---
    def kitaplari_listele(self):
        self.imlec.execute("SELECT * FROM kitaplar")
        liste = self.imlec.fetchall()
        print("\n--- 📚 KİTAP LİSTESİ ---")
        if len(liste) == 0:
            print("Kütüphane boş.")
        else:
            for i in liste:
                print(f"[ID: {i[0]}] {i[1]} - {i[2]} ({i[4]} Sayfa)")

    def uyeleri_listele(self):
        self.imlec.execute("SELECT * FROM uyeler")
        liste = self.imlec.fetchall()
        print("\n--- 👥 ÜYE LİSTESİ ---")
        if len(liste) == 0:
           print("Kayıtlı üye yok.")
        else:
            for i in liste:
                print(f"[Üye ID: {i[0]}] {i[1]} {i[2]}")

    # --- EKLEME ---
    def uye_ekle(self, ad, soyad):
        # Numara sormuyoruz, sistem otomatik veriyor
        sorgu = "INSERT INTO uyeler (ad, soyad) VALUES(?, ?)"
        self.imlec.execute(sorgu, (ad, soyad))    
        self.baglanti.commit()
        print(f"✅ Yeni üye eklendi: {ad} {soyad}")

    def kitap_ekle(self, isim, yazar, yayinevi, sayfa_sayisi):
        sorgu = "INSERT INTO kitaplar (isim, yazar, yayinevi, sayfa_sayisi, sahibi_id) VALUES(?,?,?,?,?)"
        self.imlec.execute(sorgu, (isim, yazar, yayinevi, sayfa_sayisi, None))
        self.baglanti.commit() 
        print(f"✅ Kitap eklendi: {isim}")

    # --- SİLME (KRİTİK BÖLÜM) ---
    def kitap_sil(self, kitap_id): 
        sorgu = "DELETE FROM kitaplar WHERE id = ?"
        self.imlec.execute(sorgu, (kitap_id,))
        self.baglanti.commit()
        print(f"🗑️ Kitap (ID: {kitap_id}) silindi.")

    # YENİ ÖZELLİK: GÜVENLİ ÜYE SİLME
    def uye_sil(self, uye_id):
        # 1. Önce üye var mı?
        self.imlec.execute("SELECT * FROM uyeler WHERE id = ?", (uye_id,))
        uye = self.imlec.fetchall()
        if len(uye) == 0:
            print("❌ Geçersiz Üye ID'si.")
            return

        # 2. KRİTİK KONTROL: Üyenin elinde kitap var mı?
        self.imlec.execute("SELECT * FROM kitaplar WHERE sahibi_id = ?", (uye_id,))
        elindeki_kitaplar = self.imlec.fetchall()
        
        if len(elindeki_kitaplar) > 0:
            print(f"❌ BU ÜYE SİLİNEMEZ! Şu an elinde {len(elindeki_kitaplar)} tane kitap var.")
            print("Lütfen önce kitapları iade alsın.")
            return

        # 3. Engel yoksa sil
        sorgu = "DELETE FROM uyeler WHERE id = ?"
        self.imlec.execute(sorgu, (uye_id,))
        self.baglanti.commit()
        print(f"✅ Üye (ID: {uye_id}) başarıyla silindi.")

    def sayfa_guncelle(self, kitap_id, yeni_sayfa):
        sorgu = "UPDATE kitaplar SET sayfa_sayisi = ? WHERE id = ?"
        self.imlec.execute(sorgu, (yeni_sayfa, kitap_id))
        self.baglanti.commit()
        print(f"🔄 Kitap (ID: {kitap_id}) güncellendi.")

    # --- ÖDÜNÇ VE İADE ---
    def kitap_ver(self, kitap_id, uye_id):
        self.imlec.execute("SELECT * FROM kitaplar WHERE id = ?", (kitap_id,))
        kitap = self.imlec.fetchall()
        if len(kitap) == 0:
            print("❌ Geçersiz Kitap ID'si!")
            return
        
        self.imlec.execute("SELECT * FROM uyeler WHERE id = ?", (uye_id,))
        uye = self.imlec.fetchall()
        if len(uye) == 0:
            print(f"❌ {uye_id} numaralı üye bulunamadı!")
            return

        if kitap[0][5] is not None:
            print("❌ Bu kitap zaten başkasına verilmiş.")
            return
            
        sorgu = "UPDATE kitaplar SET sahibi_id = ? WHERE id = ?"
        self.imlec.execute(sorgu, (uye_id, kitap_id))
        self.baglanti.commit()
        print(f"✅ Başarılı: Kitap (ID: {kitap_id}), Üye {uye_id}'ye verildi.")

    def kitap_iade(self, kitap_id):
        self.imlec.execute("SELECT * FROM kitaplar WHERE id = ?", (kitap_id,))
        kitap = self.imlec.fetchall()
        if len(kitap) == 0:
            print("❌ Geçersiz Kitap ID'si!")
            return
        
        if kitap[0][5] is None:
            print("❌ Bu kitap zaten kütüphanede (Rafta).")
            return
        
        sorgu = "UPDATE kitaplar SET sahibi_id = NULL WHERE id = ?"
        self.imlec.execute(sorgu, (kitap_id,))
        self.baglanti.commit()
        print(f"✅ İade Alındı: Kitap (ID: {kitap_id}) rafa kaldırıldı.")

    def detayli_listele(self):
        sorgu = """
        SELECT kitaplar.id, kitaplar.isim, uyeler.ad, uyeler.soyad 
        FROM kitaplar 
        LEFT JOIN uyeler ON kitaplar.sahibi_id = uyeler.id
        """
        self.imlec.execute(sorgu)
        full_liste = self.imlec.fetchall()
        print("\n--- 🔍 DETAYLI DURUM ---")
        if len(full_liste) == 0:
            print("Kütüphane boş.")
        else:
            for satir in full_liste:
                k_id = satir[0]
                isim = satir[1]
                uye_ad = satir[2]
                uye_soyad = satir[3]
                
                if uye_ad is None:
                    print(f"📕 [ID: {k_id}] {isim} -> RAFTA (Müsait)")
                else:
                    print(f"⛔ [ID: {k_id}] {isim} -> {uye_ad} {uye_soyad} okuyor.")

# --- ANA MENÜ ---

kutuphanem = Kutuphane()
print("\n=== 🏛️  HALK KÜTÜPHANESİ OTOMASYONU v3.0 (Türkçe) ===")

while True:
    print("\n" + "="*30)
    print("ANA MENÜ")
    print("1. 📚 Kitap İşlemleri")
    print("2. 👥 Üye ve Ödünç İşlemleri")
    print("q. Çıkış")
    print("="*30)
    
    secim = input("Seçiminiz: ")

    if secim == "q":
        kutuphanem.baglantiyi_kes()
        print("Sistemden çıkılıyor... İyi günler!")
        break

    # KİTAP MENÜSÜ
    elif secim == "1":
        while True:
            print("\n--- Kitap Yönetimi ---")
            print("1- Listele | 2- Ekle | 3- Sil (ID ile) | 4- Sayfa Güncelle | b- Geri")
            alt_islem = input("İşlem: ")
            
            if alt_islem == "b": break 
            elif alt_islem == "1":
                kutuphanem.kitaplari_listele()
            elif alt_islem == "2":
                isim = input("Kitap Adı: ")
                yazar = input("Yazar: ")
                yay = input("Yayınevi: ")
                try:
                    sayfa = int(input("Sayfa Sayısı: "))
                    kutuphanem.kitap_ekle(isim, yazar, yay, sayfa)
                except ValueError:
                    print("Lütfen sayfa sayısını rakamla giriniz.")
            elif alt_islem == "3":
                kutuphanem.kitaplari_listele() 
                try:
                    k_id = int(input("Silinecek Kitap ID'si: "))
                    kutuphanem.kitap_sil(k_id)
                except ValueError:
                    print("Lütfen rakam giriniz.")
            elif alt_islem == "4":
                kutuphanem.kitaplari_listele()
                try:
                    k_id = int(input("Güncellenecek Kitap ID'si: "))
                    yeni_sayfa = int(input("Yeni Sayfa Sayısı: "))
                    kutuphanem.sayfa_guncelle(k_id, yeni_sayfa)
                except ValueError:
                    print("Lütfen rakam giriniz.")

    # ÜYE MENÜSÜ
    elif secim == "2":
        while True:
            print("\n--- Üye ve Ödünç ---")
            print("1- Üyeleri Listele | 2- Üye Ekle | 3- ÜYE SİL (Yeni)")
            print("4- Kitap Ver (ID ile) | 5- İade Al (ID ile) | 6- Kimde Ne Var? | b- Geri")
            alt_islem = input("İşlem: ")
            
            if alt_islem == "b": break
            elif alt_islem == "1":
                kutuphanem.uyeleri_listele()
            elif alt_islem == "2":
                ad = input("Ad: ")       
                soyad = input("Soyad: ")
                kutuphanem.uye_ekle(ad, soyad)
            
            # YENİ EKLENEN KISIM
            elif alt_islem == "3":
                kutuphanem.uyeleri_listele()
                try:
                    u_id = int(input("Silinecek Üye ID: "))
                    kutuphanem.uye_sil(u_id)
                except ValueError:
                    print("Lütfen rakam giriniz.")

            elif alt_islem == "4":
                kutuphanem.kitaplari_listele() 
                try:
                    k_id = int(input("Verilecek Kitap ID'si: "))
                    u_id = int(input("Alan Üye ID'si: "))
                    kutuphanem.kitap_ver(k_id, u_id)
                except ValueError:
                    print("Lütfen rakam giriniz.")
            elif alt_islem == "5":
                try:
                    k_id = int(input("İade Edilecek Kitap ID'si: "))
                    kutuphanem.kitap_iade(k_id)
                except ValueError:
                    print("Geçersiz ID.")
            elif alt_islem == "6":
                kutuphanem.detayli_listele()