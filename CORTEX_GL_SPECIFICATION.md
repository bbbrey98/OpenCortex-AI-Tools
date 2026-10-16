# ⚡ Spécification Ouverte : Protocole Binaire `0xCB` (64 Octets) & Langage `CORTEX-GL`

> **Statut :** Spécification d'Interface Publique (v2.6) — *Le compilateur gyrovectoriel interne et l'indexeur L3 (166 230+ concepts) demeurent la propriété industrielle exclusive de **18115915 Canada Inc. (AInewgen)**.*

---

## 1. Pourquoi les Agents IA Classiques (JSON / ReAct / MCP) sont Trop Lents

Un agent LLM classique utilise du texte verbeux (JSON, schémas d'outils, boucles ReAct) pour exécuter une action multi-étapes :
- **Taille du contexte par requête :** `1 500 à 2 500 tokens` (~8 Ko de JSON).
- **Latence bout-en-bout :** `3 500 ms à 6 500 ms` (sérialisation HTTP + inférence autoregressive GPU).
- **Risque d'hallucination syntaxique :** Élevé (accolades manquantes, clés inventées, boucles infinies).

**CORTEX-GL (*Cortex Gyro-Language*)** remplace le texte par une **algèbre gyrovectorielle dans la boule de Poincaré $\mathbb{B}^8$**, exécutée directement dans les **64 Mo de cache L3** du processeur en **`0.32 ms à 0.78 ms`** sans solliciter le GPU pour les compétences connues.

---

## 2. Structure de la Trame Binaire `0xCB` (64 Octets — 1 Ligne de Cache CPU L1/L3)

Chaque requête ou réponse entre un périphérique (interface Web, robot CNC, pare-feu KillBlackHat) et le démon `cortexd` tient exactement dans **64 octets** (`struct` Little-Endian `<BBBBf8fIf4f`) :

```
Octets  0      1      2       3       4..7           8..39 (32 octets)         40..43    44..47    48..63 (16 octets)
+------+------+------+-------+------------+------------------------------+----------+----------+-------------------+
| 0xCB | MODE | STEP | FLAGS |  TAU (f32) |  COORDS_B8 (8 x float32)     | WIN_IDX  | DIST_H8  |  RESERVED / CRC   |
+------+------+------+-------+------------+------------------------------+----------+----------+-------------------+
  1B     1B     1B      1B        4B                  32B                     4B         4B             16B
```

| Offset | Champ | Type C / Python | Description |
| :--- | :--- | :--- | :--- |
| `0` | `MAGIC` | `uint8` (`0xCB`) | Signature magique *Cortex Binary* |
| `1` | `MODE` | `uint8` | `0x01` = Recherche géodésique, `0x02` = Cristallisation Hebbienne, `0x03` = Décomposition Möbius |
| `2` | `STEP` | `uint8` | Indice de l'étape dans une chaîne `CORTEX-GL` (`0..15`) |
| `3` | `FLAGS` | `uint8` | Bit 0 : `FAST_PATH_HIT`, Bit 1 : `ENTAILMENT_VERIFIED`, Bit 2 : `SANDBOX_EXEC` |
| `4..7` | `TAU` | `float32` | Seuil de température / rayon de confiance hyperbolique ($\tau \in [0.15, 0.85]$) |
| `8..39` | `COORDS_B8` | `float32[8]` | Coordonnée sur la variété de Poincaré $\mathbb{B}^8$ ($\|\mathbf{x}\| < 1 - 10^{-5}$) |
| `40..43` | `WIN_IDX` | `uint32` | Index primaire $O(1)$ du concept gagnant parmi les **166 230** nœuds |
| `44..47` | `DIST_H8` | `float32` | Distance géodésique effective $d_{\text{eff}}(\mathbf{q}, \mathbf{x})$ |
| `48..63` | `TELEMETRY` | `float32[4]` | Temps d'exécution ($\mu\text{s}$), norme résiduelle $\|\mathbf{q}_{\text{reste}}\|$, poids Hebbien $w_i$, CRC |

---

## 3. Grammaire Formelle de `CORTEX-GL`

Au lieu de générer du code Python ou JSON, un agent compatible `CORTEX-GL` émet des expressions algébriques compactes compilées en séquences d'opcodes de **6 octets par instruction** (`<BBHBB`) :

### Opérateurs Natifs :
* `@concept` : Résolution directe par index ou ancre sémantique dans $\mathbb{B}^8$.
* `⊕` (Addition gyrovectorielle de Möbius) : Fusionne deux intentions dans le même cône d'implication.
* `⊖` (Soustraction gyrovectorielle de Möbius) : Soustrait l'action résolue $\mathbf{x}_1$ de l'intention globale $\mathbf{q}$ pour isoler l'étape suivante $\mathbf{q}_{\text{reste}} = (-\mathbf{x}_1) \oplus \mathbf{q}$.
* `|>` (Pipeline Géodésique Séquentiel) : Enchaîne déterministement les nœuds gagnants.
* `&` (Tenseur Parallèle) : Exécution simultanée multi-cœurs / multi-GPU.
* `?tau=0.45` (Contrainte Probabiliste) : N'exécute le Fast-Path que si $d_{\text{eff}} \le \tau$, sinon bascule sur le solveur Slow-Path.
* `!` (Exécution Autonome Sandboxée) : Déclenche immédiatement le payload certifié en SQLite WAL.

### Exemple Comparatif :
**Intention :** *« Inspecter l'état des GPU, vérifier les conteneurs actifs et auditer l'espace disque NVMe »*

* **Agent JSON Classique (1 840 octets, ~4 850 ms) :** 3 appels d'outils séquentiels + 3 passes LLM.
* **Expression `CORTEX-GL` (54 octets texte $\to$ 18 octets bytecode, `0.38 ms`) :**
  ```cortex-gl
  @gpu_status |> @docker_ps |> @disk_usage ?tau=0.50 !
  ```
