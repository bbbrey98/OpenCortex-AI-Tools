# 🧠 OpenCortex AI Tools & CORTEX $\mathbb{B}^8$ Sovereign Showcase

[![IP Holder](https://img.shields.io/badge/IP_Holder-18115915_Canada_Inc._(AInewgen)-00f0ff.svg)](COMMERCIAL_IP_NOTICE.md)
[![Poincaré B8](https://img.shields.io/badge/Manifold-Poincar%C3%A9_%E2%84%99%E2%81%B8_(166%2C230_Nodes_L3)-a855f7.svg)](CORTEX_GL_SPECIFICATION.md)
[![0xCB Latency](https://img.shields.io/badge/Fast--Path_Latency-0.36_ms_(13%2C409x_Speedup)-00ffaa.svg)](verify_cortex_telemetry.py)
[![Zenodo DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23130667-blue.svg)](https://doi.org/10.5281/zenodo.23130667)
[![Sovereign Appliance](https://img.shields.io/badge/B2B_Appliance-25k%24--30k%24_CAD_Turnkey-eab308.svg)](https://ainewgen.ca)

> **L'Architecture IA Souveraine Sub-Milliseconde : Géométrie Hyperbolique de Poincaré $\mathbb{B}^8$, Langage Natif Binaire `CORTEX-GL` (Protocole `0xCB` 64 Octets) et Robotique Matérielle.**  
> *Développé par **Brandon Bujold Charlebois (Brey)** — **18115915 Canada Inc. (AInewgen Research Laboratories)**, Québec, Canada.*

---

## ⚡ Pourquoi CORTEX $\mathbb{B}^8$ Domine les Agents LLM Classiques (JSON / ReAct)

Les agents IA traditionnels (LangChain, AutoGen, MCP JSON) gaspillent **99 % de leur temps et de leurs jetons** à sérialiser du texte verbeux pour répéter des opérations déjà connues.

**CORTEX** sépare radicalement la **géométrie décisionnelle** de la génération textuelle :
1. **166 230+ concepts et compétences** sont plongés dans la boule hyperbolique de Poincaré $\mathbb{B}^8$ (`5.31 Mo` en `float32`), logeant intégralement dans les **64 Mo de cache L3** d'un processeur AMD Ryzen 9.
2. **Décomposition Séquencée par Soustraction de Möbius ($\ominus$) :** Une intention complexe multi-étapes est décomposée algébriquement en chaîne d'actions via $\mathbf{q}_{\text{reste}} = (-\mathbf{x}_1) \oplus \mathbf{q}_{\text{complexe}}$ sans jamais réveiller le LLM (*0 token consommé*).
3. **Protocole Binaire `0xCB` (64 octets) & Langage `CORTEX-GL` :** Chaque instruction est compilée en **6 octets** et transmise dans une trame de **64 octets** alignée sur une seule ligne de cache L1/L3.

| Métrique Certifiée (3 Actions Séquentielles) | Agent Cloud LLM Classique (JSON / ReAct) | Moteur Souverain **CORTEX $\mathbb{B}^8$ (`0xCB`)** | Gain Mesuré |
| :--- | :--- | :--- | :--- |
| **Latence d'Exécution Bout-en-Bout** | `4 850.0 ms` | **`0.362 ms` (362 µs)** | **× 13 409 plus rapide** |
| **Taille du Payload d'Instruction** | `4 920 octets` (~1 850 tokens JSON) | **`18 octets` Bytecode (`64B` wire frame)** | **× 273 plus compact** |
| **Coût Infonuagique & Fuite de Données** | `0,03 $ / requête` (Cloud externe) | **`0,00 $` (100 % Local / Air-Gapped)** | **Souveraineté Totale (Loi 25 / ITAR)** |

---

## 🖥️ Démos Interactives & Vérification Reproductible (Sans Dépendance Cloud)

Vous pouvez auditer et tester immédiatement les interfaces et les preuves télémétriques contenues dans ce dépôt :

1. **[`cortex_live_showcase.html`](cortex_live_showcase.html) — Comparateur Temps Réel Split-Screen & Visualiseur Poincaré $\mathbb{B}^8$ :**
   - Ouvrez directement ce fichier dans n'importe quel navigateur pour visualiser le duel de vitesse **Cloud LLM (4 850 ms) vs CORTEX `0xCB` (0.36 ms)**, l'arbre géodésique $\mathbb{B}^8$ et le **Calculateur de ROI B2B (Appliance 25k$–30k$ CAD)**.
2. **[`verify_cortex_telemetry.py`](verify_cortex_telemetry.py) — Vérificateur Mathématique de Trames `0xCB` (64 Octets) :**
   ```bash
   python3 verify_cortex_telemetry.py
   ```
   Vérifie la structure binaire `<BBBBf8fIf4f`, recalcule la distance géodésique exacte $d_{\mathbb{B}^8}(\mathbf{u}, \mathbf{v}) = 2 \operatorname{arcsinh}(\dots)$ et valide le facteur d'accélération de **13 409×**.
3. **[`CORTEX_GL_SPECIFICATION.md`](CORTEX_GL_SPECIFICATION.md) — Spécification Ouverte du Langage `CORTEX-GL` :**
   - Documentation complète de la trame binaire `0xCB` et des opérateurs gyrovectoriels (`|>`, `&`, `⊕`, `⊖`, `?tau=`, `!`).
4. **Studios Matériels & CAO/FAO Souverains :**
   - **[`cortex_pcb_studio.html`](cortex_pcb_studio.html) :** Studio de conception et routage de circuits imprimés (PCB) assisté par géométrie hyperbolique.
   - **[`cortex_3d_robot_studio.html`](cortex_3d_robot_studio.html) :** Simulateur cinématique 6-axes et contrôle robotique temps réel.
   - **[`cortex_gcode_generator.py`](cortex_gcode_generator.py) & [`imprimante_bridge.py`](imprimante_bridge.py) :** Générateur CAO paramétrique spectral ($\lambda_2$ de Fiedler) et pont matériel d'impression 3D Marlin sans cloud.

---

## 🏛️ Modèle « Open-Core » & Protection de la Propriété Intellectuelle

Conformément à notre **[Avis de Propriété Intellectuelle (`COMMERCIAL_IP_NOTICE.md`)](COMMERCIAL_IP_NOTICE.md)** :
- Les spécifications de protocole (`0xCB`), le vérificateur de télémétrie et les studios d'interface sont publiés en **accès ouvert** pour permettre l'audit scientifique et l'interopérabilité.
- Le **démon temps réel `cortexd`**, le moteur **L3 Slab Engine**, l'indexeur hyperbolique des **166 230+ concepts** et le solveur d'Énergie Libre Géodésique SVP demeurent **strictement fermés et propriétaires** sous le contrôle exclusif de **18115915 Canada Inc. (AInewgen)**.

### 💼 Acquisition de l'Appliance Souveraine CORTEX (B2B / Industrie / Défense)
Déployez votre propre tour d'intelligence souveraine **100 % hors-ligne** (Ryzen 9 64 Mo L3 + Dual-GPU 28 Go VRAM + 64 Go RAM + Moteur `cortexd` pré-indexé + Pare-feu sémantique **KillBlackHat**) :
- **Appliance Matérielle Clé-en-Main :** **25 000 $ à 30 000 $ CAD** (incluant jusqu'à **2 000 $ CAD** d'intégration sous-traitant ; développement spécifique excédentaire facturé selon cahier des charges).
- 🌐 **Portail Officiel & Démonstrations Live :** [https://ainewgen.ca](https://ainewgen.ca)
