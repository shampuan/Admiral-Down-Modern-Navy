import random

class YZEngine:
    def __init__(self):
        self.atilan_isabetli_bolgeler = []  # Vurulan ama henüz batmayan gemi parçaları
        self.hedef_listesi = []           # Bir sonraki atış için potansiyel kareler
        self.yon = None                   # 'yatay' veya 'dikey'
    
    def karar_ver(self, tum_vuruslar):
        """
        tum_vuruslar: {(x, y): {'isabet': True/False}} formatında bir sözlük.
        Bu fonksiyon (x, y) koordinatı döndürür.
        """
        if tum_vuruslar is None:
            tum_vuruslar = {}
            
        # 1. HEDEF MODU: Eğer daha önce vurulmuş ama batmamış bir yer varsa oraya odaklan
        if self.atilan_isabetli_bolgeler:
            return self.hedefli_atis(tum_vuruslar)
            
        # 2. AV MODU: Rastgele atış yap
        return self.akilli_rastgele_sec(tum_vuruslar)

    def akilli_rastgele_sec(self, tum_vuruslar):
        musait_kareler = []
        # Tüm tahtayı (10x10) tara
        for x in range(10):
            for y in range(10):
                if (x, y) not in tum_vuruslar:
                    musait_kareler.append((x, y))
        
        if musait_kareler:
            return random.choice(musait_kareler)
        else:
            return (random.randint(0, 9), random.randint(0, 9))

    def hedefli_atis(self, tum_vuruslar):
        # Yüzde 10'luk hata payı tamamen kaldırıldı.

        if len(self.atilan_isabetli_bolgeler) < 1:
            return self.akilli_rastgele_sec(tum_vuruslar)

        potansiyel = []
        
        # Eğer birden fazla isabet varsa, yönü belirle
        if len(self.atilan_isabetli_bolgeler) >= 2:
            isabetler = sorted(self.atilan_isabetli_bolgeler)
            x1, y1 = isabetler[0]
            x2, y2 = isabetler[-1]

            if x1 == x2: # Dikey hat
                for ny in [y1 - 1, y2 + 1]:
                    # SINIR KONTROLÜ: 0-9 aralığında kalmalı
                    if 0 <= ny < 10 and (x1, ny) not in tum_vuruslar:
                        potansiyel.append((x1, ny))
            elif y1 == y2: # Yatay hat
                for nx in [x1 - 1, x2 + 1]:
                    # SINIR KONTROLÜ: 0-9 aralığında kalmalı
                    if 0 <= nx < 10 and (nx, y1) not in tum_vuruslar:
                        potansiyel.append((nx, y1))

        # Eğer hat üzerinden atış yapamıyorsak veya tek isabet varsa
        if not potansiyel:
            # En son isabetin etrafını kontrol et
            x, y = self.atilan_isabetli_bolgeler[-1]
            yonler = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            # RASSAL SIRA: Sorun-1 çözümü için yönleri karıştırıyoruz
            random.shuffle(yonler) 
            
            for dx, dy in yonler:
                nx, ny = x + dx, y + dy
                # SINIR KONTROLÜ VE MÜSAİTLİK
                if 0 <= nx < 10 and 0 <= ny < 10 and (nx, ny) not in tum_vuruslar:
                    potansiyel.append((nx, ny))

        if potansiyel:
            # Orijinal yapıdaki seçimi koruyoruz (random.choice)
            return random.choice(potansiyel)
        else:
            # Çıkmaza girerse bir önceki isabet noktasına geri dönüp tekrar dene
            if self.atilan_isabetli_bolgeler:
                self.atilan_isabetli_bolgeler.pop()
                # Eğer hala isabetli bölge varsa özyinelemeli (recursive) olarak dene
                if self.atilan_isabetli_bolgeler:
                    return self.hedefli_atis(tum_vuruslar)
            
            return self.akilli_rastgele_sec(tum_vuruslar)

    def isabet_bildir(self, x, y, batti=False):
        """Ana koddan YZ'ye bilgi akışı sağlar"""
        if batti:
            self.atilan_isabetli_bolgeler = [] 
            self.yon = None
        else:
            if (x, y) not in self.atilan_isabetli_bolgeler:
                self.atilan_isabetli_bolgeler.append((x, y))
