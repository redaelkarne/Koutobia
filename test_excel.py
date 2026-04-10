import sys
sys.path.insert(0, '.')
from app.services.excel_reader import ExcelReader

try:
    data = ExcelReader.get_fiche_consommation()
    print(f"✅ Fiche consommation loaded: {data['row_count']} rows")
    
    data = ExcelReader.get_calcul_viande()
    print(f"✅ Calcul viande loaded: {data['row_count']} rows")
    
    data = ExcelReader.get_emballage_synthese()
    print(f"✅ Emballage synthèse loaded: {data['row_count']} rows")
    
    print("\n✅ All Excel files successfully loaded!")
except Exception as e:
    print(f"❌ Error: {str(e)}")
