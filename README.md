# 📄 CV Builder Bot

**Telegram Bot** yang membantu pengguna membuat Curriculum Vitae (CV) profesional langsung melalui chat, lalu menghasilkan file **PDF modern** siap digunakan untuk melamar pekerjaan.

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![python-telegram-bot](https://img.shields.io/badge/PTB-v22+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Deploy](https://img.shields.io/badge/Deploy-Vercel-black?logo=vercel)

---

## ✨ Fitur Utama

- **Percakapan terpandu** – pengumpulan data langkah demi langkah
- **Validasi otomatis** email & nomor telepon
- **Multi-entry** untuk Pendidikan, Pengalaman, Sertifikat, Prestasi
- **Skill & Bahasa** (input multi-value)
- **Upload foto profil** (opsional) dengan auto-crop & resize
- **4 Template CV** profesional:
  - 🎨 Modern
  - 💼 Professional
  - ✨ Creative
  - 📄 ATS Friendly
- **Preview ringkasan** sebelum generate
- **PDF berkualitas tinggi** (ReportLab) – tajam, layout rapi, file kecil
- **Privasi** – tanpa database, tanpa login, data sementara dihapus otomatis setelah PDF dibuat
- **Webhook-only** – siap deploy ke Vercel
- **Error handling & logging** sederhana

---

## 📸 Screenshot (Placeholder)

> Ganti gambar di bawah dengan screenshot nyata dari bot kamu.

```
[Screenshot: Welcome message & menu]
[Screenshot: Conversation flow]
[Screenshot: PDF Preview / generated CV]
```

---

## 🛠 Teknologi

| Komponen              | Teknologi                          |
|-----------------------|------------------------------------|
| Runtime               | Python 3.12+                       |
| Telegram Framework    | python-telegram-bot v22+           |
| PDF Generation        | ReportLab                          |
| Image Processing      | Pillow                             |
| Web Server (webhook)  | Starlette + Uvicorn                |
| Deployment            | Vercel (Serverless)                |
| Config                | python-dotenv                      |

---

## 📁 Struktur Project

```
cv-builder-bot/
├── api/
│   └── webhook.py          # Vercel entrypoint (ASGI)
├── bot/
│   ├── __init__.py
│   ├── config.py           # Constants, states, colors
│   ├── conversation.py     # ConversationHandler
│   ├── handlers.py         # All message & callback handlers
│   ├── helpers.py          # Utilities & summary builder
│   ├── keyboards.py        # Inline keyboards
│   ├── pdf_generator.py    # Professional PDF builder
│   ├── templates.py        # Template metadata
│   └── validators.py       # Email, phone, year, etc.
├── assets/
│   ├── icons/
│   ├── fonts/
│   └── templates/
├── requirements.txt
├── vercel.json
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Instalasi Lokal

### 1. Clone repository

```bash
git clone https://github.com/yourusername/cv-builder-bot.git
cd cv-builder-bot
```

### 2. Buat virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# .venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Konfigurasi environment

```bash
cp .env.example .env
```

Isi `.env`:

```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
WEBHOOK_SECRET=random_long_secret_string
WEBHOOK_URL=https://your-app.vercel.app
```

> Dapatkan token dari [@BotFather](https://t.me/BotFather).

### 5. Testing lokal (polling – development only)

Untuk development, kamu bisa menambahkan script polling sederhana.  
Project ini **dirancang untuk webhook**. Untuk test cepat, gunakan:

```bash
# Install ngrok atau cloudflared, lalu expose port lokal
# Setelah deploy ke Vercel, gunakan endpoint /set-webhook
```

---

## ☁️ Deploy ke Vercel

### 1. Push ke GitHub

```bash
git add .
git commit -m "Initial CV Builder Bot"
git push origin main
```

### 2. Import project di Vercel

1. Buka [vercel.com](https://vercel.com) → **Add New Project**
2. Import repository GitHub kamu
3. Framework Preset: **Other**
4. Root Directory: `.` (default)
5. Tambahkan **Environment Variables**:
   - `TELEGRAM_BOT_TOKEN`
   - `WEBHOOK_SECRET`
   - `WEBHOOK_URL` → `https://<nama-project>.vercel.app`

### 3. Deploy

Klik **Deploy**. Setelah selesai, catat URL deployment.

### 4. Set Webhook Telegram

Buka di browser (atau curl):

```
https://<nama-project>.vercel.app/set-webhook
```

Response harus berisi `"set_webhook": true`.

Atau secara manual:

```bash
curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://<nama-project>.vercel.app/&secret_token=<WEBHOOK_SECRET>"
```

### 5. Test

Buka bot di Telegram → kirim `/start`.

---

## 🔧 Environment Variables

| Variable             | Wajib | Deskripsi                                      |
|----------------------|-------|------------------------------------------------|
| `TELEGRAM_BOT_TOKEN` | Ya    | Token dari @BotFather                          |
| `WEBHOOK_SECRET`     | Ya    | Secret token untuk validasi header webhook     |
| `WEBHOOK_URL`        | Ya    | Base URL deployment (tanpa trailing slash)     |

---

## 📋 Alur Penggunaan Bot

1. `/start` → Menu utama
2. **Buat CV Baru**
3. Isi data pribadi (nama, posisi, kontak, tentang saya)
4. Pendidikan (bisa lebih dari satu)
5. Pengalaman kerja (bisa lebih dari satu)
6. Skill & Bahasa
7. Sertifikat & Prestasi (opsional)
8. Link (GitHub, LinkedIn, Portfolio, dll.)
9. Foto profil (opsional)
10. Pilih template
11. Review ringkasan → **Generate PDF**
12. Terima file PDF & data otomatis dihapus

---

## 🎨 Desain PDF

- Layout A4 profesional
- Header dengan nama menonjol + foto (jika ada)
- Section header dengan accent line
- Skill ditampilkan sebagai chip / separator modern
- Urutan pengalaman & pendidikan dari yang terbaru
- Warna: Navy Blue, Dark Gray, White
- Font: Helvetica family (standar ReportLab – clean & readable)
- Multi-page otomatis jika konten panjang
- Ukuran file kecil, tajam saat dicetak

---

## 🔒 Privasi

- **Tidak ada database**
- **Tidak ada login / akun**
- Semua data disimpan hanya di `context.user_data` (memory)
- Setelah PDF berhasil dikirim, data dihapus dengan `clear_user_data()`
- Foto hanya diproses di memory (Pillow) lalu dibuang

---

## 🧪 Development Notes

- Clean Architecture: setiap fitur dipisah ke modul sendiri
- Type hints di hampir semua fungsi
- Asynchronous (python-telegram-bot v22+)
- ConversationHandler dengan state machine yang jelas
- Logging sederhana via `logging` module

---

## 📄 License

MIT License – lihat file [LICENSE](LICENSE).

---

## 🤝 Kontribusi

Pull request sangat diterima! Untuk perubahan besar, buka issue terlebih dahulu.

---

## 📞 Support

Jika menemukan bug atau punya ide fitur, buat Issue di repository ini.

---

**Dibuat dengan ❤️ untuk membantu job seeker membuat CV lebih cepat dan profesional.**
