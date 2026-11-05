# Web-Desa
Web-Desa merupakan aplikasi berbasis web yang dikembangkan untuk membantu pengelolaan informasi dan pelayanan administrasi desa.

## 📌 Persyaratan

Sebelum menjalankan project, pastikan perangkat sudah memiliki:
- PHP
- Composer
- Laravel
- MySQL
- Node.js dan NPM
- Git

## 🚀 Cara Instalasi dan Menjalankan Project

### 1. Clone Repository

Buka terminal atau CMD, kemudian jalankan perintah berikut:

```bash
git clone https://github.com/Hexhub0/Web-Desa.git
```

### 2. Masuk ke Folder Project

```bash
cd Web-Desa
```

### 3. Install Dependency Laravel

```bash
composer install
```

### 4. Konfigurasi Environment

Salin file `.env.example` menjadi `.env`:

```bash
copy .env.example .env
```

### 5. Generate Application Key

```bash
php artisan key:generate
```

### 6. Konfigurasi Database

Buka file `.env`, kemudian sesuaikan konfigurasi database dengan pengaturan lokal:

```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=web_desa
DB_USERNAME=root
DB_PASSWORD=
```

Buat database dengan nama `web_desa` melalui phpMyAdmin atau MySQL.

### 7. Jalankan Migration

```bash
php artisan migrate
```

### 8. Install Dependency Frontend

```bash
npm install
```

### 9. Jalankan Project

Jalankan perintah berikut:

```bash
npm run dev
```

Buka terminal baru, kemudian jalankan:

```bash
php artisan serve
```

### 10. Buka Aplikasi

Akses aplikasi melalui browser:

```text
http://127.0.0.1:8000
```

## 👥 Kontributor

Project ini dikembangkan secara berkelompok sebagai bagian dari tugas perkuliahan.
