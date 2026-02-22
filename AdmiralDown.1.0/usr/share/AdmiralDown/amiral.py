#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yz_engine
import sys
import os
import pygame
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, QDialog, QGraphicsOpacityEffect, QSizePolicy)
from PyQt5.QtCore import Qt, QRectF, QSize, QTimer, QPropertyAnimation, QSequentialAnimationGroup, QUrl
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QMovie, QFont, QTransform, QIcon

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

# Linux/Debian tabanlı sistemler için X11 zorlaması
os.environ["QT_QPA_PLATFORM"] = "xcb"

class SonucDiyalog(QDialog):
    def __init__(self, kazanan, oyuncu_istatistik, yz_istatistik, ana_dizin):
        super().__init__()
        self.setFixedSize(960, 620) # Burası böyle kalsın böyle ideal.
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #000810; border: 2px solid #004466;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(0)

        # 1. RESİM VE YAZI ALANI
        self.label = QLabel()
        self.label.setFixedSize(960, 540)
        
        resim_adi = "oyuncuwin.png" if kazanan == "PLAYER" else "yzwin.png"
        resim_yolu = os.path.join(ana_dizin, "images and sounds", resim_adi)
        
        pixmap = QPixmap(resim_yolu)
        if pixmap.isNull():
            pixmap = QPixmap(960, 540)
            pixmap.fill(QColor(0, 10, 20))

        painter = QPainter(pixmap)
        if painter.isActive():
            painter.setRenderHint(QPainter.Antialiasing)
            
            # --- FONT VE YAZIM ---
            def metin_yaz(x, y, metin, font_boyutu, renk, sag_hizala=False):
                font = QFont("Verdana", font_boyutu, QFont.Bold)
                painter.setFont(font)
                painter.setPen(QColor(0, 0, 0, 200)) # Gölge
                if sag_hizala:
                    w = painter.fontMetrics().width(metin)
                    painter.drawText(x - w + 2, y + 2, metin)
                    painter.setPen(renk)
                    painter.drawText(x - w, y, metin)
                else:
                    painter.drawText(x + 2, y + 2, metin)
                    painter.setPen(renk)
                    painter.drawText(x, y, metin)

            # Başlıklar
            metin_yaz(30, 50, "ADMIRAL DOWN !!!", 30, QColor(255, 200, 0))
            metin_yaz(30, 90, f"WINNER: {kazanan}", 22, QColor(0, 255, 255))
            
            # Oyuncu (Sol) - Resme göre daha aşağı ve toplu
            metin_yaz(30, 140, "PLAYER DATA", 14, QColor(255, 255, 255))
            metin_yaz(30, 165, f"Shots: {oyuncu_istatistik['toplam']}", 14, QColor(200, 200, 200))
            metin_yaz(30, 190, f"Hits: {oyuncu_istatistik['isabet']}", 14, QColor(0, 255, 0))

            # Yapay Zeka (Sağ Alt) - Dışarı taşmaması için sağa yaslı
            metin_yaz(930, 470, "AI DATA", 14, QColor(255, 255, 255), True)
            metin_yaz(930, 495, f"Shots: {yz_istatistik['toplam']}", 14, QColor(200, 200, 200), True)
            metin_yaz(930, 520, f"Hits: {yz_istatistik['isabet']}", 14, QColor(255, 50, 50), True)
            
            painter.end()
        
        self.label.setPixmap(pixmap)
        layout.addWidget(self.label)

        # 2. BUTON ALANI (Resmin dışında, en altta)
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(20, 10, 20, 10)
        
        btn_tekrar = QPushButton("RE-DEPLOY")
        btn_cikis = QPushButton("ABANDON SHIP")
        
        buton_stil = "QPushButton { background-color: #002244; color: #00CCFF; border: 2px solid #004466; font-size: 16px; font-weight: bold; min-width: 200px; padding: 10px; border-radius: 5px; } QPushButton:hover { background-color: #004466; }"
        btn_tekrar.setStyleSheet(buton_stil)
        btn_cikis.setStyleSheet(buton_stil.replace("#00CCFF", "#FF3300"))
        
        btn_tekrar.clicked.connect(lambda: self.done(QDialog.Accepted))
        btn_cikis.clicked.connect(lambda: self.done(QDialog.Rejected))
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_tekrar)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(btn_cikis)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
    #def mousePressEvent(self, event): << yapay zeka kazandığında ekranın kaynolması düzeltmesi yapıyoruz. O yüzden burası iptal. 
        #self.accept()    

class VideoPenceresi(QDialog):
    def __init__(self, video_yolu, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Credits")
        self.setFixedSize(854, 480) # 480p standart genişlik
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_widget = QVideoWidget()
        self.layout.addWidget(self.video_widget)
        
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVolume(40) # Ses seviyesi %40'a düşürüldü
        self.media_player.setVideoOutput(self.video_widget)
        
        video_url = QUrl.fromLocalFile(video_yolu)
        self.media_player.setMedia(QMediaContent(video_url))
        self.media_player.stateChanged.connect(self.kontrol_et_ve_kapat)
        
        self.media_player.play()

    def kontrol_et_ve_kapat(self, state):
        # Video durduğunda pencereyi kapat
        if state == QMediaPlayer.StoppedState:
            self.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.media_player.stop()
            self.close()
        elif event.key() == Qt.Key_Space:
            if self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.pause()
            else:
                self.media_player.play()

class DenizIzgarası(QWidget):
    
    def kalan_kare_sayisi(self):
        toplam_kare = sum(len(gemi["koordinatlar"]) for gemi in self.gemiler)
        toplam_vurus = sum(gemi["vuruş_sayısı"] for gemi in self.gemiler)
        return toplam_kare - toplam_vurus
    
    def verileri_sifirla(self):
        # Gemileri ve vuruşları temizle
        self.gemiler = []
        self.vuruslar = {}
        self.yerlestirme_modu = True
        self.guncel_gemi_indis = 0
        self.guncel_yon = "dikey"
        self.setFocusPolicy(Qt.StrongFocus) # Klavyeyi dinleme yeteneği ver
        self.setMouseTracking(True)         # Fareyi takip et
        self.fare_hucre = None              # Fare koordinatı
        
        # Okyanusu normale döndür
        normal_okyanus = os.path.join(self.assets_yolu, "ocean.gif")
        if self.ocean_movie.fileName() != normal_okyanus:
            self.ocean_movie.stop()
            self.ocean_movie.setFileName(normal_okyanus)
            self.ocean_movie.start()
        
        self.update()
    
    def __init__(self, tip="oyuncu"):
        super().__init__()
        self.tip = tip
        self.fx_durumu = True # Efektler varsayılan olarak açık (oyuncu istemezse kapatsın).
        self.ana_pencere = None
        
        # Ana dizini al ve alt klasör yolunu oluştur
        self.ana_dizin = os.path.dirname(os.path.abspath(__file__))
        self.assets_yolu = os.path.join(self.ana_dizin, "images and sounds") # klasör adını artık değiştirmeye gerek yok. 

        # --- GÖRSEL DOSYALARI (PNG) ---
        self.path_passive = os.path.join(self.assets_yolu, "passive.png") # vurulan alanı işaretlemek için. 
        self.path_shot = os.path.join(self.assets_yolu, "shot.png") # vuruk gemi resmi elcaazlarımla yaptım. 
        self.pixmap_passive = QPixmap(self.path_passive)
        self.pixmap_shot = QPixmap(self.path_shot)
        
        # --- GEMİ GÖRSELLERİ ---
        self.gemi_gorselleri = {
            "Carrier": QPixmap(os.path.join(self.assets_yolu, "ShipCarrier.png")),
            "Battleship": QPixmap(os.path.join(self.assets_yolu, "ShipBattleship.png")),
            "Cruiser": QPixmap(os.path.join(self.assets_yolu, "ShipCruiser.png")), # bunu sonradan iptal ettik fazla oluyo.
            "Destroyer": QPixmap(os.path.join(self.assets_yolu, "ShipDestroyer.png")),
            "Patrol": QPixmap(os.path.join(self.assets_yolu, "ShipPatrol.png")),
            "Submarine": QPixmap(os.path.join(self.assets_yolu, "ShipSubMarine.png")),
            "Passive": self.pixmap_passive
        }

        # --- ANİMASYON DOSYALARI (GIF / WEBP) ---
        self.ocean_movie = QMovie(os.path.join(self.assets_yolu, "ocean.gif")) # Ebemizi ağlatan aha bu. 
        self.splash_movie = QMovie(os.path.join(self.assets_yolu, "splash.gif")) # Bu ayrı bi sıkıntı zaten. 
        self.splash_red_movie = QMovie(os.path.join(self.assets_yolu, "splashred.gif")) # Bu ilerde tehlikeye düşenin okyanusu olacak.
        self.explosion_movie = QMovie(os.path.join(self.assets_yolu, "explosion.gif")) # Daha iyisini bulana kadar en iyisi bu. 
        self.target_movie = QMovie(os.path.join(self.assets_yolu, "target.gif")) # Elle yapıldı, güzel oldu bu kalsın. 
        
        # Animasyonların önbelleğe alınması ve ekran tazeleme bağlantıları
        for movie in [self.ocean_movie, self.splash_movie, self.splash_red_movie, self.explosion_movie, self.target_movie]:
            if movie.isValid():
                movie.setCacheMode(QMovie.CacheAll)
                movie.frameChanged.connect(self.update)
        
        # Okyanus animasyonunu başlat
        if self.ocean_movie.isValid():
            self.ocean_movie.start()

        self.su_an_patlıyor = False
        self.patlama_koordinat = None
        
        # --- VERİ TAKİBİ VE DONANMA ---
        self.gemiler = []
        self.vuruslar = {} # (x,y): {'isabet': bool, 'animasyon_bitti': bool}
        
        self.donanma_yapisi = [
            {"tip": "Carrier", "boyut": 5},
            {"tip": "Battleship", "boyut": 4},
            {"tip": "Submarine", "boyut": 3},
            {"tip": "Patrol", "boyut": 2},
            {"tip": "Patrol", "boyut": 2} # İkinci küçük gemi eklendi, kruvazör iptal edildi. 
        ]
        self.yerlestirme_modu = True
        self.guncel_gemi_indis = 0
        self.guncel_yon = "dikey"
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True) # Sadece bir tane yeterli
        self.fare_hucre = None 
        
        
        # --- SES AYARLARI (PYGAME) ---
        if not pygame.mixer.get_init(): # Pygame kullanıyoruz çünkü QMultimedia sıkıntılı. 
            pygame.mixer.init()

        try:
            self.sound_explosion = pygame.mixer.Sound(os.path.join(self.assets_yolu, "explosion.mp3"))
            self.sound_splash = pygame.mixer.Sound(os.path.join(self.assets_yolu, "splash.mp3"))
            self.sound_explosion.set_volume(0.2)
            self.sound_splash.set_volume(0.2)
        except Exception as e:
            print(f"Uyarı: Ses dosyaları yüklenemedi: {e}")    
    
    def check_explosion_finished(self, frame_number):
        if self.explosion_movie.frameCount() > 0:
            if frame_number >= self.explosion_movie.frameCount() - 1:
                self.explosion_movie.stop()
                self.su_an_patlıyor = False
                # Bura şimdilik böyle kalsın başka ayar gerekirse bakarız.
        

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Alanı maksimum kullanmak için marginleri sıfırlıyoruz
        genislik = self.width()
        yukseklik = self.height()
        
        # Dikey yüksekliğin %95'ini dolduracak şekilde ayar
        self.hucre_boyutu = yukseklik / 10.2 
        
        # Eğer genişlik yetmiyorsa genişliğe göre küçült (Responsiveness)
        if (self.hucre_boyutu * 10) > genislik:
            self.hucre_boyutu = genislik / 10.2

        self.offset_x = (genislik - (self.hucre_boyutu * 10)) / 2
        self.offset_y = (yukseklik - (self.hucre_boyutu * 10)) / 2

        # 1. KATMAN: Okyanus (Dinamik Ölçekleme)
        if self.ocean_movie and self.ocean_movie.isValid():
            target_rect = QRectF(self.offset_x, self.offset_y, self.hucre_boyutu * 10, self.hucre_boyutu * 10)
            current_frame = self.ocean_movie.currentPixmap()
            painter.drawPixmap(target_rect.toRect(), current_frame.scaled(target_rect.size().toSize(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

        # 2. KATMAN: Izgara (Daha askeri/siyah bir görünüm) // arkaplanın siyah olması odaklanmayı arttırır daha iyi. 
        painter.setPen(QPen(QColor(0, 0, 0, 200), 1.5))
        for i in range(11):
            painter.drawLine(int(self.offset_x), int(self.offset_y + i * self.hucre_boyutu),
                             int(self.offset_x + 10 * self.hucre_boyutu), int(self.offset_y + i * self.hucre_boyutu))
            painter.drawLine(int(self.offset_x + i * self.hucre_boyutu), int(self.offset_y),
                             int(self.offset_x + i * self.hucre_boyutu), int(self.offset_y + 10 * self.hucre_boyutu))
        
        # 2,5 KATMAN: Gemilerin Çizimi
        for gemi in self.gemiler:
            # Düşman gemilerini sadece batınca veya oyuncu tarafındaysa gösterme olayı
            # if self.tip == "dusman" and not gemi.get("batık", False):
            if self.tip == "dusman" and not gemi.get("batık", False) and not self.window().oyun_gercekten_bitti: continue
                #continue <-- şimdi burası iptal artık.  
            gx, gy = gemi["koordinatlar"][0] # Geminin başlangıç hücresi
            yon = gemi.get("yon", "yatay") # Eğer 'yon' yoksa varsayılan olarak 'yatay' al
            boyut = len(gemi["koordinatlar"])
            
            # Geminin toplam kaplayacağı alanı (dikdörtgeni) hesaplıyoruz
            if yon == "yatay":
                gemi_genislik = self.hucre_boyutu * boyut
                gemi_yukseklik = self.hucre_boyutu
            else:
                gemi_genislik = self.hucre_boyutu
                gemi_yukseklik = self.hucre_boyutu * boyut

            # Çizilecek alanı tanımla
            gemi_rect = QRectF(self.offset_x + gx * self.hucre_boyutu, 
                               self.offset_y + gy * self.hucre_boyutu, 
                               gemi_genislik, gemi_yukseklik)
            
            pix = self.gemi_gorselleri.get(gemi["tip"])
            if pix:
                # Resimler doğal halleriyle dikey olduğu için,
                # eğer gemi 'yatay' yerleştirilmişse resmi 90 derece döndür.
                if yon == "yatay":
                    transform = QTransform().rotate(90)
                    pix = pix.transformed(transform, Qt.SmoothTransformation) # burası ebemi ağlattı yalnız. 
                
                # 'Qt.IgnoreAspectRatio' yerine 'Qt.KeepAspectRatio' kullanabiliriz 
                # ama kutuyu doğru hesapladığımız için Ignore da artık bozmayacaktır.
                painter.drawPixmap(gemi_rect.toRect(), pix.scaled(
                    gemi_rect.size().toSize(), 
                    Qt.IgnoreAspectRatio, 
                    Qt.SmoothTransformation))
        
        # 2.7 KATMAN: Fare İmlecindeki Gölge Gemi (Ghost Placement)
        if self.yerlestirme_modu and self.tip == "oyuncu" and self.fare_hucre and self.guncel_gemi_indis < len(self.donanma_yapisi):
            fx, fy = self.fare_hucre
            gemi_bilgisi = self.donanma_yapisi[self.guncel_gemi_indis]
            boyut = gemi_bilgisi["boyut"]
            
            # Gölge gemi boyutlarını hesapla
            g_w = self.hucre_boyutu * (boyut if self.guncel_yon == "yatay" else 1)
            g_h = self.hucre_boyutu * (1 if self.guncel_yon == "yatay" else boyut)
            
            gemi_rect = QRectF(self.offset_x + fx * self.hucre_boyutu, 
                               self.offset_y + fy * self.hucre_boyutu, g_w, g_h)
            
            pix = self.gemi_gorselleri.get(gemi_bilgisi["tip"])
            if pix:
                painter.save() # Mevcut fırça ayarlarını kaydet
                painter.setOpacity(0.5) # %50 Opaklık <-- bu iyi kalsın böyle. 
                
                if self.guncel_yon == "yatay":
                    transform = QTransform().rotate(90)
                    pix = pix.transformed(transform, Qt.SmoothTransformation)
                
                painter.drawPixmap(gemi_rect.toRect(), pix.scaled(
                    gemi_rect.size().toSize(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
                painter.restore() # Opaklığı eski haline döndür
        

            # 3. KATMAN: Vuruşlar ve Patlamalar
        for (vx, vy), veri in list(self.vuruslar.items()):
            is_hit = veri.get('isabet', False)
            anim_bitti = veri.get('animasyon_bitti', False)
            
            target_rect = QRectF(self.offset_x + vx * self.hucre_boyutu, 
                                 self.offset_y + vy * self.hucre_boyutu, 
                                 self.hucre_boyutu, self.hucre_boyutu)

            if not anim_bitti:
                if is_hit:
                    movie = self.explosion_movie
                else:
                    # Eğer okyanus kırmızıysa splashred.gif, değilse normal splash.gif kullan
                    tehlike_yolu = os.path.join(self.assets_yolu, "oceanred.gif")
                    movie = self.splash_red_movie if self.ocean_movie.fileName() == tehlike_yolu else self.splash_movie
                current_pix = movie.currentPixmap()
                
                if not current_pix.isNull():
                    painter.drawPixmap(target_rect.toRect(), current_pix.scaled(
                        target_rect.size().toSize(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                
                # Eğer animasyon durmuşsa veya son kareye gelmişse bitti olarak işaretle
                if movie.state() == QMovie.NotRunning or movie.currentFrameNumber() >= movie.frameCount() - 1:
                    self.vuruslar[(vx, vy)]['animasyon_bitti'] = True
                    # Biter bitmez bir kez daha çizilmesi için tetikle (Hayalet görüntüyü siler)
                    self.update() 
            else:
                # Animasyon bittiği anda kalıcı resim (passive veya shot) buraya çizilir
                resim = self.pixmap_shot if is_hit else self.pixmap_passive
                painter.drawPixmap(target_rect.toRect(), resim.scaled(
                    target_rect.size().toSize(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
       
            
            # 4. KATMAN: Hedefleme İmleci (Target Cursor)
        # Sadece o hücrede şu an aktif bir atış animasyonu yoksa çiz
        if not self.yerlestirme_modu and self.fare_hucre is not None:
            # KRİTİK DEĞİŞİKLİK: 'self.tip == "dusman"' kısıtlaması varsa kaldırıldı.
            # Böylece YZ senin sahanda (tip == "oyuncu") ateş ederken de imleç görünür. // Görünmüyo işte yapay zekacım, görünmüyo. 
            is_animating = False
            if self.fare_hucre in self.vuruslar:
                if not self.vuruslar[self.fare_hucre].get('animasyon_bitti', True):
                    is_animating = True
            
            if not is_animating:
                tx, ty = self.fare_hucre
                target_rect = QRectF(self.offset_x + tx * self.hucre_boyutu, 
                                     self.offset_y + ty * self.hucre_boyutu, 
                                     self.hucre_boyutu, self.hucre_boyutu)
                
                current_target_frame = self.target_movie.currentPixmap()
                if not current_target_frame.isNull():
                    painter.drawPixmap(target_rect.toRect(), current_target_frame.scaled(
                        target_rect.size().toSize(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
    def mousePressEvent(self, event):
        self.setFocus()
        
        # 1. Koordinat hesaplamaları
        x = int((event.x() - self.offset_x) // self.hucre_boyutu)
        y = int((event.y() - self.offset_y) // self.hucre_boyutu)

        # 2. YZ ALANINA GEMİ YERLEŞTİRMEYİ ENGELLE (Yeni eklenen kısım)
        if self.tip == "dusman" and self.yerlestirme_modu:
            return

        # 3. Savaş sırasındaki tıklama mantığı
        if not self.yerlestirme_modu:
            if self.tip == "dusman" and event.button() == Qt.LeftButton:
                if 0 <= x < 10 and 0 <= y < 10:
                    ana = self.window()
                    # Sadece sıra oyuncudaysa ve daha önce vurulmamış bir yerse ateş et
                    if "PLAYER" in ana.durum_label.text() and (x, y) not in self.vuruslar:
                        isabetli, batti = self.vurus_yap(x, y)
                        
                        if not isabetli:
                            ana.durum_label.setText("Turn: AI")
                            ana.durum_label.setStyleSheet("color: #FF3300; font-weight: bold;")
                            QTimer.singleShot(1000, ana.yz_ates_et)
            return # Savaş modundaysak gemi yerleştirme kodlarına girme

        # 4. Gemi Yerleştirme Mantığı (Oyuncu alanı için)
        if event.button() == Qt.LeftButton and self.tip == "oyuncu":
            if 0 <= x < 10 and 0 <= y < 10:
                self.gemi_yerlestir(x, y)
            self.update()
            
        elif self.tip == "dusman" and event.button() == Qt.LeftButton:
            if 0 <= x < 10 and 0 <= y < 10:
                ana = self.window()
                # Sadece sıra oyuncudaysa ve daha önce vurulmamış bir yerse ateş et
                if "PLAYER" in ana.durum_label.text() and (x, y) not in self.vuruslar:
                    isabetli, batti = self.vurus_yap(x, y)
                    
                    if not isabetli:
                        ana.durum_label.setText("Turn: AI")
                        ana.durum_label.setStyleSheet("color: #FF3300; font-weight: bold;")
                        QTimer.singleShot(1000, ana.yz_ates_et)
    
    def enterEvent(self, event):
        """Fare denizin üzerine geldiğinde klavye odağını buraya al"""
        self.setFocus()
        super().enterEvent(event)
    
    def mouseMoveEvent(self, event):
        self.setFocus() # Klavyeyi bu bileşene odakla
        x = int((event.x() - self.offset_x) // self.hucre_boyutu)
        y = int((event.y() - self.offset_y) // self.hucre_boyutu)
        
        # Sadece OYUNCU denizinde ve YERLEŞTİRME modundaysak gölge gemiyi göster
        if self.yerlestirme_modu and self.tip == "oyuncu":
            if 0 <= x < 10 and 0 <= y < 10:
                self.fare_hucre = (x, y)
                self.update()
            else:
                self.fare_hucre = None
        
        # Savaş başladığında DÜŞMAN denizinde hedef imlecini göster
        elif not self.yerlestirme_modu and self.tip == "dusman":
            if 0 <= x < 10 and 0 <= y < 10:
                if (x, y) not in self.vuruslar:
                    self.fare_hucre = (x, y)
                    if self.target_movie.state() == QMovie.NotRunning:
                        self.target_movie.start()
                else:
                    self.fare_hucre = None
            else:
                self.fare_hucre = None
            self.update()
    
    def keyPressEvent(self, event):
        # Sadece gemi yerleştirme aşamasındaysak tuşları dinle
        if self.yerlestirme_modu:
            
            # R TUŞU: GEMİYİ DÖNDÜRÜR
            if event.key() == Qt.Key_R:
                # Dikey-Yatay durumları
                if self.guncel_yon == "dikey":
                    self.guncel_yon = "yatay"
                else:
                    self.guncel_yon = "dikey"
                self.update() 
            
            # Z TUŞU: SON YERLEŞTİRİLEN GEMİYİ GERİ ALIR
            elif event.key() == Qt.Key_Z:
                if len(self.gemiler) > 0:
                    self.gemiler.pop()
                    self.guncel_gemi_indis -= 1
                    
                    pencere = self.window()
                    if hasattr(pencere, 'btn_start_war'):
                        pencere.btn_start_war.setEnabled(False)
                    
                    self.update()

    
    def vurus_yapilanlar(self):
        return self.vuruslar
    
    def vurus_yap(self, x, y):
        # 1. Daha önce vuruldu mu kontrolü
        if (x, y) in self.vuruslar:
            return False, False

        isabet = False
        gemi_batti_mi = False
        for gemi in self.gemiler:
            if (x, y) in gemi["koordinatlar"]:
                isabet = True
                gemi["vuruş_sayısı"] += 1
                if gemi["vuruş_sayısı"] == len(gemi["koordinatlar"]):
                    gemi["batık"] = True
                    gemi_batti_mi = True
                break

        # 2. Vuruş kaydı (animasyon_bitti başlangıçta False)
        self.vuruslar[(x, y)] = {'isabet': isabet, 'animasyon_bitti': False}
        
        # 3. Görsel ve işitsel efekt tetikleyicileri
        self.animasyon_hucre = (x, y)
        if isabet:
            if self.fx_durumu and hasattr(self, 'sound_explosion'):
                self.sound_explosion.stop()
                self.sound_explosion.play()
            self.explosion_movie.jumpToFrame(0)
            self.explosion_movie.start()
        else:
            if self.fx_durumu and hasattr(self, 'sound_splash'):
                self.sound_splash.stop()
                self.sound_splash.play()
            
            # Kırmızı okyanus durumuna göre uygun splash seçimi
            tehlike_yolu = os.path.join(self.assets_yolu, "oceanred.gif")
            if self.ocean_movie.fileName() == tehlike_yolu:
                aktif_splash = self.splash_red_movie
            else:
                aktif_splash = self.splash_movie
            
            aktif_splash.jumpToFrame(0)
            aktif_splash.start()

        # 4. Tehlike modu ve bitiş kontrolleri
        kalan = self.kalan_kare_sayisi()
        if 0 < kalan <= 4:
            self.tehlike_moduna_gec()

        if kalan == 0:
            ana = self.window()
            if hasattr(ana, 'ambians_sustur'):
                ana.ambians_sustur()
            kazanan_taraf = "PLAYER" if self.tip == "dusman" else "AI"
            ana.oyun_gercekten_bitti = True
            QTimer.singleShot(6000, lambda: ana.oyunu_bitir(kazanan_taraf))

        # 5. Ekran güncelleme
        self.update()
        return isabet, gemi_batti_mi
                
    def tehlike_moduna_gec(self):
        tehlike_yolu = os.path.join(self.assets_yolu, "oceanred.gif")
        
        # Eğer zaten kırmızıysa tekrar işlem yapma
        if self.ocean_movie.fileName() == tehlike_yolu:
            return

        if os.path.exists(tehlike_yolu):
            self.ocean_movie.stop()
            self.ocean_movie.setFileName(tehlike_yolu)
            self.ocean_movie.start()
            
            # MÜZİK TETİKLEYİCİSİ
            ana_pencere = self.window()
            if hasattr(ana_pencere, 'muzik_degistir'):
                ana_pencere.muzik_degistir("tehlike")
                
            if hasattr(ana_pencere, 'portre_guncelle'): # Tehlikeye düşenin fotosunu panik yapıyoruz.
                ana_pencere.portre_guncelle()
            
    def gemi_yerlestir(self, x, y):
        if self.guncel_gemi_indis < len(self.donanma_yapisi):
            gemi_bilgisi = self.donanma_yapisi[self.guncel_gemi_indis]
            boyut = gemi_bilgisi["boyut"]
            yeni_koordinatlar = []
            for i in range(boyut):
                kx, ky = (x + i, y) if self.guncel_yon == "yatay" else (x, y + i)
                if 0 <= kx < 10 and 0 <= ky < 10:
                    yeni_koordinatlar.append((kx, ky))
            
            # Çakışma Kontrolü: Yeni koordinatlar mevcut gemilerin koordinatlarıyla kesişiyor mu?
        
            cakisma_var = False
            mevcut_tum_koordinatlar = [koor for g in self.gemiler for koor in g["koordinatlar"]]
            for koor in yeni_koordinatlar:
                if koor in mevcut_tum_koordinatlar:
                    cakisma_var = True
                    break

            if len(yeni_koordinatlar) == boyut and not cakisma_var:
                self.gemiler.append({
                    "tip": gemi_bilgisi["tip"],
                    "koordinatlar": yeni_koordinatlar,
                    "yon": self.guncel_yon,
                    "vuruş_sayısı": 0,
                    "batık": False
                })
                self.guncel_gemi_indis += 1
            
            # Eğer tüm gemiler yerleştiyse yerleştirme modunu kapat ve butonu aç
            if self.guncel_gemi_indis >= len(self.donanma_yapisi):
                # self.yerlestirme_modu = False  <-- Bu satırı bir önceki konuşmamıza istinaden yorum satırı yaptım/sildim //Tişkür ederim yapay zeka. 
                pencere = self.window()
                if hasattr(pencere, 'btn_start_war'):
                    pencere.btn_start_war.setEnabled(True)
                    #pencere.btn_start_war.setStyleSheet("background-color: #004466; color: #00FF00; border: 1px solid #00FF00;")
        
        self.update()
            
class AnaPencere(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ana_dizin = os.path.dirname(os.path.abspath(__file__))
        self.assets_yolu = os.path.join(self.ana_dizin, "images and sounds")
        self.setWindowTitle("Admiral Down - Modern Navy")
        ikon_yolu = os.path.join(self.assets_yolu, "admiralicon.png")
        if os.path.exists(ikon_yolu):
            self.setWindowIcon(QIcon(ikon_yolu))
        self.resize(1200, 700) 
        self.setStyleSheet("background-color: #000810; color: #00CCFF;")

        self.merkezi_widget = QWidget()
        self.setCentralWidget(self.merkezi_widget)
        
        self.ana_layout = QHBoxLayout(self.merkezi_widget)
        self.ana_layout.setContentsMargins(10, 10, 10, 10)
        self.ana_layout.setSpacing(15)

        # Sol taraf: Denizlerin olduğu yatay düzen
        self.denizler_layout = QHBoxLayout()
        self.denizler_layout.setContentsMargins(0, 10, 0, 0) # Üstten biraz boşluk
        self.denizler_layout.setSpacing(20)
        
        self.oyuncu_denizi = DenizIzgarası(tip="oyuncu")
        self.oyuncu_denizi.ana_pencere = self
        self.dusman_denizi = DenizIzgarası(tip="dusman")
        
        # --- PORTRE BÖLÜMÜ ---
        self.portre_kabı = QWidget()
        self.portre_kabı.setMaximumHeight(250) # Tavanı belirledik, fazlasını okyanusa bırakacak
        self.portre_layout = QHBoxLayout(self.portre_kabı)
        self.portre_layout.setContentsMargins(50, 5, 50, 5)
        self.portre_layout.setSpacing(20)

        # Ortak Stil Sabiti (Kod tekrarını önlemek ve yuvarlak köşeler için)
        oyuncu_stil = "border: 3px solid #00CCFF; border-radius: 15px; background: rgba(0, 20, 40, 220);"
        yz_stil = "border: 3px solid #FF3300; border-radius: 15px; background: rgba(40, 0, 0, 220);"
        metin_stili = "font-weight: bold; font-size: 12px; border: none; background: transparent; min-height: 20px;"

        # --- OYUNCU TARAFI ---
        self.oyuncu_vbox = QVBoxLayout()
        self.oyuncu_vbox = QVBoxLayout()
        self.oyuncu_vbox.setSpacing(2) # Resim ile yazı arasındaki boşluğu minimize ettik
        self.oyuncu_vbox.addStretch(0)
        self.oyuncu_vbox.setContentsMargins(0, 0, 0, 0)
        self.lbl_oyuncu_resim = QLabel()
        
        self.lbl_oyuncu_resim.setAlignment(Qt.AlignCenter)
        self.lbl_oyuncu_resim.setStyleSheet(oyuncu_stil)
        
        self.lbl_oyuncu_metin = QLabel("PLAYER")
        self.lbl_oyuncu_metin.setAlignment(Qt.AlignCenter)
        self.lbl_oyuncu_metin.setStyleSheet(metin_stili + "color: #00CCFF;")
        self.lbl_oyuncu_metin.setMinimumHeight(25) # Yazı alanı için 25 piksellik bir 'kale' kurduk
        
        self.oyuncu_vbox.addWidget(self.lbl_oyuncu_resim)
        self.oyuncu_vbox.addWidget(self.lbl_oyuncu_metin)

        # --- YAPAY ZEKA TARAFI ---
        self.yz_vbox = QVBoxLayout()
        self.yz_vbox.setSpacing(2)
        self.yz_vbox.addStretch(0)
        self.yz_vbox.setContentsMargins(0, 0, 0, 0)
        self.lbl_yz_resim = QLabel()
        
        self.lbl_yz_resim.setAlignment(Qt.AlignCenter)
        self.lbl_yz_resim.setStyleSheet(yz_stil)
        
        self.lbl_yz_metin = QLabel("GAME AI")
        self.lbl_yz_metin.setAlignment(Qt.AlignCenter)
        self.lbl_yz_metin.setStyleSheet(metin_stili + "color: #FF3300;")
        self.lbl_oyuncu_metin.setMinimumHeight(25) # Yazı alanı için 25 piksellik bir 'kale' kurduk
        
        self.yz_vbox.addWidget(self.lbl_yz_resim)
        self.yz_vbox.addWidget(self.lbl_yz_metin)

        # Layout'a ekleme
        self.portre_layout.addLayout(self.oyuncu_vbox)
        self.portre_layout.addStretch()
        self.portre_layout.addLayout(self.yz_vbox)
        
        self.denizler_layout.addWidget(self.oyuncu_denizi)

        # Dikey ayırıcı çizgi
        self.line = QFrame()
        self.line.setFrameShape(QFrame.VLine)
        self.line.setStyleSheet("background-color: #004466; max-width: 1px;")
        self.denizler_layout.addWidget(self.line)
        
        self.denizler_layout.addWidget(self.dusman_denizi)

        # Sol tarafı dikey olarak topla
        self.sol_ana_layout = QVBoxLayout()
        self.sol_ana_layout.setSpacing(10) # Portreler ve Denizler arasındaki boşluğu kaldırır
        self.sol_ana_layout.setContentsMargins(0, 0, 0, 10) # Sol bölgenin genel marjini sıfırlandı
        self.sol_ana_layout.addWidget(self.portre_kabı) 
        self.sol_ana_layout.addLayout(self.denizler_layout, 10)
        
        # Ana layout'a bu dikey yapıyı ekle
        self.ana_layout.addLayout(self.sol_ana_layout, stretch=10)
        self.sol_ana_layout.addStretch(1)
        self.denizler_layout.setContentsMargins(0, 0, 0, 0) # Denizlerin etrafındaki payı kaldır
        self.denizler_layout.setSpacing(10) # İki deniz arasındaki yatay mesafe kalsın

        # Sağ Panel: Operasyon Merkezi
        self.sag_panel_frame = QFrame()
        self.sag_panel_frame.setStyleSheet("""
            QFrame {
                background-color: #000F1A;
                border: 2px solid #004466;
                border-radius: 10px;
            }
            QLabel { color: #00CCFF; border: none; background: transparent; }
        """)
        self.sag_panel = QVBoxLayout(self.sag_panel_frame)
        
        self.bilgi_label = QLabel("COMMAND CENTER")
        self.bilgi_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.bilgi_label.setAlignment(Qt.AlignCenter)
        
        # --- RADAR GIF BÖLÜMÜ ---
        self.lbl_radar = QLabel()
        self.lbl_radar.setAlignment(Qt.AlignCenter)
        self.lbl_radar.setFixedSize(220, 220) # Sağ panel genişliğine tam oturması için
        
        # Radar dosyasını yükle (assets_yolu'nu kullandığın için hata vermez)
        radar_yolu = os.path.join(self.assets_yolu, "radar.gif")
        self.radar_movie = QMovie(radar_yolu)
        
        # GIF'i panel içinde şık durması için ölçeklendiriyoruz
        self.radar_movie.setScaledSize(QSize(180, 180))
        
        self.lbl_radar.setMovie(self.radar_movie)
        self.radar_movie.start()
        
        # DOĞRU EKLEME SIRASI:
        self.sag_panel.addWidget(self.bilgi_label) # Önce Başlık
        self.sag_panel.addWidget(self.lbl_radar)   # Sonra Radar GIF
        
        self.durum_label = QLabel("Turn: PLAYER")
        self.durum_label.setStyleSheet("color: #00FF00; font-weight: bold;")
        
        self.skor_label = QLabel("R: Rotate\nZ: Undo")
        self.oyun_gercekten_bitti = False
        
        # Buton Stilleri
        # Tüm butonlar için standartlaştırılmış modern askeri stil
        buton_stil = """
            QPushButton {
                background-color: #002244;
                color: #00CCFF;
                border: 1px solid #004466;
                min-height: 40px;
                max-height: 40px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { 
                background-color: #004466; 
                border: 1px solid #00CCFF; 
            }
            QPushButton:disabled { 
                background-color: #000810; 
                color: #003344; 
                border: 1px solid #001A26; 
            }
        """
        
        self.btn_credits = QPushButton("CREDITS")
        self.btn_ambiance = QPushButton("AMBIANCE: ON") # Yeni
        self.btn_fx = QPushButton("EFFECTS: ON")      # Yeni
        self.btn_fullscreen = QPushButton("FULLSCREEN")
        
        # Ses durumlarını takip etmek için değişkenler
        self.ambians_acik = True
        self.fx_acik = True
        self.btn_start_war = QPushButton("START BATTLE")
        self.btn_start_war.setEnabled(False) # Yerleştirme bitene kadar tıklanamaz
        self.btn_start_war.setStyleSheet(buton_stil)
        self.sag_panel.addWidget(self.btn_start_war)
        
        for btn in [self.btn_credits, self.btn_ambiance, self.btn_fx, self.btn_fullscreen]:
            btn.setStyleSheet(buton_stil)

        # Sağ panel buton yerleşimi
        self.sag_panel.addWidget(self.btn_ambiance)
        self.sag_panel.addWidget(self.btn_fx)
        self.sag_panel.addWidget(self.btn_credits) # Credits butonu buraya eklendi
        self.sag_panel.addWidget(self.btn_fullscreen)

        # Buton fonksiyonlarını bağlıyoruz
        self.btn_ambiance.clicked.connect(self.toggle_ambiance)
        self.btn_fx.clicked.connect(self.toggle_fx)
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen)
        self.btn_credits.clicked.connect(self.oynat_credits_video)
        self.btn_start_war.clicked.connect(self.savasi_onayla)

        self.sag_panel.addWidget(self.bilgi_label)
        self.sag_panel.addSpacing(15)
        self.sag_panel.addWidget(self.durum_label)
        self.sag_panel.addWidget(self.skor_label)
        self.sag_panel.addStretch()
        
        
        self.sag_panel.addWidget(self.btn_fullscreen)
        
        self.ana_layout.addWidget(self.sag_panel_frame, stretch=1)
        # Müzik ve Ses Dosyaları Tanımlama
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        self.assets_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images and sounds")

        # HER SESİ AYRI BİRER NESNE OLARAK TANIYORUZ (Manuel kontrol için)
        try:
            self.snd_hazirlik = pygame.mixer.Sound(os.path.join(self.assets_yolu, "oceanwaves.mp3"))
            self.snd_oyun_basladi = pygame.mixer.Sound(os.path.join(self.assets_yolu, "All This.mp3"))
            self.snd_tehlike = pygame.mixer.Sound(os.path.join(self.assets_yolu, "Volatile Reaction.mp3"))
            self.snd_kazandi = pygame.mixer.Sound(os.path.join(self.assets_yolu, "Take a Chance.mp3"))
            self.snd_kaybetti = pygame.mixer.Sound(os.path.join(self.assets_yolu, "Undaunted.mp3"))

            # SES SEVİYELERİNİ BURADAN MANUEL AYARLA (0.0 ile 1.0 arası)
            self.snd_hazirlik.set_volume(0.15)
            self.snd_oyun_basladi.set_volume(0.15)
            self.snd_tehlike.set_volume(0.15)
            self.snd_kazandi.set_volume(0.15)
            self.snd_kaybetti.set_volume(0.15)
            
            # Sözlük yapısını fonksiyonların çalışması için güncelliyoruz
            self.muzikler = {
                "hazirlik": self.snd_hazirlik,
                "oyun_basladi": self.snd_oyun_basladi,
                "tehlike": self.snd_tehlike,
                "kazandi": self.snd_kazandi,
                "kaybetti": self.snd_kaybetti
            }
            
            # İlk müziği başlat
            self.muzikler["hazirlik"].play(-1)
            self.yz_beyni = yz_engine.YZEngine()

        except Exception as e:
            print(f"Ses dosyası yükleme hatası: {e}")

        # Başlangıç değişkenleri ve YZ kurulumu
        self.sonuc_gosteriliyor = False
        self.yz_beyni = yz_engine.YZEngine()
        self.yz_gemilerini_yerlestir() 
            
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.btn_fullscreen.setText("FULLSCREEN")
        else:
            self.showFullScreen()
            self.btn_fullscreen.setText("MINIMIZE")
    
    def yz_gemilerini_yerlestir(self):
        import random
        deniz = self.dusman_denizi
        deniz.gemiler = [] # Önce temizle
        donanma = deniz.donanma_yapisi
        
        for gemi_bilgisi in donanma:
            yerleşti = False
            deneme_sayisi = 0
            while not yerleşti and deneme_sayisi < 100:
                deneme_sayisi += 1
                boyut = gemi_bilgisi["boyut"]
                yon = random.choice(["yatay", "dikey"])
                
                if yon == "yatay":
                    x = random.randint(0, 10 - boyut)
                    y = random.randint(0, 9)
                else:
                    x = random.randint(0, 9)
                    y = random.randint(0, 10 - boyut)
                
                yeni_koor = []
                for i in range(boyut):
                    kx, ky = (x + i, y) if yon == "yatay" else (x, y + i)
                    yeni_koor.append((kx, ky))
                
                cakisma = False
                mevcut_tum_koordinatlar = [koor for g in deniz.gemiler for koor in g["koordinatlar"]]
                for koor in yeni_koor:
                    if koor in mevcut_tum_koordinatlar:
                        cakisma = True
                        break
                
                if not cakisma:
                    deniz.gemiler.append({
                        "tip": gemi_bilgisi["tip"],
                        "koordinatlar": yeni_koor,
                        "yon": yon,
                        "vuruş_sayısı": 0,
                        "batık": False
                    })
                    yerleşti = True
        deniz.update()
    
    def savasi_onayla(self):
        # Müziği değiştir
        self.muzik_degistir("oyun_basladi")
        
        # Eğer Ambians kullanıcı tarafından KAPALI yapılmışsa, yeni müziği de hemen sustur
        if not self.ambians_acik:
            pygame.mixer.pause()

        # Yerleştirme modunu kapat
        self.dusman_denizi.yerlestirme_modu = False # Düşman üzerindeki atış yasağı kalktı
        #self.oyuncu_denizi.setMouseTracking(False)
        self.btn_start_war.setEnabled(False)
        # Butonu güncelle
        self.btn_start_war.setText("BATTLE IN PROGRESS")
        self.btn_start_war.setEnabled(False)
        #self.btn_start_war.setStyleSheet("background-color: #002244; color: #00CCFF;")
        self.skor_label.setText("Battle Status: Active\nGood Luck, Admiral!")
    
    def muzik_degistir(self, durum):
        """Oyunun durumuna göre müziği değiştirir"""
        # Eğer zaten bu durumun müziği çalıyorsa tekrar başlatma
        # (Sürekli baştan başlamasını engellemek için)
        if hasattr(self, 'mevcut_muzik_durumu') and self.mevcut_muzik_durumu == durum:
            return

        # Tüm sesleri durdur
        for ses in self.muzikler.values():
            ses.stop()

        # Yeni müziği başlat
        if durum in self.muzikler:
            self.mevcut_muzik_durumu = durum
            dongu = -1 if durum in ["hazirlik", "oyun_basladi", "tehlike"] else 0
            
            # Eğer ambiyans açıksa çal, kapalıysa sadece durumu güncelle
            if self.ambians_acik:
                self.muzikler[durum].play(dongu)
            else:
                # Ambiyans kapalıyken tehlikeye geçilirse, ses açıldığında çalması için işaretle
                pass
            
    def ambians_sustur(self):
        """Patlama efektlerini bozmadan sadece fon müziğini durdurur"""
        if hasattr(self, 'muzikler'):
            for ses in self.muzikler.values():
                ses.stop()
        self.mevcut_muzik_durumu = "sessiz"
    
    def toggle_ambiance(self):
        self.ambians_acik = not self.ambians_acik
        if self.ambians_acik:
            self.btn_ambiance.setText("AMBIANCE: ON")
            # Sadece unpause yapmak yerine, mevcut müzik durumunu yeniden tetikliyoruz
            if hasattr(self, 'mevcut_muzik_durumu'):
                durum = self.mevcut_muzik_durumu
                dongu = -1 if durum in ["hazirlik", "oyun_basladi", "tehlike"] else 0
                self.muzikler[durum].play(dongu)
        else:
            self.btn_ambiance.setText("AMBIANCE: OFF")
            # Tüm müzikleri durdur
            for ses in self.muzikler.values():
                ses.stop()

    def toggle_fx(self):
        self.fx_acik = not self.fx_acik
        self.btn_fx.setText(f"EFFECTS: {'ON' if self.fx_acik else 'OFF'}")
        
        # Izgaralara ses durumunu bildiriyoruz
        if hasattr(self, 'oyuncu_denizi'):
            self.oyuncu_denizi.fx_durumu = self.fx_acik
        if hasattr(self, 'dusman_denizi'):
            self.dusman_denizi.fx_durumu = self.fx_acik
    
    def flas_efekti_uygula(self, label, tekrar_sayisi=5, hiz=70):
        # Resmin üzerine tam oturan beyaz bir katman (overlay) oluştur
        overlay = QLabel(label)
        overlay.setStyleSheet("background-color: white;")
        overlay.setGeometry(0, 0, label.width(), label.height())
        overlay.show()

        # Bu beyaz katman için opaklık efekti
        efekt = QGraphicsOpacityEffect(overlay)
        overlay.setGraphicsEffect(efekt)
        
        grup = QSequentialAnimationGroup(overlay)
        
        # 'tekrar_sayisi' kadar döngü çalışacak
        for _ in range(tekrar_sayisi):
            # Beyazlığı belirginleştir (hiz milisaniye)
            ani_ac = QPropertyAnimation(efekt, b"opacity")
            ani_ac.setDuration(hiz)
            ani_ac.setStartValue(0.0)
            ani_ac.setEndValue(0.8)
            
            # Beyazlığı sil (hiz milisaniye)
            ani_kapat = QPropertyAnimation(efekt, b"opacity")
            ani_kapat.setDuration(hiz)
            ani_kapat.setStartValue(0.8)
            ani_kapat.setEndValue(0.0)
            
            grup.addAnimation(ani_ac)
            grup.addAnimation(ani_kapat)
            
        grup.finished.connect(overlay.deleteLater)
        grup.start(QSequentialAnimationGroup.DeleteWhenStopped)
    
    def portre_guncelle(self):
        # 1. Mevcut tehlike durumlarını tespit et
        tehlike_yolu = os.path.join(self.assets_yolu, "oceanred.gif")
        oyuncu_tehlikede = self.oyuncu_denizi.ocean_movie.fileName() == tehlike_yolu
        yz_tehlikede = self.dusman_denizi.ocean_movie.fileName() == tehlike_yolu

        # 2. Dosya yollarını belirle (Varsayılan: Normal)
        oyuncu_yeni_resim = "oyuncu.png"
        yz_yeni_resim = "yz.png"

        # 3. Senaryo Mantığı
        if oyuncu_tehlikede and yz_tehlikede:
            # Her iki taraf da tehlikedeyse ikisi de EVIL
            oyuncu_yeni_resim = "oyuncu_evil.png"
            yz_yeni_resim = "yz_evil.png"
        elif oyuncu_tehlikede:
            # Sadece oyuncu tehlikedeyse: Oyuncu PANİK, YZ EVIL
            oyuncu_yeni_resim = "oyuncu_panic.png"
            yz_yeni_resim = "yz_evil.png"
        elif yz_tehlikede:
            # Sadece YZ tehlikedeyse: YZ PANİK, Oyuncu EVIL
            oyuncu_yeni_resim = "oyuncu_evil.png"
            yz_yeni_resim = "yz_panic.png"

        # 4. Görselleri Uygula ve Flaş Çaktır
        self._portre_set_ve_flash(self.lbl_oyuncu_resim, oyuncu_yeni_resim)
        self._portre_set_ve_flash(self.lbl_yz_resim, yz_yeni_resim)

    def _portre_set_ve_flash(self, label, dosya_adi):
        yol = os.path.join(self.assets_yolu, dosya_adi)
        pix = QPixmap(yol)
        
        if not pix.isNull():
            # Pencere yüksekliğinin %20'si kadar bir boyut, ama 140-200 arası sınırlı
            boyut = max(160, min(self.height() // 4, 220))
            
            label.setFixedSize(boyut, boyut)
            
            # Resmi çerçeve içine %80 oranında, yukarı hizalı yerleştir
            resim_boyutu = int(boyut * 0.9)
            label.setPixmap(pix.scaled(resim_boyutu, resim_boyutu, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            label.setAlignment(Qt.AlignCenter)
            
            self.flas_efekti_uygula(label)

    def resizeEvent(self, event):
        # Pencere boyutu her değiştiğinde (Tam ekran dahil) portreleri yeniden boyutlandır
        self.portre_guncelle()
        super().resizeEvent(event)

    def oynat_credits_video(self):
        video_yolu = os.path.join(self.assets_yolu, "credits.mp4")
        if os.path.exists(video_yolu):
            self.credits_pencere = VideoPenceresi(video_yolu, self)
            self.credits_pencere.exec_()
        else:
            print("Hata: credits.mp4 dosyası bulunamadı!")
    
    def oyunu_bitir(self, kazanan):
        # Eğer diyalog zaten açık ise fonksiyonu anında terk et
        if hasattr(self, 'sonuc_gosteriliyor') and self.sonuc_gosteriliyor:
            return
        
        # Bayrağı hemen çek ki ikinci bir sinyal (örneğin YZ'nin son atışından gelen) sızmasın
        self.sonuc_gosteriliyor = True
        
        # Her iki denizden istatistikleri al
        oyuncu_ist = {
            "toplam": len(self.dusman_denizi.vuruslar), 
            "isabet": sum(1 for v in self.dusman_denizi.vuruslar.values() if v['isabet'])
        }
        yz_ist = {
            "toplam": len(self.oyuncu_denizi.vuruslar), 
            "isabet": sum(1 for v in self.oyuncu_denizi.vuruslar.values() if v['isabet'])
        }
        
        self.durum_label.setText(f"GAME OVER: {kazanan}")
        self.durum_label.setStyleSheet("color: #FFD700; font-weight: bold;")
        
        # Sonuç müziğini başlat
        if kazanan == "PLAYER":
            self.muzik_degistir("kazandi")
        else:
            self.muzik_degistir("kaybetti")

        # Diyaloğu oluştur ve göster
        dialog = SonucDiyalog(kazanan, oyuncu_ist, yz_ist, self.ana_dizin)
        sonuc = dialog.exec_() # Program burada kullanıcı bir butona basana kadar bekler
        
        # Kullanıcı bir seçim yaptıktan sonra bayrağı indir
        self.sonuc_gosteriliyor = False

        if sonuc == QDialog.Accepted:
            QTimer.singleShot(100, self.oyunu_sifirla)
        else:
            QApplication.quit()
    
    def yz_ates_et(self):
        # EĞER SIRA OYUNCUDA İSE VEYA SİSTEM MEŞGULSE ATES ETME
        if "PLAYER" in self.durum_label.text() or self.sonuc_gosteriliyor:
            print("DEBUG: [ENGELLEME] YZ ateş etmeye çalıştı ama sıra onda değil veya sistem meşgul!")
            return

        self.sonuc_gosteriliyor = True
        # 1. Koordinat belirle (Hata yönetimli)
        vuruslar = self.oyuncu_denizi.vuruslar
        try:
            karar = self.yz_beyni.karar_ver(vuruslar)
            if karar is None or not isinstance(karar, tuple):
                import random
                x, y = random.randint(0, 9), random.randint(0, 9)
            else:
                x, y = karar
        except Exception as e:
            print(f"YZ Karar Hatası: {e}")
            import random
            x, y = random.randint(0, 9), random.randint(0, 9)

        # Detaylı takip için
        sıra_kimde = self.durum_label.text()
        print(f"DEBUG: [YZ ATES] Koord: {x},{y} | Ekrandaki Sıra: {sıra_kimde} | Meşgul mü: {self.sonuc_gosteriliyor}")

        # 2. AKSİYONU BAŞLAT
        self.oyuncu_denizi.fare_hucre = (x, y)
        self.oyuncu_denizi.update()
        
        # 1 saniye bekle ki YZ'nin nereyi hedeflediğini görebilesin
        QTimer.singleShot(1000, lambda: self.yz_aksiyonu_tamamla(x, y))
    
    def yz_aksiyonu_tamamla(self, x, y):
        # 1. Atışı gerçekleştir
        isabetli, batti = self.oyuncu_denizi.vurus_yap(x, y)
        
        # 2. Görseli temizle
        self.oyuncu_denizi.fare_hucre = None
        self.oyuncu_denizi.update()

        # 3. Sonuç Kontrolü
        if isabetli:
            self.sonuc_gosteriliyor = False
            self.yz_beyni.isabet_bildir(x, y, batti)
            
            if self.oyuncu_denizi.kalan_kare_sayisi() == 0:
                #QTimer.singleShot(2500, lambda: self.oyunu_bitir("AI"))
                return
            
            # İSABET VARSA: Sadece isabet durumunda tekrar ateş et
            QTimer.singleShot(1000, self.yz_ates_et)
        else:
            # KARAVANA VARSA: Sırayı net bir şekilde oyuncuya devret
            # Önceki kodundaki 'self.sonuc_gosteriliyor = False' satırı BURADA OLMAMALI.
            self.durum_label.setText("Turn: PLAYER")
            self.durum_label.setStyleSheet("color: #00FF00; font-weight: bold;")
            self.sonuc_gosteriliyor = False
    
    
    def oyunu_sifirla(self):
        # 1. Denizleri güvenli şekilde temizle
        self.oyuncu_denizi.verileri_sifirla()
        self.dusman_denizi.verileri_sifirla()
        self.oyun_gercekten_bitti = False
        self.dusman_denizi.update()
        
        # 2. Portreleri orijinal haline döndür
        self.portre_guncelle()
        
        # 3. Arayüzü eski haline getir
        self.btn_start_war.setEnabled(False)
        self.btn_start_war.setText("START BATTLE")
        self.durum_label.setText("Turn: PLAYER")
        self.durum_label.setStyleSheet("color: #00FF00; font-weight: bold;")
        self.skor_label.setText("Sunk: 0\nRemaining: 5")
        
        # 4. Müziği baştan başlat
        self.mevcut_muzik_durumu = None
        self.muzik_degistir("hazirlik")
        self.yz_beyni = yz_engine.YZEngine()
        self.yz_gemilerini_yerlestir()
        self.oyuncu_denizi.setFocus()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    pencere = AnaPencere()
    pencere.show()
    sys.exit(app.exec_())
