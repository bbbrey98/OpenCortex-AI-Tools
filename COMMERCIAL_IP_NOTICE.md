# 🔐 Avis de Propriété Intellectuelle & Licence Commerciale (Open-Core)
## Intellectual Property Notice & Commercial Licensing

**Titulaire exclusif / Exclusive Copyright & IP Holder :**  
**18115915 Canada Inc. (AInewgen Research Laboratories)** — Québec, Canada  
**Architecte Principal / Lead Architect :** Brandon Bujold Charlebois (Brey)  
**Référence Mathématique Certifiée / Zenodo DOI :** [10.5281/zenodo.23130667](https://doi.org/10.5281/zenodo.23130667)

---

### 1. Architecture « Open-Core » & Protection des Secrets Industriels

Ce dépôt public (**OpenCortex-AI-Tools**) publie **uniquement** :
1. Les **interfaces de démonstration visuelle** (`cortex_live_showcase.html`, `cortex_3d_robot_studio.html`, `cortex_pcb_studio.html`).
2. Les **spécifications ouvertes du protocole binaire `0xCB`** (trame de 64 octets alignée cache L1) et de la grammaire **`CORTEX-GL`** (*Gyro-Language*).
3. Le **vérificateur de télémétrie reproductible** (`verify_cortex_telemetry.py`) permettant aux juges de compétitions, auditeurs et clients B2B de vérifier mathématiquement les performances sans accès au code source du noyau.
4. Les ponts matériels périphériques ouverts (pont d'impression 3D Marlin, générateur de jeux de données synthétiques).

---

### 2. Composants Strictement Propriétaires (Fermés & Non Publiés)

Les composants suivants constituent des **secrets commerciaux et industriels exclusifs** de **18115915 Canada Inc.** et ne sont **jamais** distribués en code source :

* **Le Démon d'Orchestration Temps Réel (`cortexd`)** et le moteur **L3 Slab Engine** (`HotCrystallizableEngine`).
* **L'Indexeur Géométrique Hyperbolique (`build_poincare_index`)** et les poids synaptiques/gyrovectoriels des **166 230+ concepts** dans la boule de Poincaré $\mathbb{B}^8$.
* **Le Compilateur Binaire & Exécuteur `CORTEX-GL`** (addition/soustraction gyrovectorielle de Möbius $\oplus, \ominus$ en cache L3 CPU et cônes d'implication de Ganea).
* **Le Solveur d'Énergie Libre Géodésique SVP (`G(π)`)** haute vitesse pour l'inférence hybride Dual-GPU.

Toute tentative d'ingénierie inverse, de décompilation, d'extraction des tenseurs `.npy` d'une appliance physique, ou de reproduction commerciale non autorisée de l'architecture interne fait l'objet de poursuites civiles et pénales en vertu des lois canadiennes et internationales sur le droit d'auteur et le secret industriel.

---

### 3. Licence Commerciale — Appliance Souveraine CORTEX (B2B)

Le noyau complet **CORTEX $\mathbb{B}^8$ + CORTEX-GL + Dual-GPU Local** est commercialisé exclusivement sous forme d'**Appliance Matérielle Souveraine Clé-en-Main** (100 % locale, zéro infonuagique, Loi 25 / ITAR / Défense / Industrie) :

* **Prix de l'Appliance Souveraine :** **25 000 $ à 30 000 $ CAD** (incluant la station haute densité Ryzen 9 L3 64 Mo + Dual-GPU 28 Go VRAM + 64 Go RAM + licence perpétuelle sur site du moteur `cortexd` pré-indexé à 166 230+ compétences).
* **Intégration & Sous-traitance :** Plafond d'intégration inclus jusqu'à **2 000 $ CAD** ; tout développement sur mesure excédentaire est facturé directement au client.

📩 **Contact Commercial & Déploiement B2B :** [https://ainewgen.ca](https://ainewgen.ca)
