import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add current dir to path to import database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment.")
    sys.exit(1)

def run_migration():
    print("Starting database migration...")
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        # Add new columns
        print("Adding 'purchasePrice' and 'profitMargin' columns if they don't exist...")
        conn.execute(text('ALTER TABLE produtos ADD COLUMN IF NOT EXISTS "purchasePrice" DOUBLE PRECISION;'))
        conn.execute(text('ALTER TABLE produtos ADD COLUMN IF NOT EXISTS "profitMargin" DOUBLE PRECISION;'))
        print("Adding 'visualizacoes' column if it doesn't exist...")
        conn.execute(text('ALTER TABLE produtos ADD COLUMN IF NOT EXISTS visualizacoes INTEGER DEFAULT 0;'))
        
        # Add indexes
        print("Adding 'promocional' and 'preco_promocional' columns if they don't exist...")
        conn.execute(text("ALTER TABLE produtos ADD COLUMN IF NOT EXISTS promocional BOOLEAN DEFAULT FALSE;"))
        conn.execute(text('ALTER TABLE produtos ADD COLUMN IF NOT EXISTS preco_promocional DOUBLE PRECISION;'))

        print("Creating indexes on 'ativo' and 'criado_em' if they don't exist...")
        conn.execute(text('CREATE INDEX IF NOT EXISTS ix_produtos_ativo ON produtos (ativo);'))
        conn.execute(text('CREATE INDEX IF NOT EXISTS ix_produtos_criado_em ON produtos (criado_em);'))
        
    print("Database migration completed successfully!")

if __name__ == "__main__":
    run_migration()
