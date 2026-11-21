# Engineering Conference Program

Üç günlük bir mühendislik konferansu için Türkçe ve İngilizce kullanılabilen, mobil uyumlu bir program arayüzü tasarımı. Tasarımda, üç farklı gün ve dört paralel salon oturumu görüntülenebilmekte, bildirilerin üzerine tıklanarak detaylarına (özetlerine) erişilebilmektedir. Uygulama tek bir `index.html` dosyasıyla çalışabilmektedir.

## Önizleme

![Konferans programının genel görünümü](assets/overview.jpg)

## Kullanım demosu

Animasyon; günler arasındaki geçişleri, bildiri özetinin açılıp kapanmasını ve sayfanın İngilizce görünümünü göstermektedir.

![Gün seçimi ve bildiri özetlerinin açılması](assets/demo.gif)

## Özellikler

- Türkçe varsayılan görünüm ve TR / EN dil seçimi.
- Üç gün arasında geçiş, dört paralel salon ve 108 örnek bildiri.
- Başlığın altında açılan Türkçe ve İngilizce özetler.
- Bildiri kutularında yazar adları; birden fazla yazar arasında `·` ayırıcı.
- Günün programında başlık ve yazar araması.
- Seçili günü yazdırma veya tarayıcının yazdırma ekranından PDF olarak kaydetme.
- Küçük ekranlarda yatay kaydırılabilen program tablosu.
- JavaScript çalışmasa da kullanılabilen gün/dil seçimi, tablolar ve özet açılışları.
- İnternet bağlantısı gerektirmeyen gömülü yazı tipleri ve logo.

## Bilgisayarda çalıştırma

1. Repoyu indirin veya klonlayın.
2. `index.html` dosyasını Chrome, Edge, Firefox veya Safari gibi bir tarayıcıyla açın.

## Bildirileri düzenleme

VS Code’da `index.html` dosyasını açıp **BİLDİRİLERİ BURADAN DÜZENLEYİN** ifadesini arattırın. `program-data` bölümündeki her bildiri ayrı bir kayıttır ve şu şekilde tasarlanmıştır:

```json
{
  "id": "d1-B11",
  "tr": "Türkçe bildiri başlığı",
  "en": "English paper title",
  "authors": [
    "Ayşe Yılmaz",
    "Mehmet Demir"
  ],
  "abstract": {
    "tr": "Türkçe özet metni.",
    "en": "English abstract text."
  }
}
```

Bu örnek ilgili alanları gösterir; mevcut kaydı düzenlerken diğer alanları ve JSON yapısını koruyun. Metin içindeki çift tırnakları `\"` olarak yazın.

Normal tarayıcı kullanımında program verileri açılışta yeniden işlenir. JavaScript çalıştırmayan görüntüleyiciler için dosyanın içinde ayrıca hazır tablolar bulunur. Veri değişikliklerinden sonra bu tabloları da güncellemek için repo klasöründe çalıştırın:

```bash
python tools/sync_program.py
```

Windows’ta Python başlatıcısı kullanılıyorsa:

```powershell
py tools/sync_program.py
```

Yalnızca kontrol yapmak için:

```bash
python tools/sync_program.py --check
```

Yardımcı betik Python 3.9 veya üzerini ve yalnızca standart kütüphaneyi kullanır. Uygulamayı görüntülemek için Python gerekmez. Betik; JSON yapısını, özet uzunluklarını ve aynı gün saat aralıkları çakışan farklı salonlardaki ortak yazarları denetler. Bir çakışma bulursa yazarları otomatik değiştirmek yerine hatayı bildirir.

## Dosyalar

| Dosya | Amaç |
| --- | --- |
| `index.html` | Uygulama, program verileri, stiller, etkileşimler, gömülü fontlar ve logo |
| `README.md` | Tanıtım, kurulum ve düzenleme açıklamaları |
| `assets/overview.jpg` | Genel ekran görüntüsü |
| `assets/demo.gif` | Gün/dil değişimi ve özet açılışlarının animasyonu |
| `tools/sync_program.py` | Veri kontrolü ve JavaScript’siz tabloların güncellenmesi |
| `description.txt` | GitHub repo açıklaması için kopyalanabilir metin |

## Teknoloji ve örnek içerik

HTML, CSS ve JavaScript kullanılmıştır. Başlıklarda Bricolage Grotesque, metinlerde Figtree tercih edilmiştir; font lisans metinleri HTML içinde mevcuttur.

Bildiri başlıkları, yazar isimleri ve özetler arayüzü göstermek için oluşturulmuş örnek içeriklerdir. Gerçek bir konferans programını veya tamamlanmış araştırma sonuçlarını temsil etmez. Örneğin iletişim adresi `program@example.com` örnek bir adrestir. Aynı şekilde bildiriler ve özetleri de yine YZ tarafından oluşturulmuştur. Üç günlük bir konferans tasarımı bu HTML aracılığı ile örneklendirilmeye çalışılmıştır.
