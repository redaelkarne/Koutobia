from fastapi import APIRouter, File, UploadFile, Query
from fastapi.responses import JSONResponse
import shutil
import re
from pathlib import Path
from app.services.cache_manager import CacheManager
from app.services.excel_reader import ExcelReader
from app.services.analysis_service import AnalysisService
from app.config import UPLOADS_DIR, EXCEL_DIR
from datetime import datetime

router = APIRouter(prefix="/api", tags=["data"])


def extract_date_from_filename(filename: str) -> str | None:
    """Extract date from filename and normalize to YYYY-MM-DD.

    Supported patterns include:
    - DD,MM,YYYY / DD-MM-YYYY / DD_MM_YYYY / DD.MM.YYYY
    - YYYY-MM-DD / YYYY_MM_DD / YYYY.MM.DD
    """
    base_name = Path(filename).stem

    # DD?MM?YYYY
    dmy_match = re.search(r"(?<!\d)(\d{2})[\s,._-](\d{2})[\s,._-](\d{4})(?!\d)", base_name)
    if dmy_match:
        day, month, year = dmy_match.groups()
        return f"{year}-{month}-{day}"

    # YYYY?MM?DD
    ymd_match = re.search(r"(?<!\d)(\d{4})[\s,._-](\d{2})[\s,._-](\d{2})(?!\d)", base_name)
    if ymd_match:
        year, month, day = ymd_match.groups()
        return f"{year}-{month}-{day}"

    return None

@router.get("/data/fiche-consommation")
async def get_fiche_consommation(
    use_cache: bool = Query(True),
    view: str = Query("general", pattern="^(general|day|month|range)$"),
    date: str | None = Query(None),
    month: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    """Get fiche consommation data"""
    try:
        data = CacheManager.get_data_by_view(
            "fiche_consommation",
            use_cache=use_cache,
            view=view,
            snapshot_date=date,
            snapshot_month=month,
            date_from=date_from,
            date_to=date_to,
        )
        return {
            "success": True,
            "data": data,
            "from_cache": use_cache,
            "view": view,
            "date": date,
            "month": month,
            "date_from": date_from,
            "date_to": date_to,
        }
    except Exception as e:
        code = 404 if "No snapshot found" in str(e) else 500
        return JSONResponse(status_code=code, content={"success": False, "error": str(e)})

@router.get("/data/calcul-viande")
async def get_calcul_viande(
    use_cache: bool = Query(True),
    view: str = Query("general", pattern="^(general|day|month|range)$"),
    date: str | None = Query(None),
    month: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    """Get calcul viande data"""
    try:
        data = CacheManager.get_data_by_view(
            "calcul_viande",
            use_cache=use_cache,
            view=view,
            snapshot_date=date,
            snapshot_month=month,
            date_from=date_from,
            date_to=date_to,
        )
        return {
            "success": True,
            "data": data,
            "from_cache": use_cache,
            "view": view,
            "date": date,
            "month": month,
            "date_from": date_from,
            "date_to": date_to,
        }
    except Exception as e:
        code = 404 if "No snapshot found" in str(e) else 500
        return JSONResponse(status_code=code, content={"success": False, "error": str(e)})

@router.get("/data/fiche-emb-ingredient")
async def get_fiche_emb_ingredient(
    use_cache: bool = Query(True),
    view: str = Query("general", pattern="^(general|day|month|range)$"),
    date: str | None = Query(None),
    month: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    """Get fiche contrôle emballage/ingrédients data."""
    try:
        data = CacheManager.get_data_by_view(
            "fiche_emb_ingredient",
            use_cache=use_cache,
            view=view,
            snapshot_date=date,
            snapshot_month=month,
            date_from=date_from,
            date_to=date_to,
        )
        return {
            "success": True,
            "data": data,
            "from_cache": use_cache,
            "view": view,
            "date": date,
            "month": month,
            "date_from": date_from,
            "date_to": date_to,
        }
    except Exception as e:
        code = 404 if "No snapshot found" in str(e) else 500
        return JSONResponse(status_code=code, content={"success": False, "error": str(e)})

@router.get("/data/fiche-appro-viande")
async def get_fiche_appro_viande(
    use_cache: bool = Query(True),
    view: str = Query("general", pattern="^(general|day|month|range)$"),
    date: str | None = Query(None),
    month: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    """Get fiche contrôle appro viande data."""
    try:
        data = CacheManager.get_data_by_view(
            "fiche_appro_viande",
            use_cache=use_cache,
            view=view,
            snapshot_date=date,
            snapshot_month=month,
            date_from=date_from,
            date_to=date_to,
        )
        return {
            "success": True,
            "data": data,
            "from_cache": use_cache,
            "view": view,
            "date": date,
            "month": month,
            "date_from": date_from,
            "date_to": date_to,
        }
    except Exception as e:
        code = 404 if "No snapshot found" in str(e) else 500
        return JSONResponse(status_code=code, content={"success": False, "error": str(e)})

@router.get("/data/emballage-synthese")
async def get_emballage_synthese(
    use_cache: bool = Query(True),
    view: str = Query("general", pattern="^(general|day|month|range)$"),
    date: str | None = Query(None),
    month: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    """Get emballage synthèse data"""
    try:
        data = CacheManager.get_data_by_view(
            "emballage_synthese",
            use_cache=use_cache,
            view=view,
            snapshot_date=date,
            snapshot_month=month,
            date_from=date_from,
            date_to=date_to,
        )
        return {
            "success": True,
            "data": data,
            "from_cache": use_cache,
            "view": view,
            "date": date,
            "month": month,
            "date_from": date_from,
            "date_to": date_to,
        }
    except Exception as e:
        code = 404 if "No snapshot found" in str(e) else 500
        return JSONResponse(status_code=code, content={"success": False, "error": str(e)})

@router.get("/data/all")
async def get_all_data(
    use_cache: bool = Query(True),
    view: str = Query("general", pattern="^(general|day|month|range)$"),
    date: str | None = Query(None),
    month: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    """Get all data from all sources"""
    try:
        data = CacheManager.get_all_data(
            use_cache=use_cache,
            view=view,
            snapshot_date=date,
            snapshot_month=month,
            date_from=date_from,
            date_to=date_to,
        )
        return {
            "success": True,
            "data": data,
            "view": view,
            "date": date,
            "month": month,
            "date_from": date_from,
            "date_to": date_to,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/data/available-dates")
async def get_available_dates():
    """List available daily snapshot dates."""
    try:
        return {
            "success": True,
            "data": CacheManager.list_available_dates(),
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@router.get("/analysis/variance")
async def get_variance_analysis(
    view: str = Query("general", pattern="^(general|day|month|range)$"),
    date: str | None = Query(None),
    month: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    """Get business analysis: real (fiche) vs theoretical (viande + emballage)."""
    try:
        all_data = CacheManager.get_all_data(
            use_cache=True,
            view=view,
            snapshot_date=date,
            snapshot_month=month,
            date_from=date_from,
            date_to=date_to,
        )
        analysis = AnalysisService.build_variance_report(all_data)
        return {
            "success": True,
            "view": view,
            "date": date,
            "month": month,
            "date_from": date_from,
            "date_to": date_to,
            "data": analysis,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/analysis/control")
async def get_control_analysis(
    view: str = Query("general", pattern="^(general|day|month|range)$"),
    date: str | None = Query(None),
    month: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    """Get control analysis: real (fiche) vs control (Contrôle Emb+Ingr, Contrôle Appro Viande)."""
    try:
        all_data = CacheManager.get_all_data(
            use_cache=True,
            view=view,
            snapshot_date=date,
            snapshot_month=month,
            date_from=date_from,
            date_to=date_to,
        )
        analysis = AnalysisService.build_control_variance_report(all_data)
        return {
            "success": True,
            "view": view,
            "date": date,
            "month": month,
            "date_from": date_from,
            "date_to": date_to,
            "data": analysis,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/upload/fiche-consommation")
async def upload_fiche_consommation(file: UploadFile = File(...)):
    """Upload new fiche consommation file"""
    try:
        snapshot_date = extract_date_from_filename(file.filename)
        if snapshot_date is None:
            return JSONResponse(status_code=400, content={
                "success": False,
                "error": "Date introuvable dans le nom du fichier. Utilisez un nom contenant une date (ex: 10-04-2026 ou 2026-04-10)."
            })

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = UPLOADS_DIR / f"{timestamp}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Always process from uploaded file first to avoid dependency on existing source file.
        data = ExcelReader.get_fiche_consommation(file_path=file_path)
        CacheManager.save_to_cache("fiche_consommation", data, snapshot_date=snapshot_date)
        emb_ing_data = ExcelReader.get_fiche_emb_ingredient(file_path=file_path)
        CacheManager.save_to_cache("fiche_emb_ingredient", emb_ing_data, snapshot_date=snapshot_date)
        appro_viande_data = ExcelReader.get_fiche_appro_viande(file_path=file_path)
        CacheManager.save_to_cache("fiche_appro_viande", appro_viande_data, snapshot_date=snapshot_date)

        # Try to synchronize the canonical source file, but do not fail the request if copy fails.
        copy_warning = None
        try:
            import shutil as sh
            EXCEL_DIR.mkdir(parents=True, exist_ok=True)
            sh.copy(file_path, EXCEL_DIR / "Fiche_Complète_Contrôle_Approvisionnement_Interne.xlsx")
        except Exception:
            copy_warning = "Synchronisation vers EXCEL_DIR impossible. Donnees traitees depuis le fichier uploade."
        
        response = {
            "success": True,
            "message": "File uploaded and processed",
            "snapshot_date": snapshot_date,
            "data": data
        }
        if copy_warning:
            response["warning"] = copy_warning
        return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/upload/calcul-viande")
async def upload_calcul_viande(file: UploadFile = File(...)):
    """Upload new calcul viande file"""
    try:
        snapshot_date = extract_date_from_filename(file.filename)
        if snapshot_date is None:
            return JSONResponse(status_code=400, content={
                "success": False,
                "error": "Date introuvable dans le nom du fichier. Utilisez un nom contenant une date (ex: 10-04-2026 ou 2026-04-10)."
            })

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = UPLOADS_DIR / f"{timestamp}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Always process from uploaded file first to avoid dependency on existing source file.
        data = ExcelReader.get_calcul_viande(file_path=file_path)
        CacheManager.save_to_cache("calcul_viande", data, snapshot_date=snapshot_date)

        # Try to synchronize the canonical source file, but do not fail the request if copy fails.
        copy_warning = None
        try:
            import shutil as sh
            EXCEL_DIR.mkdir(parents=True, exist_ok=True)
            sh.copy(file_path, EXCEL_DIR / "Calculateur_Ing_Viande 07,03,2026.xlsx")
        except Exception:
            copy_warning = "Synchronisation vers EXCEL_DIR impossible. Donnees traitees depuis le fichier uploade."
        
        response = {
            "success": True,
            "message": "File uploaded and processed",
            "snapshot_date": snapshot_date,
            "data": data
        }
        if copy_warning:
            response["warning"] = copy_warning
        return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/upload/emballage")
async def upload_emballage(file: UploadFile = File(...)):
    """Upload new emballage file"""
    try:
        snapshot_date = extract_date_from_filename(file.filename)
        if snapshot_date is None:
            return JSONResponse(status_code=400, content={
                "success": False,
                "error": "Date introuvable dans le nom du fichier. Utilisez un nom contenant une date (ex: 10-04-2026 ou 2026-04-10)."
            })

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = UPLOADS_DIR / f"{timestamp}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Always process from uploaded file first to avoid dependency on existing source file.
        data = ExcelReader.get_emballage_synthese(file_path=file_path)
        CacheManager.save_to_cache("emballage_synthese", data, snapshot_date=snapshot_date)

        # Try to synchronize the canonical source file, but do not fail the request if copy fails.
        copy_warning = None
        try:
            import shutil as sh
            EXCEL_DIR.mkdir(parents=True, exist_ok=True)
            sh.copy(file_path, EXCEL_DIR / "Calculateur_Emballage_V3.xlsx")
        except Exception:
            copy_warning = "Synchronisation vers EXCEL_DIR impossible. Donnees traitees depuis le fichier uploade."
        
        response = {
            "success": True,
            "message": "File uploaded and processed",
            "snapshot_date": snapshot_date,
            "data": data
        }
        if copy_warning:
            response["warning"] = copy_warning
        return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/refresh")
async def refresh_all():
    """Refresh all cache from Excel files"""
    try:
        CacheManager.clear_cache()
        data = CacheManager.get_all_data(use_cache=False)
        return {
            "success": True,
            "message": "All data refreshed",
            "data": data
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/cache-stats")
async def cache_stats():
    """Get cache statistics"""
    stats = CacheManager.get_cache_stats()
    return {
        "success": True,
        "stats": stats
    }

@router.delete("/cache")
async def clear_cache():
    """Clear all cache"""
    CacheManager.clear_cache()
    return {
        "success": True,
        "message": "Cache cleared"
    }
