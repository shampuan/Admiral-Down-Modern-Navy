#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap

# Linux/Debian tabanlı sistemler için X11 zorlaması
os.environ["QT_QPA_PLATFORM"] = "xcb"

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        
        # 1. Çerçevesiz pencere ve her zaman üstte kalma ayarı
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 2. Düzen ve Görsel Yükleme
        layout = QVBoxLayout(self)
        self.label = QLabel()
        
        # Resim yolunu belirle (Dosya amiral.py ile aynı dizinde olmalı)
        ana_dizin = os.path.dirname(os.path.abspath(__file__))
        resim_yolu = os.path.join(ana_dizin, "images and sounds", "splashscreen.png")
        
        pixmap = QPixmap(resim_yolu)
        if not pixmap.isNull():
            self.label.setPixmap(pixmap)
            self.setFixedSize(pixmap.size())
        else:
            # Resim bulunamazsa hata vermemesi için geçici bir boyut
            self.label.setText("YÜKLENİYOR...")
            self.label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
            self.setFixedSize(400, 200)

        layout.addWidget(self.label)
        self.setLayout(layout)

        # 3. Ekranın tam ortasına konumlandır
        self.merkeze_al()

        # 4. Ana oyunu arka planda başlat
        # subprocess.Popen kullanarak amiral.py'yi gamestart'ı kilitlemeden açıyoruz
        try:
            ana_dizin = os.path.dirname(os.path.abspath(__file__))
            amiral_yolu = os.path.join(ana_dizin, "amiral.py")
            subprocess.Popen([sys.executable, amiral_yolu])
        except Exception as e:
            print(f"Oyun başlatılamadı: {e}")

        # 5. 4 saniye sonra splash ekranını kapat ve uygulamadan çık
        QTimer.singleShot(4000, self.kapat_ve_cik)

    def merkeze_al(self):
        # Ekran geometrisini alıp pencereyi tam ortaya taşır
        frame_gm = self.frameGeometry()
        center_point = QApplication.desktop().availableGeometry().center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())

    def kapat_ve_cik(self):
        self.close()
        sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Splash ekranını göster
    splash = SplashScreen()
    splash.show()
    
    sys.exit(app.exec_())
