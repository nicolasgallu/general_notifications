from sqlalchemy import create_engine, text
from google.cloud.sql.connector import Connector
import os
from dotenv import load_dotenv
load_dotenv()

INSTANCE_DB = os.getenv("INSTANCE_DB")
USER_DB = os.getenv("USER_DB")
PASSWORD_DB = os.getenv("PASSWORD_DB")
NAME_DB = os.getenv("NAME_DB")

# ======================================================
# CONEXIÓN
# ======================================================
def getconn():
    connector = Connector() 
    return connector.connect(
        INSTANCE_DB,
        "pymysql",
        user=USER_DB,
        password=PASSWORD_DB,
        db=NAME_DB,
    )   

engine = create_engine(
        "mysql+pymysql://",
        creator=getconn,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=2,
    )


def get_yesterday_performance():
    """
    Returns metrics over bot performance.
    """
    try:
        sql = text(f"""
            WITH
            agg AS (
              SELECT
                created_at,
                COUNT(question_id) AS questions,
                SUM(bool_invalid) AS invalid
              FROM zamplin_mercadolibre.ai_responses_for_analysis
              GROUP BY created_at
            )
                   
            SELECT 
              created_at as periodo,
              questions as preguntas,
              questions - invalid as respondidas,
              invalid as no_respondidas,
              round((questions - invalid)/questions,2) as share_respondidas

            FROM agg
            WHERE created_at = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
            LIMIT 1
        """)
        with engine.connect() as conn:
            result = conn.execute(sql).fetchone()._mapping
            if result:
                return result
            return None
    except Exception as e:
        print(f"Error obteniendo results: {e}")
        return None

def meli_metrics():
  data = get_yesterday_performance()
  meli_metrics = (f"""\
      MercadoLibre Metricas de Ayer
      - preguntas: {data.get('preguntas')}
      - respondidas: {data.get('respondidas')}
      - no_respondidas: {data.get('no_respondidas')}
      - share_respondidas: {str(round((data.get('share_respondidas')*100),1)) + "%"}""")
  return meli_metrics
