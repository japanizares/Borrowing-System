from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os, traceback
from datetime import datetime, timedelta
app = Flask(__name__)

# ── DATABASE ───────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    db_path = os.path.join(os.path.dirname(__file__), "pe_system.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

app.config["SECRET_KEY"]                     = os.environ.get("SECRET_KEY", "pe_borrowing_secret_2024")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"]             = 10 * 1024 * 1024

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "pe_admin_2024")

db     = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

IS_PG = "postgresql" in app.config["SQLALCHEMY_DATABASE_URI"]

def LIMIT(n): return f"LIMIT {n}"
def NOW_EXPR(): return "NOW()" if IS_PG else "CURRENT_TIMESTAMP"

# ── INIT TABLES ────────────────────────────────────────────────────────────
def init_db():
    ai = "AUTOINCREMENT" if not IS_PG else ""
    if IS_PG:
        pg_stmts = [
            """CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                student_id VARCHAR(50),
                year_level VARCHAR(20),
                department VARCHAR(200),
                role VARCHAR(20) DEFAULT 'student',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT NOW()
            )""",
            """CREATE TABLE IF NOT EXISTS equipment (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                description VARCHAR(500),
                total_quantity INTEGER NOT NULL DEFAULT 0,
                available_quantity INTEGER NOT NULL DEFAULT 0,
                condition VARCHAR(20) DEFAULT 'Good',
                image_url VARCHAR(500),
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT NOW()
            )""",
            """CREATE TABLE IF NOT EXISTS borrowings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                equipment_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                purpose VARCHAR(300),
                borrowed_at TIMESTAMP DEFAULT NOW(),
                expected_return_at TIMESTAMP NOT NULL,
                returned_at TIMESTAMP,
                status VARCHAR(20) DEFAULT 'borrowed',
                condition_on_return VARCHAR(20),
                notes VARCHAR(500),
                approved_by INTEGER,
                created_at TIMESTAMP DEFAULT NOW()
            )""",
            """CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                message VARCHAR(500) NOT NULL,
                type VARCHAR(30) DEFAULT 'info',
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            )""",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'student'",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active INTEGER DEFAULT 1",
            "ALTER TABLE equipment ADD COLUMN IF NOT EXISTS is_active INTEGER DEFAULT 1",
            "ALTER TABLE borrowings ADD COLUMN IF NOT EXISTS condition_on_return VARCHAR(20)",
            "ALTER TABLE borrowings ADD COLUMN IF NOT EXISTS notes VARCHAR(500)",
            "ALTER TABLE borrowings ADD COLUMN IF NOT EXISTS approved_by INTEGER",
        ]
        for s in pg_stmts:
            try: db.session.execute(db.text(s))
            except Exception as e: print(f"PG init: {e}")
    else:
        sqlite_stmts = [
            f"""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY {ai},
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                student_id VARCHAR(50),
                year_level VARCHAR(20),
                department VARCHAR(200),
                role VARCHAR(20) DEFAULT 'student',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            f"""CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY {ai},
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                description VARCHAR(500),
                total_quantity INTEGER NOT NULL DEFAULT 0,
                available_quantity INTEGER NOT NULL DEFAULT 0,
                condition VARCHAR(20) DEFAULT 'Good',
                image_url VARCHAR(500),
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            f"""CREATE TABLE IF NOT EXISTS borrowings (
                id INTEGER PRIMARY KEY {ai},
                user_id INTEGER NOT NULL,
                equipment_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                purpose VARCHAR(300),
                borrowed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expected_return_at TIMESTAMP NOT NULL,
                returned_at TIMESTAMP,
                status VARCHAR(20) DEFAULT 'borrowed',
                condition_on_return VARCHAR(20),
                notes VARCHAR(500),
                approved_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            f"""CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY {ai},
                user_id INTEGER NOT NULL,
                title VARCHAR(200) NOT NULL,
                message VARCHAR(500) NOT NULL,
                type VARCHAR(30) DEFAULT 'info',
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
        ]
        for s in sqlite_stmts:
            try: db.session.execute(db.text(s))
            except Exception as e: print(f"SQLite init: {e}")
    db.session.commit()
    print("DB tables ready")

    try:
        count = db.session.execute(db.text("SELECT COUNT(*) FROM users WHERE role='admin'")).scalar()
        if count == 0:
            hashed = bcrypt.generate_password_hash("pe_admin_2024").decode("utf-8")
            db.session.execute(db.text(
                "INSERT INTO users (name,email,password_hash,role,student_id) VALUES (:n,:e,:pw,'admin','ADMIN-001')"
            ), {"n": "PE Admin", "e": "admin@pe.adnu.edu.ph", "pw": hashed})
            db.session.commit()
            print("Default admin created: admin@pe.adnu.edu.ph / pe_admin_2024")
    except Exception as e:
        db.session.rollback(); print(f"Seed admin error: {e}")

    try:
        count = db.session.execute(db.text("SELECT COUNT(*) FROM equipment")).scalar()
        if count == 0:
            sample = [
                ("Basketball",         "Ball Sports",   "Official size basketball",          10, 10),
                ("Volleyball",         "Ball Sports",   "Standard volleyball",               8,  8),
                ("Badminton Racket",   "Racket Sports", "Aluminum frame badminton racket",   20, 20),
                ("Shuttlecock (tube)", "Racket Sports", "Tube of 12 shuttlecocks",           15, 15),
                ("Table Tennis Bat",   "Racket Sports", "Standard ping pong paddle",         16, 16),
                ("Football",           "Ball Sports",   "Standard size football",            6,  6),
                ("Jump Rope",          "Fitness",       "Individual jump rope",              25, 25),
                ("Frisbee",            "Outdoor",       "Standard flying disc",              12, 12),
                ("Volleyball Net",     "Equipment",     "Regulation volleyball net",         4,  4),
                ("Badminton Net",      "Equipment",     "Standard badminton net",            6,  6),
            ]
            for (name, cat, desc, total, avail) in sample:
                db.session.execute(db.text(
                    "INSERT INTO equipment (name,category,description,total_quantity,available_quantity) VALUES (:n,:c,:d,:t,:a)"
                ), {"n": name, "c": cat, "d": desc, "t": total, "a": avail})
            db.session.commit()
            print("Sample equipment seeded")
    except Exception as e:
        db.session.rollback(); print(f"Seed equipment error: {e}")

with app.app_context():
    init_db()

# ── HELPERS ────────────────────────────────────────────────────────────────
def notify(user_id, title, message, ntype="info"):
    try:
        db.session.execute(db.text(
            "INSERT INTO notifications (user_id,title,message,type,is_read) VALUES (:u,:t,:m,:ty,0)"
        ), {"u": user_id, "t": title, "m": message, "ty": ntype})
        db.session.commit()
    except Exception as e:
        print(f"Notify error: {e}"); db.session.rollback()

def notify_all_admins(title, message, ntype="warning"):
    try:
        admins = db.session.execute(db.text("SELECT id FROM users WHERE role='admin' AND is_active=1")).fetchall()
        for a in admins:
            db.session.execute(db.text(
                "INSERT INTO notifications (user_id,title,message,type,is_read) VALUES (:u,:t,:m,:ty,0)"
            ), {"u": a[0], "t": title, "m": message, "ty": ntype})
        db.session.commit()
    except Exception as e:
        print(f"Notify admins error: {e}"); db.session.rollback()

def check_overdue():
    try:
        now = datetime.now()
        rows = db.session.execute(db.text("""
            SELECT b.id, b.user_id, b.equipment_id, b.quantity, b.expected_return_at,
                   u.name, e.name as eq_name
            FROM borrowings b
            JOIN users u ON b.user_id = u.id
            JOIN equipment e ON b.equipment_id = e.id
            WHERE b.status = 'borrowed' AND b.expected_return_at < :now
        """), {"now": now}).fetchall()
        for r in rows:
            db.session.execute(db.text(
                "UPDATE borrowings SET status='overdue' WHERE id=:id"
            ), {"id": r[0]})
            notify_all_admins(
                "Overdue Equipment",
                f"{r[5]} has not returned {r[6]} (x{r[3]}) - due {r[4].strftime('%b %d, %Y') if r[4] else ''}",
                "warning"
            )
            notify(r[1], "Overdue Return",
                   f"Your borrowed {r[6]} was due on {r[4].strftime('%b %d, %Y') if r[4] else ''}. Please return immediately.",
                   "warning")
        db.session.commit()
    except Exception as e:
        print(f"Check overdue error: {e}"); db.session.rollback()

def fmt_borrowing(r, include_user=True, include_eq=True):
    d = {
        "id":                 r[0],
        "user_id":            r[1],
        "equipment_id":       r[2],
        "quantity":           r[3],
        "purpose":            r[4],
        "borrowed_at":        str(r[5]) if r[5] else None,
        "expected_return_at": str(r[6]) if r[6] else None,
        "returned_at":        str(r[7]) if r[7] else None,
        "status":             r[8],
        "condition_on_return":r[9],
        "notes":              r[10],
    }
    idx = 11
    if include_user:
        d["student_name"]  = r[idx];     d["student_id"]   = r[idx+1]
        d["department"]    = r[idx+2];   idx += 3
    if include_eq:
        d["equipment_name"]    = r[idx]; d["equipment_category"] = r[idx+1]; idx += 2
    return d

# ── ROOT ───────────────────────────────────────────────────────────────────
@app.route("/")
def home(): return "PE Borrowing System API is running"

# ── AUTH ───────────────────────────────────────────────────────────────────
@app.route("/api/register", methods=["POST"])
def register():
    data  = request.get_json() or {}
    name  = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    pw    = data.get("password") or ""
    sid   = (data.get("student_id") or "").strip()
    if not name or not email or not pw:
        return jsonify({"message": "Name, email and password are required"}), 400
    if len(pw) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400
    if db.session.execute(db.text("SELECT COUNT(*) FROM users WHERE email=:e"), {"e": email}).scalar() > 0:
        return jsonify({"message": "Email already registered"}), 400
    try:
        hashed = bcrypt.generate_password_hash(pw).decode("utf-8")
        db.session.execute(db.text(
            "INSERT INTO users (name,email,password_hash,student_id,year_level,department,role) VALUES (:n,:e,:pw,:sid,:yr,:dept,'student')"
        ), {"n": name, "e": email, "pw": hashed, "sid": sid,
            "yr": data.get("year_level",""), "dept": data.get("department","")})
        db.session.commit()
        return jsonify({"message": "Registered successfully! Please log in."}), 201
    except Exception as ex:
        db.session.rollback(); traceback.print_exc()
        return jsonify({"message": f"Server error: {str(ex)}"}), 500

@app.route("/api/login", methods=["POST"])
def login():
    data  = request.get_json() or {}
    email = (data.get("email") or "").strip()
    pw    = data.get("password") or ""
    row   = db.session.execute(db.text(
        "SELECT id,name,email,password_hash,student_id,year_level,department,role,is_active FROM users WHERE email=:e"
    ), {"e": email}).fetchone()
    if not row: return jsonify({"message": "No account found with that email"}), 404
    if not bcrypt.check_password_hash(str(row[3]), pw):
        return jsonify({"message": "Incorrect password"}), 401
    if not int(row[8] or 1):
        return jsonify({"message": "Your account has been deactivated. Contact admin."}), 403
    return jsonify({
        "user_id": row[0], "name": row[1], "email": row[2],
        "student_id": row[4], "year_level": row[5], "department": row[6], "role": row[7],
    })

@app.route("/api/profile/<int:uid>", methods=["GET"])
def get_profile(uid):
    row = db.session.execute(db.text(
        "SELECT id,name,email,student_id,year_level,department,role FROM users WHERE id=:id"
    ), {"id": uid}).fetchone()
    if not row: return jsonify({"message": "User not found"}), 404
    return jsonify({"user_id":row[0],"name":row[1],"email":row[2],"student_id":row[3],"year_level":row[4],"department":row[5],"role":row[6]})

@app.route("/api/profile/<int:uid>", methods=["PUT"])
def update_profile(uid):
    data = request.get_json() or {}
    try:
        db.session.execute(db.text(
            "UPDATE users SET name=:n,student_id=:sid,year_level=:yr,department=:dept WHERE id=:id"
        ), {"n":data.get("name"),"sid":data.get("student_id"),"yr":data.get("year_level"),"dept":data.get("department"),"id":uid})
        db.session.commit()
        return jsonify({"message": "Profile updated"})
    except Exception as e:
        db.session.rollback(); return jsonify({"message": "Server error"}), 500

# ── EQUIPMENT ──────────────────────────────────────────────────────────────
@app.route("/api/equipment", methods=["GET"])
def get_equipment():
    check_overdue()
    search   = (request.args.get("search") or "").strip()
    category = (request.args.get("category") or "").strip()
    avail    = request.args.get("available_only", "false").lower() == "true"
    try:
        conds  = ["is_active=1"]
        params = {}
        if search:
            conds.append("(LOWER(name) LIKE :search OR LOWER(category) LIKE :search OR LOWER(description) LIKE :search)")
            params["search"] = f"%{search.lower()}%"
        if category:
            conds.append("category=:category"); params["category"] = category
        if avail:
            conds.append("available_quantity > 0")
        sql = "SELECT id,name,category,description,total_quantity,available_quantity,condition,image_url FROM equipment WHERE " + " AND ".join(conds) + " ORDER BY category,name"
        rows = db.session.execute(db.text(sql), params).fetchall()
        return jsonify([{
            "id":r[0],"name":r[1],"category":r[2],"description":r[3],
            "total_quantity":r[4],"available_quantity":r[5],"condition":r[6],"image_url":r[7],
            "is_available": r[5] > 0
        } for r in rows])
    except Exception as e:
        traceback.print_exc(); return jsonify({"message":"Server error"}), 500
@app.route("/api/categories", methods=["GET"])
def get_categories():
    rows = db.session.execute(db.text("""
        SELECT DISTINCT category
        FROM equipment
        WHERE is_active = 1
        ORDER BY category
    """)).fetchall()

    return jsonify([r[0] for r in rows])

@app.route("/api/equipment/<int:eid>", methods=["GET"])
def get_equipment_detail(eid):
    row = db.session.execute(db.text(
        "SELECT id,name,category,description,total_quantity,available_quantity,condition,image_url FROM equipment WHERE id=:id"
    ), {"id":eid}).fetchone()
    if not row: return jsonify({"message":"Not found"}), 404
    return jsonify({"id":row[0],"name":row[1],"category":row[2],"description":row[3],"total_quantity":row[4],"available_quantity":row[5],"condition":row[6],"image_url":row[7]})

@app.route("/api/equipment", methods=["POST"])
def add_equipment():
    data = request.get_json() or {}
    name  = (data.get("name") or "").strip()
    cat   = (data.get("category") or "").strip()
    qty   = int(data.get("total_quantity", 0))
    if not name or not cat: return jsonify({"message":"Name and category required"}), 400
    if qty < 0: return jsonify({"message":"Quantity cannot be negative"}), 400
    try:
        db.session.execute(db.text(
            "INSERT INTO equipment (name,category,description,total_quantity,available_quantity,condition) VALUES (:n,:c,:d,:t,:a,:cond)"
        ), {"n":name,"c":cat,"d":data.get("description",""),"t":qty,"a":qty,"cond":data.get("condition","Good")})
        db.session.commit()
        return jsonify({"message":"Equipment added"}), 201
    except Exception as e:
        db.session.rollback(); return jsonify({"message":"Server error"}), 500

@app.route("/api/equipment/<int:eid>", methods=["PUT"])
def update_equipment(eid):
    data = request.get_json() or {}
    try:
        row = db.session.execute(db.text("SELECT total_quantity,available_quantity FROM equipment WHERE id=:id"),{"id":eid}).fetchone()
        if not row: return jsonify({"message":"Not found"}), 404
        new_total = int(data.get("total_quantity", row[0]))
        diff = new_total - row[0]
        new_avail = max(0, row[1] + diff)
        db.session.execute(db.text(
            "UPDATE equipment SET name=:n,category=:c,description=:d,total_quantity=:t,available_quantity=:a,condition=:cond WHERE id=:id"
        ), {"n":data.get("name"),"c":data.get("category"),"d":data.get("description",""),"t":new_total,"a":new_avail,"cond":data.get("condition","Good"),"id":eid})
        db.session.commit()
        return jsonify({"message":"Equipment updated"})
    except Exception as e:
        db.session.rollback(); traceback.print_exc(); return jsonify({"message":"Server error"}), 500

@app.route("/api/equipment/<int:eid>", methods=["DELETE"])
def delete_equipment(eid):
    try:
        db.session.execute(db.text("UPDATE equipment SET is_active=0 WHERE id=:id"),{"id":eid})
        db.session.commit()
        return jsonify({"message":"Equipment removed"})
    except Exception as e:
        db.session.rollback(); return jsonify({"message":"Server error"}), 500

# ── BORROWINGS ─────────────────────────────────────────────────────────────
@app.route("/api/borrow", methods=["POST"])
def borrow():
    check_overdue()
    data       = request.get_json() or {}
    user_id    = data.get("user_id")
    eq_id      = data.get("equipment_id")
    qty        = int(data.get("quantity", 1))
    purpose    = (data.get("purpose") or "").strip()
    return_date= data.get("expected_return_at")

    if not user_id or not eq_id or not return_date:
        return jsonify({"message":"user_id, equipment_id, and expected_return_at are required"}), 400
    if qty < 1:
        return jsonify({"message":"Quantity must be at least 1"}), 400

    try:
        expected_dt = datetime.fromisoformat(return_date.replace("Z",""))
        if expected_dt <= datetime.now():
            return jsonify({"message":"Return date must be in the future"}), 400
    except:
        return jsonify({"message":"Invalid return date format"}), 400

    try:
        eq = db.session.execute(db.text(
            "SELECT id,name,available_quantity FROM equipment WHERE id=:id AND is_active=1"
        ),{"id":eq_id}).fetchone()
        if not eq: return jsonify({"message":"Equipment not found"}), 404
        if eq[2] < qty:
            return jsonify({"message":f"Only {eq[2]} unit(s) available"}), 400

        existing = db.session.execute(db.text(
            "SELECT COUNT(*) FROM borrowings WHERE user_id=:u AND equipment_id=:e AND status IN ('borrowed','overdue')"
        ),{"u":user_id,"e":eq_id}).scalar()
        if existing > 0:
            return jsonify({"message":"You already have this equipment. Return it first before borrowing again."}), 400

        db.session.execute(db.text(
            "INSERT INTO borrowings (user_id,equipment_id,quantity,purpose,expected_return_at,status) VALUES (:u,:e,:q,:p,:r,'borrowed')"
        ),{"u":user_id,"e":eq_id,"q":qty,"p":purpose,"r":expected_dt})

        db.session.execute(db.text(
            "UPDATE equipment SET available_quantity=available_quantity-:q WHERE id=:id"
        ),{"q":qty,"id":eq_id})

        db.session.commit()

        notify(user_id, "Borrow Request Confirmed",
               f"You have borrowed {qty}x {eq[1]}. Please return by {expected_dt.strftime('%b %d, %Y %I:%M %p')}.",
               "success")
        user_row = db.session.execute(db.text("SELECT name,student_id FROM users WHERE id=:id"),{"id":user_id}).fetchone()
        notify_all_admins("New Borrow Request",
               f"{user_row[0]} ({user_row[1]}) borrowed {qty}x {eq[1]}. Return: {expected_dt.strftime('%b %d, %Y')}",
               "info")

        return jsonify({"message":"Equipment borrowed successfully!"}), 201
    except Exception as e:
        db.session.rollback(); traceback.print_exc()
        return jsonify({"message":f"Server error: {str(e)}"}), 500

@app.route("/api/return/<int:borrow_id>", methods=["POST"])
def return_equipment(borrow_id):
    data      = request.get_json() or {}
    condition = data.get("condition_on_return", "Good")
    notes     = data.get("notes", "")
    admin_id  = data.get("admin_id")
    try:
        row = db.session.execute(db.text(
            "SELECT user_id,equipment_id,quantity,status,expected_return_at FROM borrowings WHERE id=:id"
        ),{"id":borrow_id}).fetchone()
        if not row: return jsonify({"message":"Record not found"}), 404
        if row[3] == "returned": return jsonify({"message":"Already returned"}), 400

        now = datetime.now()
        db.session.execute(db.text(
            "UPDATE borrowings SET status='returned',returned_at=:now,condition_on_return=:cond,notes=:notes,approved_by=:adm WHERE id=:id"
        ),{"now":now,"cond":condition,"notes":notes,"adm":admin_id,"id":borrow_id})

        db.session.execute(db.text(
            "UPDATE equipment SET available_quantity=available_quantity+:q WHERE id=:id"
        ),{"q":row[2],"id":row[1]})

        db.session.commit()

        eq_name = db.session.execute(db.text("SELECT name FROM equipment WHERE id=:id"),{"id":row[1]}).scalar()
        notify(row[0], "Equipment Returned",
               f"Your return of {row[2]}x {eq_name} has been recorded. Thank you!",
               "success")

        return jsonify({"message":"Equipment returned successfully"})
    except Exception as e:
        db.session.rollback(); traceback.print_exc()
        return jsonify({"message":f"Server error: {str(e)}"}), 500

@app.route("/api/borrowings", methods=["GET"])
def get_borrowings():
    check_overdue()
    user_id  = request.args.get("user_id")
    status   = request.args.get("status")
    search   = (request.args.get("search") or "").strip()
    limit    = int(request.args.get("limit", 100))
    try:
        conds  = ["1=1"]
        params = {}
        if user_id:
            conds.append("b.user_id=:uid"); params["uid"] = int(user_id)
        if status and status != "all":
            conds.append("b.status=:status"); params["status"] = status
        if search:
            conds.append("(LOWER(u.name) LIKE :s OR LOWER(e.name) LIKE :s OR LOWER(u.student_id) LIKE :s)")
            params["s"] = f"%{search.lower()}%"
        sql = f"""
            SELECT b.id,b.user_id,b.equipment_id,b.quantity,b.purpose,
                   b.borrowed_at,b.expected_return_at,b.returned_at,b.status,
                   b.condition_on_return,b.notes,
                   u.name,u.student_id,u.department,
                   e.name,e.category
            FROM borrowings b
            JOIN users u ON b.user_id=u.id
            JOIN equipment e ON b.equipment_id=e.id
            WHERE {' AND '.join(conds)}
            ORDER BY b.borrowed_at DESC
            LIMIT {limit}
        """
        rows = db.session.execute(db.text(sql), params).fetchall()
        return jsonify([fmt_borrowing(r) for r in rows])
    except Exception as e:
        traceback.print_exc(); return jsonify({"message":"Server error"}), 500

@app.route("/api/borrowings/<int:bid>", methods=["GET"])
def get_borrowing_detail(bid):
    row = db.session.execute(db.text("""
        SELECT b.id,b.user_id,b.equipment_id,b.quantity,b.purpose,
               b.borrowed_at,b.expected_return_at,b.returned_at,b.status,
               b.condition_on_return,b.notes,
               u.name,u.student_id,u.department,
               e.name,e.category
        FROM borrowings b
        JOIN users u ON b.user_id=u.id
        JOIN equipment e ON b.equipment_id=e.id
        WHERE b.id=:id
    """),{"id":bid}).fetchone()
    if not row: return jsonify({"message":"Not found"}), 404
    return jsonify(fmt_borrowing(row))

# ── NOTIFICATIONS ──────────────────────────────────────────────────────────
@app.route("/api/notifications/<int:uid>", methods=["GET"])
def get_notifications(uid):
    rows = db.session.execute(db.text(
        "SELECT id,title,message,type,is_read,created_at FROM notifications WHERE user_id=:u ORDER BY created_at DESC LIMIT 50"
    ),{"u":uid}).fetchall()
    return jsonify([{"id":r[0],"title":r[1],"message":r[2],"type":r[3],"is_read":r[4],"created_at":str(r[5])} for r in rows])

@app.route("/api/notifications/<int:uid>/read", methods=["POST"])
def mark_notifications_read(uid):
    try:
        db.session.execute(db.text("UPDATE notifications SET is_read=1 WHERE user_id=:u"),{"u":uid})
        db.session.commit()
        return jsonify({"message":"Marked as read"})
    except Exception as e:
        db.session.rollback(); return jsonify({"message":"Server error"}), 500

@app.route("/api/notifications/unread-count/<int:uid>", methods=["GET"])
def notif_unread_count(uid):
    count = db.session.execute(db.text(
        "SELECT COUNT(*) FROM notifications WHERE user_id=:u AND is_read=0"
    ),{"u":uid}).scalar()
    return jsonify({"count": count})

# ── DASHBOARD STATS ────────────────────────────────────────────────────────
@app.route("/api/stats", methods=["GET"])
def get_stats():
    check_overdue()
    try:
        total_eq      = db.session.execute(db.text("SELECT COUNT(*) FROM equipment WHERE is_active=1")).scalar()
        total_users   = db.session.execute(db.text("SELECT COUNT(*) FROM users WHERE role='student'")).scalar()
        active_borrows= db.session.execute(db.text("SELECT COUNT(*) FROM borrowings WHERE status='borrowed'")).scalar()
        overdue       = db.session.execute(db.text("SELECT COUNT(*) FROM borrowings WHERE status='overdue'")).scalar()
        if IS_PG:
            returned_today = db.session.execute(db.text(
                "SELECT COUNT(*) FROM borrowings WHERE status='returned' AND returned_at::date=CURRENT_DATE"
            )).scalar()
        else:
            returned_today = db.session.execute(db.text(
                "SELECT COUNT(*) FROM borrowings WHERE status='returned' AND DATE(returned_at)=DATE('now')"
            )).scalar()
        total_borrows = db.session.execute(db.text("SELECT COUNT(*) FROM borrowings")).scalar()

        top_eq = db.session.execute(db.text("""
            SELECT e.name, COUNT(*) as cnt
            FROM borrowings b JOIN equipment e ON b.equipment_id=e.id
            GROUP BY e.name ORDER BY cnt DESC LIMIT 5
        """)).fetchall()

        recent = db.session.execute(db.text("""
            SELECT b.id, u.name, e.name, b.quantity, b.status, b.borrowed_at
            FROM borrowings b JOIN users u ON b.user_id=u.id JOIN equipment e ON b.equipment_id=e.id
            ORDER BY b.borrowed_at DESC LIMIT 8
        """)).fetchall()

        return jsonify({
            "total_equipment":   total_eq,
            "total_students":    total_users,
            "active_borrowings": active_borrows,
            "overdue":           overdue,
            "returned_today":    returned_today,
            "total_borrowings":  total_borrows,
            "top_equipment":     [{"name":r[0],"count":r[1]} for r in top_eq],
            "recent_activity":   [{"id":r[0],"student":r[1],"equipment":r[2],"qty":r[3],"status":r[4],"date":str(r[5])} for r in recent],
        })
    except Exception as e:
        traceback.print_exc(); return jsonify({"message":"Server error"}), 500

# ── ADMIN: USERS ───────────────────────────────────────────────────────────
@app.route("/api/admin/users", methods=["GET"])
def admin_get_users():
    rows = db.session.execute(db.text(
        "SELECT id,name,email,student_id,year_level,department,role,is_active,created_at FROM users ORDER BY id DESC"
    )).fetchall()
    return jsonify([{"id":r[0],"name":r[1],"email":r[2],"student_id":r[3],"year_level":r[4],"department":r[5],"role":r[6],"is_active":r[7],"created_at":str(r[8])} for r in rows])

@app.route("/api/admin/users/<int:uid>/toggle", methods=["POST"])
def toggle_user(uid):
    try:
        current = db.session.execute(db.text("SELECT is_active FROM users WHERE id=:id"),{"id":uid}).scalar()
        new_val = 0 if current else 1
        db.session.execute(db.text("UPDATE users SET is_active=:v WHERE id=:id"),{"v":new_val,"id":uid})
        db.session.commit()
        return jsonify({"message": "Activated" if new_val else "Deactivated", "is_active": new_val})
    except Exception as e:
        db.session.rollback(); return jsonify({"message":"Server error"}), 500

@app.route("/api/admin/users/<int:uid>", methods=["DELETE"])
def delete_user(uid):
    try:
        db.session.execute(db.text("DELETE FROM notifications WHERE user_id=:id"),{"id":uid})
        db.session.execute(db.text("DELETE FROM borrowings WHERE user_id=:id"),{"id":uid})
        db.session.execute(db.text("DELETE FROM users WHERE id=:id"),{"id":uid})
        db.session.commit()
        return jsonify({"message":"User deleted"})
    except Exception as e:
        db.session.rollback(); return jsonify({"message":"Server error"}), 500

# ── REPORTS ────────────────────────────────────────────────────────────────
@app.route("/api/reports/borrowings", methods=["GET"])
def report_borrowings():
    date_from = request.args.get("from")
    date_to   = request.args.get("to")
    status    = request.args.get("status","all")
    try:
        conds  = ["1=1"]
        params = {}
        if date_from:
            conds.append("b.borrowed_at >= :dfrom"); params["dfrom"] = date_from
        if date_to:
            conds.append("b.borrowed_at <= :dto"); params["dto"] = date_to
        if status != "all":
            conds.append("b.status=:status"); params["status"] = status
        sql = f"""
            SELECT b.id,b.user_id,b.equipment_id,b.quantity,b.purpose,
                   b.borrowed_at,b.expected_return_at,b.returned_at,b.status,
                   b.condition_on_return,b.notes,
                   u.name,u.student_id,u.department,
                   e.name,e.category
            FROM borrowings b
            JOIN users u ON b.user_id=u.id
            JOIN equipment e ON b.equipment_id=e.id
            WHERE {' AND '.join(conds)}
            ORDER BY b.borrowed_at DESC
        """
        rows = db.session.execute(db.text(sql), params).fetchall()
        return jsonify([fmt_borrowing(r) for r in rows])
    except Exception as e:
        traceback.print_exc(); return jsonify({"message":"Server error"}), 500

@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json() or {}
    if data.get("password") == ADMIN_PASSWORD:
        return jsonify({"success": True})
    return jsonify({"message": "Wrong admin password"}), 401

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG","0")=="1")