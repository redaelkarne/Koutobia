from typing import Any, Dict, List, Optional


class AnalysisService:
    """Business analysis service for real vs theoretical consumption."""

    @staticmethod
    def _to_float(value: Any) -> float:
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).strip().replace('""', '').replace(',', '.')
        if text == "":
            return 0.0
        try:
            return float(text)
        except ValueError:
            return 0.0

    @staticmethod
    def _pct_gap(real_value: float, theoretical_value: float) -> float:
        if theoretical_value == 0:
            return 0.0
        return (real_value - theoretical_value) / theoretical_value * 100.0

    @staticmethod
    def _norm(text: Any) -> str:
        if text is None:
            return ""
        return str(text).strip().lower()

    @staticmethod
    def _extract_real_by_name(fiche_rows: List[Dict[str, Any]]) -> Dict[str, float]:
        result: Dict[str, float] = {}
        section = ""

        for row in fiche_rows:
            mp_value = AnalysisService._norm(row.get("MP"))
            if mp_value:
                section = mp_value

            name = str(row.get("Matière première/ingrédient/matériel d'emballage", "")).strip()
            qty = AnalysisService._to_float(row.get("Qté MP/ PF\n(Kg/L/Pcs)"))

            if not name:
                continue

            key = AnalysisService._norm(name)
            result[key] = result.get(key, 0.0) + qty

            section_key = f"section::{section}"
            result[section_key] = result.get(section_key, 0.0) + qty

        return result

    @staticmethod
    def _extract_theoretical_viande(calcul_rows: List[Dict[str, Any]]) -> Dict[str, float]:
        total_row: Optional[Dict[str, Any]] = None
        for row in calcul_rows:
            if "total" in AnalysisService._norm(row.get("N°")):
                total_row = row
                break

        if total_row is None:
            return {}

        epices_g = AnalysisService._to_float(total_row.get("🌿 Épices\n(g)"))
        return {
            "production_totale_kg": AnalysisService._to_float(total_row.get("🔢 Production\nTotale (kg)\n[épices incluses]")),
            "base_sans_epices_kg": AnalysisService._to_float(total_row.get("📐 Base\nsans épices\n(kg)")),
            "epices_kg": epices_g / 1000.0,
            "blanquette_filet_petite_viande_kg": AnalysisService._to_float(total_row.get("Blanquette/\nFilet/Petite Viande (kg)")),
            "gesier_kg": AnalysisService._to_float(total_row.get("Gésier")),
            "coeur_kg": AnalysisService._to_float(total_row.get("Cœur\n(kg)")),
            "croupion_kg": AnalysisService._to_float(total_row.get("Croupion\n(kg)")),
            "peau_kg": AnalysisService._to_float(total_row.get("Peau\n(kg)")),
            "soja_kg": AnalysisService._to_float(total_row.get("Soja\n(kg)")),
            "fecule_kg": AnalysisService._to_float(total_row.get("Fécule\n(kg)")),
            "eau_l": AnalysisService._to_float(total_row.get("Eau\n(L)")),
            "fromage_kg": AnalysisService._to_float(total_row.get("Fromage\n(kg)")),
            "chaplure_kg": AnalysisService._to_float(total_row.get("Chaplure\n(kg)")),
        }

    @staticmethod
    def _extract_theoretical_emballage(emb_rows: List[Dict[str, Any]]) -> Dict[str, float]:
        result: Dict[str, float] = {"total_general_pcs": 0.0}
        for row in emb_rows:
            name = str(row.get("Composant Emballage", "")).strip()
            number_col = str(row.get("N°", "")).strip()
            total_pcs = AnalysisService._to_float(row.get("TOTAL  (Pcs)"))

            if "total" in AnalysisService._norm(number_col):
                result["total_general_pcs"] = total_pcs
                continue

            if name:
                result[AnalysisService._norm(name)] = total_pcs

        if result["total_general_pcs"] == 0.0:
            # fallback sum if no explicit total row found
            result["total_general_pcs"] = sum(v for k, v in result.items() if k != "total_general_pcs")

        return result

    @staticmethod
    def build_variance_report(all_data: Dict[str, Any]) -> Dict[str, Any]:
        fiche = all_data.get("fiche_consommation", {})
        calcul = all_data.get("calcul_viande", {})
        emballage = all_data.get("emballage_synthese", {})

        fiche_rows = fiche.get("data", []) if isinstance(fiche, dict) else []
        calcul_rows = calcul.get("data", []) if isinstance(calcul, dict) else []
        emballage_rows = emballage.get("data", []) if isinstance(emballage, dict) else []

        real = AnalysisService._extract_real_by_name(fiche_rows)
        th_viande = AnalysisService._extract_theoretical_viande(calcul_rows)
        th_emb = AnalysisService._extract_theoretical_emballage(emballage_rows)

        real_viande_total = real.get("section::viande", 0.0)
        real_emb_total = real.get("section::emballage", 0.0)
        real_ing_total = real.get("section::ingredient", 0.0)

        meat_variances = [
            {
                "metric": "Viande totale (kg)",
                "real": round(real_viande_total, 2),
                "theoretical": round(th_viande.get("base_sans_epices_kg", 0.0), 2),
                "gap": round(real_viande_total - th_viande.get("base_sans_epices_kg", 0.0), 2),
                "gap_pct": round(AnalysisService._pct_gap(real_viande_total, th_viande.get("base_sans_epices_kg", 0.0)), 2),
            },
            {
                "metric": "Blanquette/Filet/Petite Viande (kg)",
                "real": round(real.get("blanquette de dinde désossée", 0.0) + real.get("filet de dinde", 0.0) + real.get("filet de poulet", 0.0) + real.get("petite viande", 0.0), 2),
                "theoretical": round(th_viande.get("blanquette_filet_petite_viande_kg", 0.0), 2),
                "gap": round((real.get("blanquette de dinde désossée", 0.0) + real.get("filet de dinde", 0.0) + real.get("filet de poulet", 0.0) + real.get("petite viande", 0.0)) - th_viande.get("blanquette_filet_petite_viande_kg", 0.0), 2),
                "gap_pct": round(AnalysisService._pct_gap((real.get("blanquette de dinde désossée", 0.0) + real.get("filet de dinde", 0.0) + real.get("filet de poulet", 0.0) + real.get("petite viande", 0.0)), th_viande.get("blanquette_filet_petite_viande_kg", 0.0)), 2),
            },
            {
                "metric": "Gésier (kg)",
                "real": round(real.get("gésier de dinde", 0.0), 2),
                "theoretical": round(th_viande.get("gesier_kg", 0.0), 2),
                "gap": round(real.get("gésier de dinde", 0.0) - th_viande.get("gesier_kg", 0.0), 2),
                "gap_pct": round(AnalysisService._pct_gap(real.get("gésier de dinde", 0.0), th_viande.get("gesier_kg", 0.0)), 2),
            },
            {
                "metric": "Cœur (kg)",
                "real": round(real.get("cœur de dinde", 0.0), 2),
                "theoretical": round(th_viande.get("coeur_kg", 0.0), 2),
                "gap": round(real.get("cœur de dinde", 0.0) - th_viande.get("coeur_kg", 0.0), 2),
                "gap_pct": round(AnalysisService._pct_gap(real.get("cœur de dinde", 0.0), th_viande.get("coeur_kg", 0.0)), 2),
            },
            {
                "metric": "Peau (kg)",
                "real": round(real.get("peau de dinde", 0.0), 2),
                "theoretical": round(th_viande.get("peau_kg", 0.0), 2),
                "gap": round(real.get("peau de dinde", 0.0) - th_viande.get("peau_kg", 0.0), 2),
                "gap_pct": round(AnalysisService._pct_gap(real.get("peau de dinde", 0.0), th_viande.get("peau_kg", 0.0)), 2),
            },
            {
                "metric": "Soja (kg)",
                "real": round(real.get("soja", 0.0), 2),
                "theoretical": round(th_viande.get("soja_kg", 0.0), 2),
                "gap": round(real.get("soja", 0.0) - th_viande.get("soja_kg", 0.0), 2),
                "gap_pct": round(AnalysisService._pct_gap(real.get("soja", 0.0), th_viande.get("soja_kg", 0.0)), 2),
            },
            {
                "metric": "Fécule (kg)",
                "real": round(real.get("fécule", 0.0), 2),
                "theoretical": round(th_viande.get("fecule_kg", 0.0), 2),
                "gap": round(real.get("fécule", 0.0) - th_viande.get("fecule_kg", 0.0), 2),
                "gap_pct": round(AnalysisService._pct_gap(real.get("fécule", 0.0), th_viande.get("fecule_kg", 0.0)), 2),
            },
            {
                "metric": "Fromage (kg)",
                "real": round(real.get("fromage", 0.0), 2),
                "theoretical": round(th_viande.get("fromage_kg", 0.0), 2),
                "gap": round(real.get("fromage", 0.0) - th_viande.get("fromage_kg", 0.0), 2),
                "gap_pct": round(AnalysisService._pct_gap(real.get("fromage", 0.0), th_viande.get("fromage_kg", 0.0)), 2),
            },
            {
                "metric": "Chapelure (kg)",
                "real": round(real.get("chapelure jaune", 0.0), 2),
                "theoretical": round(th_viande.get("chaplure_kg", 0.0), 2),
                "gap": round(real.get("chapelure jaune", 0.0) - th_viande.get("chaplure_kg", 0.0), 2),
                "gap_pct": round(AnalysisService._pct_gap(real.get("chapelure jaune", 0.0), th_viande.get("chaplure_kg", 0.0)), 2),
            },
        ]

        packaging_variances = [
            {
                "metric": "Sachet SV 2,5 Kg (pcs)",
                "real": round(real.get("sachet sv 2,5 kg", 0.0), 0),
                "theoretical": round(th_emb.get("sachet sv 2,5 kg", 0.0), 0),
            },
            {
                "metric": "Sachet Vrac 10 Kg (pcs)",
                "real": round(real.get("sachet vrac 10 kg", 0.0), 0),
                "theoretical": round(th_emb.get("sachet vrac 10 kg", 0.0), 0),
            },
            {
                "metric": "Barquette Ab 0,5 Kg (pcs)",
                "real": round(real.get("barquette ab 0,5 kg", 0.0), 0),
                "theoretical": round(th_emb.get("barquette ab 0,5 kg", 0.0), 0),
            },
            {
                "metric": "Barquette Sèche 0,250 Kg (pcs)",
                "real": round(real.get("barquette sèche 0,250 kg", 0.0), 0),
                "theoretical": round(th_emb.get("barquette sèche 0,250 kg", 0.0), 0),
            },
            {
                "metric": "Carton 10 Kg (pcs)",
                "real": round(real.get("carton 10 kg", 0.0), 0),
                "theoretical": round(th_emb.get("carton 10 kg", 0.0), 0),
            },
            {
                "metric": "Eti Koutoubia (pcs)",
                "real": round(real.get("eti koutoubia", 0.0), 0),
                "theoretical": round(th_emb.get("eti koutoubia", 0.0), 0),
            },
            {
                "metric": "Eti Date (pcs)",
                "real": round(real.get("eti date", 0.0), 0),
                "theoretical": round(th_emb.get("eti date", 0.0), 0),
            },
            {
                "metric": "Eti Carton (pcs)",
                "real": round(real.get("eti carton", 0.0), 0),
                "theoretical": round(th_emb.get("eti carton", 0.0), 0),
            },
        ]

        for row in packaging_variances:
            row["gap"] = round(row["real"] - row["theoretical"], 0)
            row["gap_pct"] = round(AnalysisService._pct_gap(row["real"], row["theoretical"]), 2)

        summary = {
            "real_totals": {
                "ingredient_kg": round(real_ing_total, 2),
                "viande_kg": round(real_viande_total, 2),
                "emballage_pcs": round(real_emb_total, 0),
            },
            "theoretical_totals": {
                "viande_base_kg": round(th_viande.get("base_sans_epices_kg", 0.0), 2),
                "production_totale_kg": round(th_viande.get("production_totale_kg", 0.0), 2),
                "emballage_pcs": round(th_emb.get("total_general_pcs", 0.0), 0),
            },
            "efficiency": {
                "meat_gap_kg": round(real_viande_total - th_viande.get("base_sans_epices_kg", 0.0), 2),
                "meat_gap_pct": round(AnalysisService._pct_gap(real_viande_total, th_viande.get("base_sans_epices_kg", 0.0)), 2),
                "packaging_gap_pcs": round(real_emb_total - th_emb.get("total_general_pcs", 0.0), 0),
                "packaging_gap_pct": round(AnalysisService._pct_gap(real_emb_total, th_emb.get("total_general_pcs", 0.0)), 2),
            },
        }

        # Top 5 absolute gaps for operations focus
        combined_rows = []
        for row in meat_variances:
            combined_rows.append({"type": "viande", **row, "abs_gap": abs(row["gap"])})
        for row in packaging_variances:
            combined_rows.append({"type": "emballage", **row, "abs_gap": abs(row["gap"])})

        top_gaps = sorted(combined_rows, key=lambda x: x["abs_gap"], reverse=True)[:5]

        return {
            "summary": summary,
            "meat_variances": meat_variances,
            "packaging_variances": packaging_variances,
            "top_gaps": top_gaps,
            "notes": [
                "Reel = Fiche Consommation (A5:G36)",
                "Theorique viande = Total journalier Calculateur Ing Viande",
                "Theorique emballage = Synthese Totaux (A5:F14)",
            ],
        }
