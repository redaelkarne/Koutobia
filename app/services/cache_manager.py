import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.config import CACHE_DIR, HISTORY_DIR
from app.services.excel_reader import ExcelReader

class CacheManager:
    """Manage caching of Excel data to JSON files"""
    
    @staticmethod
    def _get_cache_file(key: str) -> Path:
        """Get cache file path for a key"""
        return CACHE_DIR / f"{key}_cache.json"

    @staticmethod
    def _get_daily_snapshot_file(key: str, snapshot_date: str) -> Path:
        """Get daily snapshot file path for a key/date."""
        key_dir = HISTORY_DIR / key
        key_dir.mkdir(parents=True, exist_ok=True)
        return key_dir / f"{snapshot_date}.json"

    @staticmethod
    def _validate_date(snapshot_date: str) -> str:
        """Validate and normalize a YYYY-MM-DD date string."""
        try:
            return datetime.strptime(snapshot_date, "%Y-%m-%d").date().isoformat()
        except ValueError as exc:
            raise ValueError("Invalid date format. Use YYYY-MM-DD") from exc

    @staticmethod
    def _validate_month(snapshot_month: str) -> str:
        """Validate and normalize a YYYY-MM month string."""
        try:
            return datetime.strptime(snapshot_month, "%Y-%m").strftime("%Y-%m")
        except ValueError as exc:
            raise ValueError("Invalid month format. Use YYYY-MM") from exc

    @staticmethod
    def _validate_date_range(date_from: str, date_to: str) -> tuple[str, str]:
        """Validate inclusive date range in YYYY-MM-DD format."""
        from_norm = CacheManager._validate_date(date_from)
        to_norm = CacheManager._validate_date(date_to)
        if from_norm > to_norm:
            raise ValueError("date_from must be <= date_to")
        return from_norm, to_norm
    
    @staticmethod
    def load_from_cache(key: str, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """Load data from JSON cache with age check"""
        cache_file = CacheManager._get_cache_file(key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Check cache age
            last_updated = datetime.fromisoformat(cached_data.get('timestamp', datetime.now().isoformat()))
            age = datetime.now() - last_updated
            
            if age > timedelta(hours=max_age_hours):
                return None  # Cache expired
            
            return cached_data
        except Exception as e:
            print(f"Error loading cache: {str(e)}")
            return None
    
    @staticmethod
    def save_to_cache(key: str, data: Dict[str, Any], snapshot_date: Optional[str] = None) -> bool:
        """Save data to JSON cache"""
        cache_file = CacheManager._get_cache_file(key)
        
        try:
            # Add timestamp
            data['timestamp'] = datetime.now().isoformat()
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            # Persist a daily snapshot only when an explicit file date is provided.
            if snapshot_date is not None:
                normalized_date = CacheManager._validate_date(snapshot_date)
                CacheManager.save_daily_snapshot(key, data, normalized_date)
            
            return True
        except Exception as e:
            print(f"Error saving cache: {str(e)}")
            return False

    @staticmethod
    def save_daily_snapshot(key: str, data: Dict[str, Any], snapshot_date: str) -> bool:
        """Save a daily snapshot for a key/date."""
        try:
            normalized_date = CacheManager._validate_date(snapshot_date)
            snapshot_file = CacheManager._get_daily_snapshot_file(key, normalized_date)

            snapshot_payload = dict(data)
            snapshot_payload["snapshot_date"] = normalized_date
            snapshot_payload["snapshot_saved_at"] = datetime.now().isoformat()

            with open(snapshot_file, "w", encoding="utf-8") as file:
                json.dump(snapshot_payload, file, ensure_ascii=False, indent=2, default=str)

            return True
        except Exception as e:
            print(f"Error saving daily snapshot: {str(e)}")
            return False

    @staticmethod
    def get_daily_snapshot(key: str, snapshot_date: str) -> Optional[Dict[str, Any]]:
        """Load a daily snapshot for a key/date if it exists."""
        try:
            normalized_date = CacheManager._validate_date(snapshot_date)
            snapshot_file = CacheManager._get_daily_snapshot_file(key, normalized_date)
            if not snapshot_file.exists():
                return None

            with open(snapshot_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return None

    @staticmethod
    def get_monthly_snapshot(key: str, snapshot_month: str) -> Optional[Dict[str, Any]]:
        """Aggregate all daily snapshots for a given month into one dataset."""
        try:
            normalized_month = CacheManager._validate_month(snapshot_month)
            key_dir = HISTORY_DIR / key
            if not key_dir.exists():
                return None

            month_files = sorted(key_dir.glob(f"{normalized_month}-*.json"))
            if not month_files:
                return None

            aggregated_rows = []
            aggregated_columns = []

            for file_path in month_files:
                with open(file_path, "r", encoding="utf-8") as file:
                    payload = json.load(file)

                snapshot_date = payload.get("snapshot_date", file_path.stem)
                rows = payload.get("data", [])
                columns = payload.get("columns", [])

                if not aggregated_columns and columns:
                    aggregated_columns = list(columns)

                for row in rows:
                    if isinstance(row, dict):
                        new_row = {"SnapshotDate": snapshot_date, **row}
                        aggregated_rows.append(new_row)

            if not aggregated_rows:
                return None

            final_columns = ["SnapshotDate", *aggregated_columns] if aggregated_columns else ["SnapshotDate"]
            return {
                "name": f"{key} monthly aggregate",
                "data": aggregated_rows,
                "columns": final_columns,
                "row_count": len(aggregated_rows),
                "snapshot_month": normalized_month,
                "days_count": len(month_files),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception:
            return None

    @staticmethod
    def get_range_snapshot(key: str, date_from: str, date_to: str) -> Optional[Dict[str, Any]]:
        """Aggregate daily snapshots between date_from and date_to (inclusive)."""
        try:
            from_norm, to_norm = CacheManager._validate_date_range(date_from, date_to)
            key_dir = HISTORY_DIR / key
            if not key_dir.exists():
                return None

            files_in_range = []
            for file_path in key_dir.glob("*.json"):
                day = file_path.stem
                if from_norm <= day <= to_norm:
                    files_in_range.append(file_path)

            files_in_range = sorted(files_in_range)
            if not files_in_range:
                return None

            aggregated_rows = []
            aggregated_columns = []

            for file_path in files_in_range:
                with open(file_path, "r", encoding="utf-8") as file:
                    payload = json.load(file)

                snapshot_date = payload.get("snapshot_date", file_path.stem)
                rows = payload.get("data", [])
                columns = payload.get("columns", [])

                if not aggregated_columns and columns:
                    aggregated_columns = list(columns)

                for row in rows:
                    if isinstance(row, dict):
                        aggregated_rows.append({"SnapshotDate": snapshot_date, **row})

            if not aggregated_rows:
                return None

            final_columns = ["SnapshotDate", *aggregated_columns] if aggregated_columns else ["SnapshotDate"]
            return {
                "name": f"{key} range aggregate",
                "data": aggregated_rows,
                "columns": final_columns,
                "row_count": len(aggregated_rows),
                "date_from": from_norm,
                "date_to": to_norm,
                "days_count": len(files_in_range),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception:
            return None

    @staticmethod
    def get_data_by_view(
        key: str,
        use_cache: bool = True,
        view: str = "general",
        snapshot_date: Optional[str] = None,
        snapshot_month: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Resolve data by view mode for a single key."""
        if view == "general":
            return CacheManager.get_data(key, use_cache=use_cache)

        if view == "day":
            target_date = snapshot_date or datetime.now().date().isoformat()
            target_date = CacheManager._validate_date(target_date)
            day_data = CacheManager.get_daily_snapshot(key, target_date)
            if day_data is None:
                raise ValueError(f"No snapshot found for {target_date}")
            return day_data

        if view == "month":
            target_month = snapshot_month or datetime.now().strftime("%Y-%m")
            target_month = CacheManager._validate_month(target_month)
            month_data = CacheManager.get_monthly_snapshot(key, target_month)
            if month_data is None:
                raise ValueError(f"No snapshot found for month {target_month}")
            return month_data

        if view == "range":
            range_from = date_from or datetime.now().date().isoformat()
            range_to = date_to or range_from
            range_from, range_to = CacheManager._validate_date_range(range_from, range_to)
            range_data = CacheManager.get_range_snapshot(key, range_from, range_to)
            if range_data is None:
                raise ValueError(f"No snapshot found between {range_from} and {range_to}")
            return range_data

        raise ValueError("view must be 'general', 'day', 'month' or 'range'")

    @staticmethod
    def list_available_dates() -> Dict[str, Any]:
        """List available snapshot dates per key and globally."""
        keys = ["fiche_consommation", "calcul_viande", "emballage_synthese"]
        result: Dict[str, Any] = {"by_key": {}, "all_dates": []}
        all_dates = set()

        for key in keys:
            key_dir = HISTORY_DIR / key
            dates = []
            if key_dir.exists():
                for file in key_dir.glob("*.json"):
                    dates.append(file.stem)

            dates = sorted(set(dates), reverse=True)
            result["by_key"][key] = dates
            all_dates.update(dates)

        result["all_dates"] = sorted(all_dates, reverse=True)
        return result
    
    @staticmethod
    def get_data(key: str, use_cache: bool = True) -> Dict[str, Any]:
        """Get data from cache or Excel"""
        if use_cache:
            cached = CacheManager.load_from_cache(key)
            if cached:
                return cached
        
        # Load from Excel
        if key == "fiche_consommation":
            data = ExcelReader.get_fiche_consommation()
        elif key == "calcul_viande":
            data = ExcelReader.get_calcul_viande()
        elif key == "emballage_synthese":
            data = ExcelReader.get_emballage_synthese()
        else:
            raise ValueError(f"Unknown data key: {key}")
        
        # Save to cache
        CacheManager.save_to_cache(key, data)
        
        return data
    
    @staticmethod
    def get_all_data(
        use_cache: bool = True,
        view: str = "general",
        snapshot_date: Optional[str] = None,
        snapshot_month: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get all data from cache/history.

        view='general' -> latest cache data
        view='day' -> daily snapshot data for snapshot_date (YYYY-MM-DD)
        view='month' -> monthly aggregate for snapshot_month (YYYY-MM)
        view='range' -> date range aggregate for date_from/date_to (YYYY-MM-DD)
        """
        if view not in {"general", "day", "month", "range"}:
            raise ValueError("view must be 'general', 'day', 'month' or 'range'")

        if view == "day":
            if snapshot_date is None:
                snapshot_date = datetime.now().date().isoformat()
            snapshot_date = CacheManager._validate_date(snapshot_date)
        if view == "month":
            if snapshot_month is None:
                snapshot_month = datetime.now().strftime("%Y-%m")
            snapshot_month = CacheManager._validate_month(snapshot_month)
        if view == "range":
            if date_from is None:
                date_from = datetime.now().date().isoformat()
            if date_to is None:
                date_to = date_from
            date_from, date_to = CacheManager._validate_date_range(date_from, date_to)

        all_data = {}

        for key in ["fiche_consommation", "calcul_viande", "emballage_synthese"]:
            try:
                all_data[key] = CacheManager.get_data_by_view(
                    key,
                    use_cache=use_cache,
                    view=view,
                    snapshot_date=snapshot_date,
                    snapshot_month=snapshot_month,
                    date_from=date_from,
                    date_to=date_to,
                )
            except Exception as e:
                all_data[key] = {"error": str(e)}

        all_data["view"] = view
        if view == "day":
            all_data["snapshot_date"] = snapshot_date
        if view == "month":
            all_data["snapshot_month"] = snapshot_month
        if view == "range":
            all_data["date_from"] = date_from
            all_data["date_to"] = date_to
        all_data['timestamp'] = datetime.now().isoformat()
        return all_data
    
    @staticmethod
    def clear_cache() -> bool:
        """Clear all cache files"""
        try:
            for cache_file in CACHE_DIR.glob("*_cache.json"):
                cache_file.unlink()
            return True
        except Exception as e:
            print(f"Error clearing cache: {str(e)}")
            return False
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "total_cache_files": 0,
            "total_size_kb": 0,
            "files": {}
        }
        
        for cache_file in CACHE_DIR.glob("*_cache.json"):
            size_kb = cache_file.stat().st_size / 1024
            stats["total_size_kb"] += size_kb
            stats["total_cache_files"] += 1
            stats["files"][cache_file.name] = {
                "size_kb": round(size_kb, 2),
                "modified": datetime.fromtimestamp(cache_file.stat().st_mtime).isoformat()
            }
        
        return stats
