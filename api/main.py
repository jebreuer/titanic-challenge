from fastapi import FastAPI, HTTPException, Request
import sqlite3
from auth import router as auth_router
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Initialize tracing
trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger-collector.istio-system:4317")
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])

FastAPIInstrumentor.instrument_app(app)

DATABASE = "./titanic.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Add middleware to log request ID from Istio
@app.middleware("http")
async def add_request_id_header(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get("x-request-id")
    if request_id:
        response.headers["x-request-id"] = request_id
    return response

@app.get("/schema")
def get_schema():
    conn = get_db_connection()
    # Get all tables
    tables = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table'
    """).fetchall()
    
    schema = {}
    for table in tables:
        table_name = table['name']
        # Get column info for each table
        columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        schema[table_name] = [
            {
                "name": col['name'],
                "type": col['type'],
                "notnull": col['notnull'],
                "pk": col['pk']
            }
            for col in columns
        ]
    
    conn.close()
    return schema

@app.get("/statistics/survival")
def get_survival_stats():
    conn = get_db_connection()
    stats = {}
    
    # Survival by class
    stats["by_class"] = conn.execute("""
        SELECT c.class, 
               COUNT(*) as total,
               SUM(o.survived) as survived,
               ROUND(AVG(o.survived) * 100, 2) as survival_rate
        FROM Observation o
        JOIN Class c ON o.class_id = c.class_id
        GROUP BY c.class
        ORDER BY c.class
    """).fetchall()

    # Survival by sex
    stats["by_sex"] = conn.execute("""
        SELECT s.sex,
               COUNT(*) as total,
               SUM(o.survived) as survived,
               ROUND(AVG(o.survived) * 100, 2) as survival_rate
        FROM Observation o
        JOIN Sex s ON o.sex_id = s.sex_id
        GROUP BY s.sex
    """).fetchall()

    # Survival by age group
    stats["by_age_group"] = conn.execute("""
        SELECT 
            CASE 
                WHEN age < 18 THEN 'child'
                WHEN age < 35 THEN 'young_adult'
                WHEN age < 50 THEN 'adult'
                ELSE 'elderly'
            END as age_group,
            COUNT(*) as total,
            SUM(survived) as survived,
            ROUND(AVG(survived) * 100, 2) as survival_rate
        FROM Observation
        WHERE age IS NOT NULL
        GROUP BY age_group
        ORDER BY age_group
    """).fetchall()
    
    conn.close()
    return {k: [dict(row) for row in v] for k, v in stats.items()}

@app.get("/passengers/overview")
def get_passengers_overview():
    conn = get_db_connection()
    passengers = conn.execute("""
        SELECT 
            o.rowid as passenger_id,
            CASE 
                WHEN o.survived = 1 THEN 'Yes'
                ELSE 'No'
            END as survived,
            c.class,
            s.sex,
            o.age,
            et.embark_town,
            o.fare
        FROM Observation o
        JOIN Class c ON o.class_id = c.class_id
        JOIN Sex s ON o.sex_id = s.sex_id
        JOIN EmbarkTown et ON o.embark_town_id = et.embark_town_id
        ORDER BY o.rowid
    """).fetchall()
    
    conn.close()
    return [dict(row) for row in passengers]

@app.get("/passengers/details/{passenger_id}")
def get_passenger_details(passenger_id: int):
    conn = get_db_connection()
    passenger = conn.execute("""
        SELECT 
            o.*,
            s.sex,
            c.class,
            e.embarked,
            et.embark_town,
            w.who,
            d.deck,
            a.alive
        FROM Observation o
        LEFT JOIN Sex s ON o.sex_id = s.sex_id
        LEFT JOIN Class c ON o.class_id = c.class_id
        LEFT JOIN Embarked e ON o.embarked_id = e.embarked_id
        LEFT JOIN EmbarkTown et ON o.embark_town_id = et.embark_town_id
        LEFT JOIN Who w ON o.who_id = w.who_id
        LEFT JOIN Deck d ON o.deck_id = d.deck_id
        LEFT JOIN Alive a ON o.alive_id = a.alive_id
        WHERE o.rowid = ?
    """, (passenger_id,)).fetchone()
    
    if passenger is None:
        raise HTTPException(status_code=404, detail="Passenger not found")
    
    conn.close()
    return dict(passenger)

@app.get("/analysis/fare")
def get_fare_analysis():
    conn = get_db_connection()
    analysis = conn.execute("""
        SELECT 
            c.class,
            et.embark_town,
            ROUND(AVG(o.fare), 2) as avg_fare,
            ROUND(MIN(o.fare), 2) as min_fare,
            ROUND(MAX(o.fare), 2) as max_fare,
            COUNT(*) as passenger_count
        FROM Observation o
        JOIN Class c ON o.class_id = c.class_id
        JOIN EmbarkTown et ON o.embark_town_id = et.embark_town_id
        GROUP BY c.class, et.embark_town
        ORDER BY c.class, et.embark_town
    """).fetchall()
    
    conn.close()
    return [dict(row) for row in analysis]
