
from app import app, db
from models import AnalysisResult

def clear_all_analyses():
    """Clear all analysis records from the database"""
    with app.app_context():
        try:
            # Get count before deletion
            count = AnalysisResult.query.count()
            print(f"Found {count} analysis records in database")
            
            if count == 0:
                print("Database is already empty")
                return
            
            # Delete all records
            AnalysisResult.query.delete()
            db.session.commit()
            
            print(f"Successfully deleted all {count} analysis records")
            print("Database cleared successfully!")
            
        except Exception as e:
            print(f"Error clearing database: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    clear_all_analyses()
