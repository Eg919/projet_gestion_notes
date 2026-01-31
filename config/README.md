# Configuration des identifiants

Les identifiants de connexion sont chargés dans cet ordre :

1. **Variables d'environnement** (recommandé en production)
   - `GESTION_NOTES_USER` : nom d'utilisateur
   - `GESTION_NOTES_PASSWORD` : mot de passe

   Exemple (Windows PowerShell) :
   ```powershell
   $env:GESTION_NOTES_USER = "Admin"
   $env:GESTION_NOTES_PASSWORD = "votre_mot_de_passe"
   python main.py
   ```

   Exemple (Linux / macOS) :
   ```bash
   export GESTION_NOTES_USER=Admin
   export GESTION_NOTES_PASSWORD=votre_mot_de_passe
   python main.py
   ```

2. **Fichier protégé** `config/credentials.json` (ne pas versionner)
   - Copier `credentials.example.json` vers `credentials.json`
   - Remplir avec vos identifiants
   - S'assurer que `credentials.json` est dans `.gitignore`

   Contenu attendu :
   ```json
   {
       "username": "votre_nom_utilisateur",
       "password": "votre_mot_de_passe"
   }
   ```

3. **Valeurs par défaut** (développement uniquement : Admin / 1234) si rien n'est configuré.
