from flask import Flask, render_template, request, url_for, redirect, session, jsonify, send_file
from flask_session import Session

import os
import json

import config
from scraper import Scraper, check_format

from concurrent.futures import ThreadPoolExecutor


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def response(msg: str, state: int):
    """return json response with msg"""
    if state == 0:
        return jsonify({
            'state': 'failure',
            'msg': msg
        })

    elif state == 1:
        return jsonify({
            'state': 'success',
            'msg': msg
        })


def reset():
    # with open(config.INVALID_PRODUCT_JSON_FILE_PATH, 'w') as j:
    #     j.write()
    with open(config.OUTPUT_FILE_PATH, 'w') as c:
        c.write("")


@app.route("/")
def index():
    """handle / route"""
    if not session.get("logged_in"):
        return redirect("/login")
    reset()
    return render_template("upload.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """handle /login route"""
    # check if already logged in
    if session.get("logged_in") is True:
        print(session.get("logged_in"))
        return redirect("/")

    # check the request method
    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username and password:

            if username == os.getenv("LOGIN_USERNAME") and password == os.getenv("LOGIN_PASSWORD"):
                session["logged_in"] = True
                return redirect("/")

            else:
                return render_template("login.html", incorrect=True)

        else:
            return render_template("login.html", incorrect=True)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """handle logout process"""
    session["logged_in"] = None
    return redirect("/login")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """handle /upload route"""
    # check if logged in
    # if not session.get("logged_in"):
    #     # redirect to login
    #     return redirect("/login")
    if request.method == "GET":
        # render upload page if request method is get
        reset()
        return render_template("upload.html")

    elif request.method == "POST":
        # get uploaded file
        uploaded_file = request.files['file']
        # get its content type
        mimetype = uploaded_file.content_type
        # check if it is "xlsx"
        if mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            # save it on the server
            uploaded_file.save(config.INPUT_EXCEL_SHEET_PATH)
            return response("Successfully uploaded inventory sheet", 1)
        else:
            return response("Wrong file format, expected: xlsx", 0), 400


def check_if_csv_is_ready():
    """checK if csv is ready"""
    if os.path.getsize(config.OUTPUT_FILE_PATH) == 0:
        return False
    return True


@app.route("/csv")
def download_file():
    """download CSV file"""
    # check if logged in
    # if not session.get("logged_in"):
    #     # redirect to login
    #     return redirect("/login")
    if check_if_csv_is_ready():
        if request.args.get("check"):
            return ""
        return send_file(config.OUTPUT_FILE_PATH, as_attachment=True)
    else:
        return response("File is not ready yet.", 0), 400


@app.route("/checkSheetFormat")
def checkSheetFormat():

    missings = check_format()
    if len(missings["Sheet"]) != 0:
        return response("Missing Sheet: " + ", ".join(sheet for sheet in missings["Sheet"]), 0), 400

    missing_column_names = "Missing column names\n"
    missing = False

    if len(missings["Men"]) != 0:
        missing_column_names += "Men: " + ", ".join(column_name for column_name in missings["Men"]) + "\n"
        missing = True

    if len(missings["Women"]) != 0:
        missing_column_names += "Men: " + ", ".join(column_name for column_name in missings["Men"]) + "\n"
        missing = True

    if len(missings["Youth"]) != 0:
        missing_column_names += "Men: " + ", ".join(column_name for column_name in missings["Men"]) + "\n"
        missing = True

    if missing:
        return response(missing_column_names, 0), 400

    return response("Valid", 1)


@app.route("/scrap")
def scrap():
    """handle / route"""
    # check if logged in
    # if not session.get("logged_in"):
    #     # redirect to login
    #     return redirect("/login")

    s = Scraper()

    try:
        s.scrap_sheet()
    except UnicodeDecodeError:
        s.scrap_sheet()

    # invalid_products = s.get_invalid_products()
    # if len(invalid_products) != 0:
    #     with open(config.INVALID_PRODUCT_JSON_FILE_PATH, 'w') as j:
    #         j.write(json.dumps(invalid_products))

    return response("Done scraping", 1)


if __name__ == "__main__":
    app.run()
