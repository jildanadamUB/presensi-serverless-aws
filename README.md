# Sistem Kehadiran Mahasiswa Serverless AWS

Sistem Kehadiran Mahasiswa Serverless merupakan aplikasi presensi berbasis cloud yang dibangun menggunakan layanan Amazon Web Services (AWS). Sistem ini memungkinkan dosen membuka sesi presensi secara real-time maupun terjadwal, mahasiswa melakukan presensi secara online, serta dosen melihat rekapitulasi hasil kehadiran secara otomatis.

Proyek ini dikembangkan sebagai implementasi konsep **Serverless Computing** dengan memanfaatkan AWS Lambda, Amazon DynamoDB, Amazon API Gateway, dan Amazon SNS.

---

## Fitur Utama

### Fitur Dosen

* Login ke sistem
* Membuka sesi presensi secara real-time
* Menjadwalkan sesi presensi
* Mengakhiri sesi presensi
* Melihat rekap kehadiran mahasiswa

### Fitur Mahasiswa

* Login ke sistem
* Melihat sesi presensi yang sedang aktif
* Mengisi kehadiran
* Menerima notifikasi email saat sesi presensi dibuka

---

## Teknologi yang Digunakan

| Teknologi          | Kegunaan           |
| ------------------ | ------------------ |
| HTML5              | Antarmuka pengguna |
| JavaScript         | Logika frontend    |
| AWS Lambda         | Backend serverless |
| Amazon DynamoDB    | Database NoSQL     |
| Amazon API Gateway | REST API           |
| Amazon SNS         | Notifikasi email   |
| GitHub Pages       | Hosting frontend   |

---

## Arsitektur Sistem

```text
Mahasiswa / Dosen
        │
        ▼
Frontend (HTML + JavaScript)
        │
        ▼
Amazon API Gateway
        │
 ┌──────┼──────┐
 ▼      ▼      ▼
Login  Presensi Rekap
Lambda Lambda  Lambda
        │
        ▼
 Amazon DynamoDB
        │
        ▼
 Amazon SNS
```

---

## AWS Services yang Digunakan

### AWS Lambda

Backend sistem terdiri dari beberapa fungsi Lambda:

| Function           | Deskripsi                          |
| ------------------ | ---------------------------------- |
| FungsiLogin        | Memvalidasi login pengguna         |
| FungsiBukaKelas    | Membuka dan menutup sesi presensi  |
| FungsiGetSesiAktif | Menampilkan sesi yang sedang aktif |
| FungsiIsiAbsen     | Menyimpan data presensi mahasiswa  |
| FungsiLihatHasil   | Menampilkan rekapitulasi kehadiran |

### Amazon API Gateway

Endpoint API yang tersedia:

| Endpoint      | Method | Fungsi                             |
| ------------- | ------ | ---------------------------------- |
| `/login`      | POST   | Login pengguna                     |
| `/bukakelas`  | POST   | Membuka atau menutup sesi presensi |
| `/sesiaktif`  | POST   | Mengambil sesi yang sedang aktif   |
| `/isiabsen`   | POST   | Mengirim data kehadiran mahasiswa  |
| `/lihathasil` | POST   | Menampilkan rekap presensi         |

### Amazon DynamoDB

#### Tabel Users

| Attribute | Tipe   |
| --------- | ------ |
| email     | String |
| nama      | String |
| password  | String |
| role      | String |

#### Tabel SesiKuliah

| Attribute     | Tipe                   |
| ------------- | ---------------------- |
| id_matakuliah | String (Partition Key) |
| waktu         | String (Sort Key)      |
| topik         | String                 |
| status        | String                 |
| tipe_sesi     | String                 |
| waktu_selesai | String                 |

#### Tabel Presensi

| Attribute           | Tipe   |
| ------------------- | ------ |
| email               | String |
| id_matakuliah       | String |
| topik               | String |
| keterangan_presensi | String |

### Amazon SNS

Digunakan untuk mengirim notifikasi email kepada mahasiswa ketika dosen membuka sesi presensi baru.

---

## Alur Sistem

### Dosen

1. Login ke sistem
2. Memilih mata kuliah
3. Membuka sesi presensi
4. Sistem mengirim notifikasi email melalui SNS
5. Mahasiswa melakukan presensi
6. Dosen melihat hasil rekap presensi
7. Dosen mengakhiri sesi

### Mahasiswa

1. Login ke sistem
2. Melihat sesi yang sedang aktif
3. Mengisi status kehadiran
4. Data tersimpan ke DynamoDB
