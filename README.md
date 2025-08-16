# Blockchain Voting System

Sistem e-voting berbasis blockchain menggunakan **Python** untuk memastikan transparansi, keamanan, dan keadilan dalam proses pemungutan suara.  
Setiap suara dicatat dalam block, ditandatangani secara kriptografi, dan disinkronkan antar node.  
Selain itu, sistem ini menghasilkan **receipt hash** unik untuk tiap pemilih (sebagai bukti inklusi), sehingga pemilih dapat memverifikasi bahwa suaranya tercatat tanpa membuka identitasnya.

---

## ✨ Fitur Utama
- **Keamanan**: Suara divalidasi dengan **public/private key** dan tanda tangan digital.  
- **Membership Validation**: Hanya anggota sah (dari `membership_ids.json`) yang dapat memilih.  
- **Anti-Duplikasi**: 1 anggota hanya bisa memberikan 1 suara.  
- **Filter Kandidat**: Hanya dapat memilih *Candidate A* atau *Candidate B* (payload manipulasi otomatis ditolak).  
- **Blockchain**: Vote disimpan dalam blockchain yang tidak dapat diubah.  
- **Multi-node Sync**: Chain disinkronisasi antar beberapa node untuk konsistensi data.  
- 🧾**Receipt Hash (ZKP-style)**: Setiap pemilih mendapat hash unik saat memilih, yang bisa dicatat/scan sebagai bukti bahwa suaranya benar-benar masuk ke blockchain (tanpa membuka identitas).  
