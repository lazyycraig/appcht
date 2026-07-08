import sys
import traceback
try:
    from app import app, db
    print("✓ App imported successfully")
    
    with app.app_context():
        db.create_all()
        print("✓ Database initialized")
    
    print("Starting server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
except Exception as e:
    print(f"✗ Error: {e}")
    traceback.print_exc()
    sys.exit(1)
