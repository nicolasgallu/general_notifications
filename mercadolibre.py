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
            questions AS (
              SELECT
                q.question_id,
                -- En MySQL usamos JSON_UNQUOTE(JSON_EXTRACT(...)) o el operador ->>
                q.data->>'$.item_id' AS item_id,
                q.data->>'$.text' AS question,
                q.data->>'$.timestamp' AS created_at
              FROM zamplin_mercadolibre.questions q
            ),

            ai_responses AS (
              SELECT * FROM zamplin_mercadolibre.ai_responses
            ),

            q_category AS (
              SELECT
                t.question_id,
                t.response->>'$.model' AS model,
                t.response->>'$.timestamp' AS timestamp,
                t.response->>'$.tokens_used' AS tokens_used,
                t.response->>'$.response' AS category
              FROM ai_responses AS t
              WHERE t.stage = 'category'
            ),

            q_answer AS (
              SELECT
                t.question_id,
                t.response->>'$.model' AS model,
                t.response->>'$.timestamp' AS timestamp,
                t.response->>'$.tokens_used' AS tokens_used,
                t.response->>'$.response' AS response_text
              FROM ai_responses AS t
              WHERE t.stage = 'answer'
            ),

            q_audit AS (
              SELECT
                t.question_id,
                t.response->>'$.model' AS model,
                t.response->>'$.timestamp' AS timestamp,
                t.response->>'$.tokens_used' AS tokens_used,
                -- En MySQL se puede encadenar el operador ->> directamente
                t.response->>'$.response.valid' AS response_valid,
                t.response->>'$.response.fail_reason' AS response_fail_reason,
                t.response->>'$.response.corrected_answer' AS response_corrected_answer
              FROM ai_responses AS t
              WHERE t.stage = 'audit'
            ),

            q_fallback AS (
              SELECT
                t.question_id,
                t.response->>'$.bool_invalid' AS bool_invalid,
                t.response->>'$.reason' AS reason,
                t.response->>'$.timestamp' AS timestamp
              FROM ai_responses AS t
              WHERE t.stage = 'fallback'
            ),

            new_base AS (
              SELECT
                a.question_id,
                q.question,
                -- DATE_TRUNC(..., DAY) en MySQL es simplemente CAST(value AS DATE) o DATE(value)
                DATE(q.created_at) AS created_at,
                a.category,
                b.response_text,
                c.response_fail_reason,
                c.response_corrected_answer,
                -- INT64 a MySQL es SIGNED
                CAST(d.bool_invalid AS SIGNED) AS bool_invalid,
                d.reason
              FROM q_category AS a
              LEFT JOIN q_answer AS b ON a.question_id = b.question_id
              LEFT JOIN q_audit  AS c ON a.question_id = c.question_id
              LEFT JOIN q_fallback AS d ON a.question_id = d.question_id
              LEFT JOIN questions AS q ON a.question_id = q.question_id
            ),

            agg AS (
              SELECT
                created_at,
                COUNT(question_id) AS questions,
                SUM(bool_invalid) AS invalid
              FROM new_base
              GROUP BY created_at
            )

            -- MySQL no tiene EXCEPT, así que seleccionamos las columnas explícitamente
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
  #4. Separate variables
  meli_metrics = (f"""\
      MercadoLibre Metricas de Ayer
      - preguntas: {data.get('preguntas')}
      - respondidas: {data.get('respondidas')}
      - no_respondidas: {data.get('no_respondidas')}
      - share_respondidas: {str(round((data.get('share_respondidas')*100),1)) + "%"}""")
  return meli_metrics
