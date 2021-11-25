from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

ERROR = {
    "not found": "Sorry, we don't have a caffe at that location"
}



##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=["GET"])
def randomcafe():
    # Apparently this is the quickest way to get a random row from a database that may become large / Scalability
    # Firstly, get the total number of rows in the database
    row_count = Cafe.query.count()
    # Generate a random number for skipping some records
    random_offset = random.randint(0, row_count-1)
    # Return the first record after skipping random_offset rows
    random_cafe = Cafe.query.offset(random_offset).first()
    return jsonify(cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
    })

@app.route("/all")
def get_all():
    cafes = {}
    row_count = Cafe.query.count()
    for row in range(row_count):
        random_cafe = Cafe.query.offset(row).first()
        cafes[f"Cafe{row}"] ={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
        }
    all_cafes = {"cafes": cafes}
    return jsonify(cafes=all_cafes["cafes"])


@app.route("/search")
def search():
    loc = request.args.get('loc').capitalize()
    random_cafe = Cafe.query.filter_by(location=loc).first()
    try:
        cafe_to_return = {"cafe": {
            "id": random_cafe.id,
            "name": random_cafe.name,
            "map_url": random_cafe.map_url,
            "img_url": random_cafe.img_url,
            "location": random_cafe.location,
            "seats": random_cafe.seats,
            "has_toilet": random_cafe.has_toilet,
            "has_wifi": random_cafe.has_wifi,
            "has_sockets": random_cafe.has_sockets,
            "can_take_calls": random_cafe.can_take_calls,
            "coffee_price": random_cafe.coffee_price,
            }}

        return jsonify(cafe=cafe_to_return["cafe"])
    except:
        return jsonify(error= ERROR["not found"])

## HTTP GET - Read Record

## HTTP POST - Create Record
@app.route("/add")
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

## HTTP PUT/PATCH - Update Record

@app.route("/update-price/<cafe_id>")
def updateprice(cafe_id):
    cafe_to_update = Cafe.query.filter_by(id=cafe_id).first()
    if cafe_to_update:
        cafe_to_update.coffee_price = f"${str(float(request.args.get('price')))}"
        db.session.commit()
        return jsonify(response={"Success": "price was updated"}), 200
    else:
        return jsonify(response={"Error": "cafe not found"}), 404


## HTTP DELETE - Delete Record

@app.route("/report-closed/<cafe_id>")
def delete_cafe(cafe_id):
    if request.args.get('api_key') == "SecretAPIKey":
        book_to_delete = Cafe.query.get(cafe_id)
        if book_to_delete:
            db.session.delete(book_to_delete)
            db.session.commit()
            return jsonify(Success={"Cafe was deleted": f"{book_to_delete.name} was reported closed and deleted from db"})
        else:
            return jsonify(error={"Cafe not found": "Did you lose something my friend?"}), 404
    else:
        return jsonify(error={"Not allowed": "Api key is incorrect, get out!!!"}), 403

if __name__ == '__main__':
    app.run(debug=True)
