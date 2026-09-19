import os
import psycopg

from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)
from functools import wraps
from werkzeug.security import check_password_hash
from psycopg.rows import dict_row

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
def get_db():
    return psycopg.connect(
        os.environ["DATABASE_URL"],
        row_factory=dict_row
    )

@app.get("/")
def home():
    with get_db() as conn:
        with conn.cursor() as cur:

            # 1. Get all projects
            cur.execute("""
                SELECT
                    id,
                    title,
                    year,
                    venue,
                    
                    github_url,
                    paper_url,
                    project_url,
                    video_url
                FROM projects
                ORDER BY year DESC;
            """)

            projects = cur.fetchall()


            # 2. Get authors for every project
            cur.execute("""
                SELECT
                    pa.project_id,
                    a.id,
                    a.name,
                    a.website_url,
                    pa.author_order,
                    pa.co_first
                FROM project_authors pa
                JOIN authors a
                    ON pa.author_id = a.id
                ORDER BY
                    pa.project_id,
                    pa.author_order;
            """)

            author_rows = cur.fetchall()


    # 3. Give every project an empty authors list
    project_map = {}

    for project in projects:
        project["authors"] = []
        project_map[project["id"]] = project


    # 4. Put each author under the correct project
    for author in author_rows:
        project = project_map.get(author["project_id"])

        if project:
            project["authors"].append({
                "id": author["id"],
                "name": author["name"],
                "website_url": author["website_url"],
                "co_first": author["co_first"]
            })


    return render_template(
        "index.html",
        projects=projects
    )

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped_view

@app.get("/admin")
@login_required
def admin():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    title,
                    year,
                    venue
                FROM projects
                ORDER BY year DESC;
            """)

            projects = cur.fetchall()

    return render_template(
        "admin.html",
        projects=projects
    )

@app.post("/admin/projects")
@login_required
def create_project():
    data = request.form

    year = data.get("year")
    year = int(year) if year else None

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO projects (
                    title,
                    year,
                    venue,
                    github_url,
                    paper_url,
                    project_url,
                    video_url
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s
                );
            """, (
                data["title"],
                year,
                data.get("venue") or None,
                data.get("github_url") or None,
                data.get("paper_url") or None,
                data.get("project_url") or None,
                data.get("video_url") or None
            ))

        conn.commit()

    return redirect(url_for("admin"))

@app.post("/admin/projects/<int:project_id>/delete")
@login_required
def delete_project(project_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM projects
                WHERE id = %s;
            """, (project_id,))

        conn.commit()

    return redirect(url_for("admin"))

@app.get("/admin/projects/<int:project_id>/edit")
@login_required
def edit_project(project_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    id,
                    title,
                    year,
                    venue,
                    
                    github_url,
                    paper_url,
                    project_url,
                    video_url
                FROM projects
                WHERE id = %s;
            """, (project_id,))

            project = cur.fetchone()

    return render_template(
        "edit_project.html",
        project=project
    )

@app.post("/admin/projects/<int:project_id>/edit")
@login_required
def update_project(project_id):
    data = request.form

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE projects
                SET
                    title = %s,
                    year = %s,
                    venue = %s,
                    github_url = %s,
                    paper_url = %s,
                    project_url = %s,
                    video_url = %s
                WHERE id = %s;
            """, (
                data["title"],
                data.get("year") or None,
                data.get("venue") or None,
                data.get("github_url") or None,
                data.get("paper_url") or None,
                data.get("project_url") or None,
                data.get("video_url") or None,
                project_id
            ))

        conn.commit()

    return redirect(url_for("admin"))



@app.route("/admin/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        id,
                        username,
                        password_hash
                    FROM users
                    WHERE username = %s;
                """, (username,))   

                user = cur.fetchone()

        if user is None:
            error = "Invalid username or password."

        elif not check_password_hash(
            user["password_hash"],
            password
        ):
            error = "Invalid username or password."

        else:
            session.clear()
            session["user_id"] = user["id"]

            return redirect(url_for("admin"))

    return render_template(
        "login.html",
        error=error
    )

@app.post("/admin/logout")
@login_required
def logout():
    session.clear()

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, port=8000)